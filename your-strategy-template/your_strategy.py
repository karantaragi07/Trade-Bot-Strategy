#!/usr/bin/env python3
"""High-Conviction Ultra-Profit Strategy for 90%+ Returns with 90%+ Win Rate.

This strategy focuses on maximizing profits while maintaining high win rate:
1. High-Conviction Signal Generation
2. Aggressive Position Sizing
3. Optimal Risk/Reward Ratio
4. Minimal Trade Count
5. Advanced Profit Maximization
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from statistics import pstdev, mean
import logging
import math
from typing import Any, Dict, Optional, List, Tuple

# Import base infrastructure from base-bot-template
import sys
import os

# Handle both local development and Docker container paths
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if not os.path.exists(base_path):
    # In Docker container, base template is at /app/base/
    base_path = '/app/base'

sys.path.insert(0, base_path)

from strategy_interface import BaseStrategy, Signal, register_strategy
from exchange_interface import MarketSnapshot


# ----------------------------- Custom strategy helpers -----------------------------

def _utc_iso(dt: datetime) -> str:
    """Return ISO timestamp with UTC tzinfo (seconds precision)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat(timespec="seconds")


def _as_bool(val, default: bool = False) -> bool:
    """Parse truthy strings/values to bool."""
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in ("1", "true", "yes", "on")


# --------------------------------- High-Conviction Ultra-Profit Strategy --------------------------------------

class HighConvictionUltraProfitStrategy(BaseStrategy):
    """High-Conviction Ultra-Profit Strategy for 90%+ Returns with 90%+ Win Rate.

    Core Strategy Components:
    1. High-Conviction Signal Generation
    2. Aggressive Position Sizing
    3. Optimal Risk/Reward Ratio
    4. Minimal Trade Count
    5. Advanced Profit Maximization
    """

    def __init__(self, config: Dict[str, Any], exchange):
        super().__init__(config=config, exchange=exchange)
        
        # Strategy parameters
        # High-Conviction Signal Generation
        self.conviction_threshold = float(config.get("conviction_threshold", 0.9))
        self.rsi_period = int(config.get("rsi_period", 14))
        self.rsi_overbought = float(config.get("rsi_overbought", 80))
        self.rsi_oversold = float(config.get("rsi_oversold", 20))
        self.bb_period = int(config.get("bb_period", 20))
        self.bb_std = float(config.get("bb_std", 2.0))
        self.macd_fast = int(config.get("macd_fast", 12))
        self.macd_slow = int(config.get("macd_slow", 26))
        self.macd_signal = int(config.get("macd_signal", 9))
        
        # Aggressive Position Sizing
        self.base_position_pct = float(config.get("base_position_pct", 0.15))   # 15% of portfolio per trade
        self.max_position_pct = float(config.get("max_position_pct", 0.4))     # Max 40% of portfolio
        self.conviction_position_multiplier = float(config.get("conviction_position_multiplier", 2.0))
        
        # Optimal Risk/Reward
        self.stop_loss_pct = float(config.get("stop_loss_pct", 0.03))          # 3% stop loss
        self.take_profit_pct = float(config.get("take_profit_pct", 0.15))      # 15% take profit
        self.trailing_stop_pct = float(config.get("trailing_stop_pct", 0.05))  # 5% trailing stop
        
        # Risk Management
        self.max_drawdown_pct = float(config.get("max_drawdown_pct", 0.2))     # 20% max drawdown
        self.consecutive_loss_limit = int(config.get("consecutive_loss_limit", 2))
        
        # Trade Management
        self.max_trades = int(config.get("max_trades", 30))
        self.min_time_between_trades = int(config.get("min_time_between_trades", 6))  # Hours
        
        # Internal state
        self._last_signal: Optional[str] = None
        self._entry_price: Optional[float] = None
        self._entry_time: Optional[datetime] = None
        self._trailing_high: Optional[float] = None
        self._trailing_low: Optional[float] = None
        self._consecutive_losses = 0
        self._peak_portfolio_value = 0.0
        self._local_logs_enabled = _as_bool(
            config.get("strategy_local_logs", os.getenv("STRATEGY_LOCAL_LOGS", "true")), True
        )
        self._logger = logging.getLogger("strategy.high_conviction")
        
        # Advanced components state
        self._price_history: List[float] = []
        self._win_loss_history: List[bool] = []
        self._trade_count = 0
        self._last_trade_time: Optional[datetime] = None
        self._recent_performance_score = 1.0

    # --------------------------- local logging utils ---------------------------

    def _log_local(self, kind: str, msg: str) -> None:
        """Local, strategy-only logger (no-throw)."""
        if not self._local_logs_enabled:
            return
        try:
            self._logger.info(f"[HIGH_CONVICTION/{kind}] {msg}")
        except Exception:
            pass  # never let logging crash strategy

    # --------------------------- Technical indicators --------------------------

    def _calculate_sma(self, prices: list, window: int) -> Optional[float]:
        """Calculate Simple Moving Average."""
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window

    def _calculate_rsi(self, prices: list, period: int) -> Optional[float]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None
            
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas[-period:]]
        losses = [-delta if delta < 0 else 0 for delta in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_bollinger_bands(self, prices: list, period: int, std_dev: float) -> Optional[Tuple[float, float, float]]:
        """Calculate Bollinger Bands (middle, upper, lower)."""
        if len(prices) < period:
            return None
            
        middle_band = self._calculate_sma(prices, period)
        if middle_band is None:
            return None
            
        variance = sum((price - middle_band) ** 2 for price in prices[-period:]) / period
        std_deviation = math.sqrt(variance)
        
        upper_band = middle_band + (std_dev * std_deviation)
        lower_band = middle_band - (std_dev * std_deviation)
        
        return (middle_band, upper_band, lower_band)

    def _calculate_macd(self, prices: list, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Optional[Tuple[float, float, float]]:
        """Calculate MACD (MACD line, Signal line, Histogram)."""
        if len(prices) < slow_period + signal_period:
            return None
            
        # Calculate EMAs
        def _calculate_ema(data, period):
            if len(data) < period:
                return None
            k = 2 / (period + 1)
            ema = data[-period]
            for price in data[-period+1:]:
                ema = price * k + ema * (1 - k)
            return ema
            
        fast_ema = _calculate_ema(prices, fast_period)
        slow_ema = _calculate_ema(prices, slow_period)
        
        if fast_ema is None or slow_ema is None:
            return None
            
        macd_line = fast_ema - slow_ema
        signal_line = _calculate_ema([fast_ema - slow_ema for _ in range(signal_period)], signal_period)
        
        if signal_line is None:
            return None
            
        histogram = macd_line - signal_line
        return (macd_line, signal_line, histogram)

    def _calculate_volatility(self, prices: list, window: int) -> Optional[float]:
        """Calculate price volatility."""
        if len(prices) < window:
            return None
            
        window_prices = prices[-window:]
        returns = []
        for i in range(1, len(window_prices)):
            if window_prices[i-1] > 0:
                returns.append((window_prices[i] - window_prices[i-1]) / window_prices[i-1])
                
        if len(returns) < 2:
            return 0
            
        return pstdev(returns)

    # --------------------------- Advanced Strategy Components --------------------------

    def _high_conviction_signal(self, market: MarketSnapshot) -> Tuple[float, str]:
        """Generate high-conviction signal with multiple confirmations."""
        if len(market.prices) < max(self.rsi_period, self.bb_period, self.macd_slow):
            return (0.0, "insufficient_data")
            
        current_price = market.current_price
        conviction_score = 0.0
        reasons = []
        
        # 1. RSI Extreme Confirmation
        rsi = self._calculate_rsi(market.prices, self.rsi_period)
        if rsi is not None:
            if rsi < self.rsi_oversold:
                # Oversold condition - potential buy signal
                rsi_score = (self.rsi_oversold - rsi) / self.rsi_oversold
                conviction_score += rsi_score * 0.4
                reasons.append(f"rsi_oversold:{rsi:.2f}")
            elif rsi > self.rsi_overbought:
                # Overbought condition - potential sell signal
                rsi_score = (rsi - self.rsi_overbought) / (100 - self.rsi_overbought)
                conviction_score -= rsi_score * 0.4
                reasons.append(f"rsi_overbought:{rsi:.2f}")
        
        # 2. Bollinger Band Extreme Confirmation
        bb = self._calculate_bollinger_bands(market.prices, self.bb_period, self.bb_std)
        if bb is not None:
            middle_band, upper_band, lower_band = bb
            if current_price < lower_band:
                # Deep oversold - strong buy signal
                bb_score = min(1.0, (lower_band - current_price) / lower_band * 2)
                conviction_score += bb_score * 0.3
                reasons.append(f"bb_oversold:{bb_score:.3f}")
            elif current_price > upper_band:
                # Deep overbought - strong sell signal
                bb_score = min(1.0, (current_price - upper_band) / upper_band * 2)
                conviction_score -= bb_score * 0.3
                reasons.append(f"bb_overbought:{bb_score:.3f}")
        
        # 3. MACD Confirmation
        macd_result = self._calculate_macd(market.prices, self.macd_fast, self.macd_slow, self.macd_signal)
        if macd_result is not None:
            macd_line, signal_line, histogram = macd_result
            if histogram > 0 and macd_line > signal_line:
                # Bullish MACD - buy confirmation
                macd_score = min(1.0, histogram * 10)
                conviction_score += macd_score * 0.3
                reasons.append(f"macd_bullish:{macd_score:.3f}")
            elif histogram < 0 and macd_line < signal_line:
                # Bearish MACD - sell confirmation
                macd_score = min(1.0, abs(histogram) * 10)
                conviction_score -= macd_score * 0.3
                reasons.append(f"macd_bearish:{macd_score:.3f}")
        
        reason = "|".join(reasons) if reasons else "no_conviction"
        return (conviction_score, reason)

    def _calculate_optimal_position_size(self, market: MarketSnapshot, portfolio_value: float, conviction_score: float) -> float:
        """Calculate aggressive position size based on conviction score."""
        # Base position size
        base_size = self.base_position_pct
        
        # Aggressive scaling based on conviction
        if conviction_score >= 0.9:
            position_factor = self.conviction_position_multiplier  # 2x for extremely high conviction
        elif conviction_score >= 0.8:
            position_factor = 1.5  # 1.5x for high conviction
        else:
            position_factor = 1.0  # Base size for moderate conviction
            
        # Recent performance adjustment
        if len(self._win_loss_history) >= 5:
            recent_win_rate = sum(self._win_loss_history[-5:]) / 5
            if recent_win_rate < 0.8:
                performance_factor = 0.7  # Reduce position size after poor performance
            else:
                performance_factor = 1.0
        else:
            performance_factor = 1.0
            
        # Volatility adjustment - increase size in moderate volatility
        current_vol = self._calculate_volatility(market.prices, 20)
        if current_vol is not None:
            if current_vol > 0.03:  # High volatility
                vol_factor = 0.8  # Reduce position in high volatility
            elif current_vol < 0.01:  # Low volatility
                vol_factor = 1.2  # Increase position in low volatility
            else:
                vol_factor = 1.0  # Normal volatility
        else:
            vol_factor = 1.0
            
        # Combine all factors
        optimal_size = base_size * position_factor * performance_factor * vol_factor
        optimal_size = max(0.05, min(self.max_position_pct, optimal_size))  # Clamp between 5% and max
        
        return optimal_size

    def _check_trade_limits(self, now: datetime) -> Tuple[bool, str]:
        """Check trade count and frequency limits."""
        # Trade count limit
        if self._trade_count >= self.max_trades:
            return (False, "max_trades_reached")
            
        # Time between trades
        if self._last_trade_time is not None:
            time_since_last = now - self._last_trade_time
            min_interval = timedelta(hours=self.min_time_between_trades)
            if time_since_last < min_interval:
                return (False, f"min_time_between_trades_not_met:{time_since_last.total_seconds()/3600:.1f}h")
                
        return (True, "ok")

    def _check_drawdown_limits(self, portfolio_value: float) -> bool:
        """Check if drawdown limits are exceeded."""
        if self._peak_portfolio_value == 0:
            self._peak_portfolio_value = portfolio_value
            return True
            
        # Update peak portfolio value
        if portfolio_value > self._peak_portfolio_value:
            self._peak_portfolio_value = portfolio_value
            self._consecutive_losses = 0  # Reset consecutive losses
            
        # Calculate current drawdown
        drawdown = (self._peak_portfolio_value - portfolio_value) / self._peak_portfolio_value
        
        # If we have consecutive losses, increase caution
        if self._last_signal == "sell" and self._entry_price and portfolio_value < self._entry_price:
            self._consecutive_losses += 1
        elif self._last_signal == "buy" and self._entry_price and portfolio_value > self._entry_price:
            self._consecutive_losses = 0  # Reset on profitable trade
            
        # Stop trading after consecutive loss limit
        if self._consecutive_losses >= self.consecutive_loss_limit:
            return False  # Stop trading after consecutive losses
            
        # Check maximum drawdown
        if drawdown > self.max_drawdown_pct:
            return False  # Stop trading if max drawdown exceeded
            
        return True

    # --------------------------------- Main Logic ----------------------------------

    def generate_signal(self, market: MarketSnapshot, portfolio) -> Signal:
        """Generate trading signal using high-conviction ultra-profit approach."""
        now = datetime.now(timezone.utc)
        
        # Update internal histories
        self._price_history.append(market.current_price)
        if len(self._price_history) > 200:
            self._price_history = self._price_history[-200:]
        
        # Need sufficient price history
        if len(market.prices) < max(self.rsi_period, self.bb_period, self.macd_slow):
            self._log_local("DECISION", "HOLD | reason=insufficient_data")
            return Signal("hold", reason="Insufficient price data")
            
        current_price = market.current_price
        portfolio_value = portfolio.cash + portfolio.quantity * current_price
        
        # Update peak portfolio value
        if portfolio_value > self._peak_portfolio_value:
            self._peak_portfolio_value = portfolio_value
            
        # Check trade limits
        can_trade, trade_limit_reason = self._check_trade_limits(now)
        if not can_trade:
            self._log_local("DECISION", f"HOLD | reason=trade_limit | detail={trade_limit_reason}")
            return Signal("hold", reason=f"Trade limit: {trade_limit_reason}")
            
        # Check drawdown limits
        if not self._check_drawdown_limits(portfolio_value):
            self._log_local("RISK", "HOLD | reason=drawdown_limit_exceeded")
            return Signal("hold", reason="Drawdown limit exceeded")
            
        # Generate high-conviction signal
        conviction_score, conviction_reason = self._high_conviction_signal(market)
        
        # Apply high-conviction threshold
        if abs(conviction_score) < self.conviction_threshold:
            self._log_local("DECISION", f"HOLD | reason=low_conviction | score={conviction_score:.3f}")
            return Signal("hold", reason=f"Low conviction: {conviction_score:.3f}")
            
        # Determine signal direction
        final_signal = "buy" if conviction_score > 0 else "sell"
        reason = f"CONVICTION:{conviction_reason}|SCORE:{conviction_score:.3f}"
        
        # Position management
        if final_signal == "buy" and self._last_signal == "buy":
            final_signal = "hold"
            reason = "already_in_long_position"
        elif final_signal == "sell" and self._last_signal != "buy":
            final_signal = "hold"
            reason = "no_long_position_to_sell"
            
        # Risk management overrides
        # Trailing stop and take profit logic
        if self._last_signal == "buy" and self._entry_price is not None:
            price_change_pct = (current_price - self._entry_price) / self._entry_price
            
            # Update trailing high
            if self._trailing_high is None or current_price > self._trailing_high:
                self._trailing_high = current_price
                
            # Trailing stop (aggressive for high profit)
            if self._trailing_high is not None:
                trailing_stop_price = self._trailing_high * (1 - self.trailing_stop_pct)
                if current_price <= trailing_stop_price:
                    final_signal = "sell"
                    reason = f"TRAILING_STOP_TRIGGERED | high:{self._trailing_high:.2f} | current:{current_price:.2f}"
                    
            # Stop loss (moderate for high win rate)
            elif price_change_pct <= -self.stop_loss_pct:
                final_signal = "sell"
                reason = f"STOP_LOSS_TRIGGERED | loss:{price_change_pct:.2%}"
                
            # Take profit (aggressive for high profit)
            elif price_change_pct >= self.take_profit_pct:
                final_signal = "sell"
                reason = f"TAKE_PROFIT_TRIGGERED | profit:{price_change_pct:.2%}"
                
            # Time-based exit (moderate for high win rate)
            elif self._entry_time and (now - self._entry_time).days > 3:
                final_signal = "sell"
                reason = "TIME_BASED_EXIT | position_held_over_3_days"
                
        # Execute final decision
        if final_signal == "buy":
            # Check if we have cash
            position_size_pct = self._calculate_optimal_position_size(market, portfolio_value, conviction_score)
            notional = portfolio.cash * position_size_pct
            if notional <= 0:
                self._log_local("DECISION", "HOLD | reason=insufficient_cash")
                return Signal("hold", reason="Insufficient cash")
                
            size = notional / current_price
            if size <= 0:
                self._log_local("DECISION", "HOLD | reason=invalid_size")
                return Signal("hold", reason="Invalid position size")
                
            self._last_signal = "buy"
            self._entry_price = current_price
            self._entry_time = now
            self._trailing_high = current_price
            self._trailing_low = current_price
            self._last_trade_time = now
            self._trade_count += 1
            self._log_local("DECISION", f"BUY | reason={reason} | size={size:.8f} | notional=${notional:,.2f} | position_size={position_size_pct:.2%} | score={conviction_score:.3f}")
            return Signal("buy", size=size, reason=reason)
            
        elif final_signal == "sell":
            # Check if we have positions
            if portfolio.quantity <= 0:
                self._log_local("DECISION", "HOLD | reason=no_position_to_sell")
                return Signal("hold", reason="No position to sell")
                
            is_stop_loss = "STOP_LOSS" in reason or "TRAILING_STOP" in reason
            self._last_signal = "sell" if is_stop_loss else None
            self._entry_price = None
            self._entry_time = None
            self._trailing_high = None
            self._trailing_low = None
            self._last_trade_time = now
            self._trade_count += 1
            size = portfolio.quantity
            self._log_local("DECISION", f"SELL | reason={reason} | size={size:.8f}")
            return Signal("sell", size=size, reason=reason)
        
        # Default hold
        self._log_local("DECISION", f"HOLD | reason={reason} | score={conviction_score:.3f}")
        return Signal("hold", reason=reason)

    def on_trade(self, signal: Signal, execution_price: float, execution_size: float, timestamp: datetime) -> None:
        """Update internal state after a trade is executed."""
        if signal.action == "buy" and execution_size > 0:
            self._log_local("ACTION", f"EXECUTED BUY {execution_size:.8f} @ ${execution_price:,.2f}")
        elif signal.action == "sell" and execution_size > 0:
            self._log_local("ACTION", f"EXECUTED SELL {execution_size:.8f} @ ${execution_price:,.2f}")
            
            # Update win/loss history
            if self._entry_price:
                is_win = execution_price > self._entry_price
                self._win_loss_history.append(is_win)
                if len(self._win_loss_history) > 100:
                    self._win_loss_history.pop(0)
                
                # Update consecutive losses counter
                if not is_win:
                    self._consecutive_losses += 1
                else:
                    self._consecutive_losses = 0
                    
                # Update performance score
                if is_win:
                    self._recent_performance_score = min(1.2, self._recent_performance_score + 0.05)
                else:
                    self._recent_performance_score = max(0.8, self._recent_performance_score - 0.1)

    def get_state(self) -> Dict[str, Any]:
        """Return strategy state for persistence."""
        return {
            "last_signal": self._last_signal,
            "entry_price": self._entry_price,
            "entry_time": _utc_iso(self._entry_time) if self._entry_time else None,
            "trailing_high": self._trailing_high,
            "trailing_low": self._trailing_low,
            "consecutive_losses": self._consecutive_losses,
            "peak_portfolio_value": self._peak_portfolio_value,
            "trade_count": self._trade_count,
            "last_trade_time": _utc_iso(self._last_trade_time) if self._last_trade_time else None,
            "win_loss_history": self._win_loss_history[-50:] if len(self._win_loss_history) > 50 else self._win_loss_history,
            "recent_performance_score": self._recent_performance_score
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore strategy state."""
        self._last_signal = state.get("last_signal")
        self._entry_price = state.get("entry_price")
        entry_time = state.get("entry_time")
        if entry_time:
            self._entry_time = datetime.fromisoformat(entry_time)
        self._trailing_high = state.get("trailing_high")
        self._trailing_low = state.get("trailing_low")
        self._consecutive_losses = state.get("consecutive_losses", 0)
        self._peak_portfolio_value = state.get("peak_portfolio_value", 0.0)
        self._trade_count = state.get("trade_count", 0)
        last_trade_time = state.get("last_trade_time")
        if last_trade_time:
            self._last_trade_time = datetime.fromisoformat(last_trade_time)
        self._win_loss_history = state.get("win_loss_history", [])
        self._recent_performance_score = state.get("recent_performance_score", 1.0)


# Register high-conviction ultra-profit strategy at import time
register_strategy("high_conviction_ultra_profit_strategy", lambda cfg, ex: HighConvictionUltraProfitStrategy(cfg, ex))