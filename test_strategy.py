#!/usr/bin/env python3
"""Simple test for high-conviction ultra-profit strategy."""

import sys
import os

# Add paths
base_path = os.path.join(os.path.dirname(__file__), 'base-bot-template')
strategy_path = os.path.join(os.path.dirname(__file__), 'your-strategy-template')
sys.path.insert(0, base_path)
sys.path.insert(0, strategy_path)

# Import strategy
import your_strategy

# Import required classes
from strategy_interface import Portfolio
from exchange_interface import MarketSnapshot
from datetime import datetime

def test_strategy():
    """Test the high-conviction ultra-profit strategy logic."""
    print("Testing high-conviction ultra-profit strategy...")
    
    # Create a mock exchange and config
    class MockExchange:
        pass
    
    config = {
        "conviction_threshold": 0.9,
        "rsi_period": 14,
        "rsi_overbought": 80,
        "rsi_oversold": 20,
        "bb_period": 20,
        "bb_std": 2.0,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "base_position_pct": 0.15,
        "max_position_pct": 0.4,
        "conviction_position_multiplier": 2.0,
        "stop_loss_pct": 0.03,
        "take_profit_pct": 0.15,
        "trailing_stop_pct": 0.05,
        "max_drawdown_pct": 0.2,
        "consecutive_loss_limit": 2,
        "max_trades": 30,
        "min_time_between_trades": 6
    }
    
    # Create strategy instance
    exchange = MockExchange()
    strategy = your_strategy.HighConvictionUltraProfitStrategy(config, exchange)
    
    # Create mock market data (strong oversold condition)
    prices = []
    base_price = 45000
    # Create strong oversold condition - prices dropping then sharp recovery
    for i in range(30):
        if i < 10:
            # Sharp drop
            price = base_price - i * 300
        else:
            # Strong recovery
            price = base_price - 3000 + (i - 10) * 400
        prices.append(price)
    
    market = MarketSnapshot(
        symbol="BTC-USD",
        current_price=prices[-1],
        prices=prices,
        timestamp=datetime.now()
    )
    
    # Create mock portfolio
    portfolio = Portfolio(
        symbol="BTC-USD",
        cash=10000.0,
        quantity=0.0
    )
    
    # Generate signal
    signal = strategy.generate_signal(market, portfolio)
    print(f"Signal: {signal.action} ({signal.reason})")
    
    print("Strategy test completed successfully!")

if __name__ == "__main__":
    test_strategy()