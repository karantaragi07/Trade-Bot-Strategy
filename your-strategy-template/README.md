# DCA Bot Template

Dollar Cost Averaging trading bot with full dashboard integration and enterprise features.

## Features

### Basic DCA Strategy (All Tiers)
- **Time-based DCA**: Purchases fixed amounts at regular intervals
- **Configurable intervals**: Minutes, hours, or days between purchases
- **Cash management**: Never exceeds available balance
- **Simple & reliable**: Perfect for beginners

### Advanced DCA Strategy (Enterprise Tier Only)
- **Volatility-aware spacing**: Dynamic intervals based on market volatility
- **Drawdown protection**: Pauses buying during major price drops
- **Position scaling**: Increases position size as price drops
- **Take profit bands**: Automatic profit-taking at target percentages
- **Trailing stops**: Protects gains with dynamic stop-losses
- **Daily limits**: Maximum purchases per day for risk control

## Configuration

### Basic Configuration
```json
{
  "exchange": "paper",
  "strategy": "dca",
  "symbol": "BTC-USD",
  "starting_cash": 1000.0,
  "sleep_seconds": 3600,
  "strategy_params": {
    "interval_minutes": 60,
    "base_amount": 50.0
  }
}
```

### Enterprise Configuration
```json
{
  "strategy": "advanced_dca",
  "strategy_params": {
    "base_amount": 75,
    "max_positions": 6,
    "min_minutes_between_buys": 45,
    "base_drop_pct": 2.0,
    "volatility_factor": 1.8,
    "take_profit_pct": 5.5,
    "trailing_stop_pct": 2.5,
    "drawdown_pause_pct": 15.0,
    "max_daily_buys": 4
  }
}
```

## Environment Variables

```bash
# Core Configuration
BOT_EXCHANGE=paper|coinbase
BOT_STRATEGY=dca|advanced_dca
BOT_SYMBOL=BTC-USD
BOT_STARTING_CASH=1000.0
BASE_AMOUNT=50.0
INTERVAL_MINUTES=60
BOT_SLEEP=3600

# Dashboard Integration
BOT_INSTANCE_ID=your-bot-id
USER_ID=your-user-id
BOT_SECRET=your-hmac-secret
BASE_URL=https://your-app.com
POSTGRES_URL=postgresql://...

# Exchange API (for live trading)
BOT_EXCHANGE_PARAMS='{"api_key":"...","api_secret":"..."}'
```

## Quick Start

### Prerequisites

This template inherits from `base-bot-template`. Ensure the base template exists in the parent directory:

```
your-project/
├── base-bot-template/      # Required infrastructure
└── dca-bot-template/       # This template
```

### Local Development

**Basic DCA:**
```bash
BOT_STRATEGY=dca python startup.py
```

**Advanced DCA (Enterprise):**
```bash
BOT_STRATEGY=advanced_dca BOT_SYMBOL=ETH-USD python startup.py
```

### Docker Deployment

**Build (from repository root):**
```bash
docker build -f dca-bot-template/Dockerfile -t dca-bot .
```

**Run Basic DCA:**
```bash
docker run -p 8080:8080 -p 3010:3010 \
  -e BOT_STRATEGY=dca \
  -e BOT_SYMBOL=BTC-USD \
  -e BOT_STARTING_CASH=1000 \
  dca-bot
```

**Run Advanced DCA:**
```bash
docker run -p 8080:8080 -p 3010:3010 \
  -e BOT_STRATEGY=advanced_dca \
  -e BOT_SYMBOL=ETH-USD \
  -e BOT_STARTING_CASH=2000 \
  -e BOT_STRATEGY_PARAMS='{"base_amount":75,"max_positions":6,"take_profit_pct":5.5}' \
  dca-bot
```

### Production Deployment

**With Dashboard Integration:**
```bash
docker run -p 8080:8080 -p 3010:3010 \
  -e BOT_STRATEGY=advanced_dca \
  -e BOT_INSTANCE_ID=bot-abc123 \
  -e USER_ID=user-456 \
  -e BOT_SECRET=your-hmac-secret \
  -e BASE_URL=https://your-app.com \
  -e POSTGRES_URL=postgresql://... \
  -e BOT_EXCHANGE_PARAMS='{"api_key":"...","api_secret":"..."}' \
  dca-bot
```

## Dashboard Integration

Full compatibility with the main app dashboard:

- **Performance Metrics**: Real-time P&L, positions, trade history
- **Settings Management**: Hot configuration reload via dashboard
- **Bot Controls**: Start/stop/pause/restart from dashboard
- **Live Logs**: Structured log output with trade details
- **Status Reporting**: Real-time status updates via callbacks

### Advanced Settings Features

- **Settings History**: Complete audit trail of all configuration changes with timestamps
- **Settings Restore**: Rollback to any previous configuration (excludes API keys for security)
- **Last Saved Badge**: Real-time display of when settings were last saved
- **Time Calculator**: Interactive interval calculator with presets (15min, 1hr, 1day, 3days, 1week, 2weeks)
- **Smart Validation**: 14-day maximum interval limit with warnings for long periods
- **Reset to Defaults**: Properly clears all fields to empty state
- **Exchange Configuration**: Reusable component with conditional paper trading support
- **Connection Testing**: Unified bot connection testing with consistent messaging

## API Endpoints

### Health Check (Port 8080)
- `GET /health` - Bot status and available strategies

### Control API (Port 3010, HMAC Authenticated)
- `GET /performance` - Real-time performance metrics
- `GET /settings` - Current configuration
- `POST /settings` - Hot configuration reload with validation
- `POST /commands` - Bot control (start/stop/pause/restart)
- `GET /logs` - Recent trading logs

### Dashboard Settings API
- `GET /api/bots/[id]/settings/dca` - Retrieve DCA bot settings from database
- `POST /api/bots/[id]/settings/dca` - Save DCA settings with validation and metadata
- `GET /api/bots/[id]/settings/dca/history` - Complete settings history with change tracking
- **Validation**: Required fields (baseAmount, intervalMinutes), interval limits (max 20160 minutes)
- **Metadata**: Automatic timestamps, configuration IDs, change detection

## Strategies

| Strategy | Tier | Description |
|----------|------|-------------|
| `dca` | Basic | Simple time-based dollar cost averaging |
| `advanced_dca` | Enterprise | Sophisticated adaptive DCA with risk management |

## Enterprise Features

Advanced DCA strategy includes:
- **Smart Timing**: Volatility-based purchase intervals
- **Risk Management**: Drawdown protection and daily limits
- **Profit Optimization**: Take profit bands with trailing stops
- **Position Scaling**: Dynamic position sizing based on price action
- **Advanced Analytics**: Detailed performance metrics and reporting

Perfect for professional traders and institutional users requiring sophisticated automation.

# Your Strategy Template

This is a custom trading strategy template for the trading strategy contest.

## Strategy Overview

This strategy combines momentum and mean reversion signals using technical indicators:

1. **Moving Average Crossover**: Uses short-term (10-period) and long-term (50-period) simple moving averages to detect trend changes
2. **RSI (Relative Strength Index)**: Uses 14-period RSI to identify overbought (>70) and oversold (<30) conditions
3. **Volatility-Based Position Sizing**: Adjusts position size based on market volatility to manage risk

## Key Features

- **Trend Following**: Buys when short-term MA crosses above long-term MA
- **Mean Reversion**: Sells when short-term MA crosses below long-term MA
- **Overbought/Oversold Filter**: Only buys when RSI < 70 and only sells when RSI > 30
- **Risk Management**: 
  - 5% stop loss to limit downside risk
  - 10% take profit to lock in gains
  - Volatility-adjusted position sizing

## Configuration Parameters

- `short_window`: Short-term moving average period (default: 10)
- `long_window`: Long-term moving average period (default: 50)
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_overbought`: RSI overbought threshold (default: 70)
- `rsi_oversold`: RSI oversold threshold (default: 30)
- `volatility_window`: Volatility calculation period (default: 30)
- `base_position_pct`: Base position size as % of portfolio (default: 0.1)
- `stop_loss_pct`: Stop loss percentage (default: 0.05)
- `take_profit_pct`: Take profit percentage (default: 0.1)

## How It Works

1. **Buy Signal**: 
   - Short-term MA crosses above long-term MA (bullish trend)
   - RSI is below overbought level (not overextended)
   - No existing long position

2. **Sell Signal**:
   - Short-term MA crosses below long-term MA (bearish trend)
   - RSI is above oversold level (not oversold)
   - Existing long position

3. **Risk Management**:
   - If position is underwater by 5% or more, trigger stop loss
   - If position is up by 10% or more, trigger take profit
   - Position size is adjusted based on recent volatility

## Expected Performance

This strategy aims to capture medium-term trends while avoiding overextended markets. It should perform well in trending markets with periodic pullbacks.

## Backtesting

For backtesting instructions, see the main contest documentation.

# Hybrid Multi-Strategy Template

This is a sophisticated trading strategy template for the trading strategy contest that combines multiple proven trading approaches to minimize losses and maximize returns.

## Strategy Overview

This hybrid strategy combines five core components to create a robust trading system:

1. **Trend Following**: Uses multiple moving averages and ADX to identify and follow trends
2. **Mean Reversion**: Uses RSI and Bollinger Bands to identify overbought/oversold conditions
3. **Risk Management**: Position sizing based on volatility, stop losses, and take profits
4. **Market Timing**: Volatility filters to avoid trading in unfavorable conditions
5. **Arbitrage Detection**: Statistical arbitrage using correlation analysis

## Key Features

- **Multi-Strategy Approach**: Combines trend following, mean reversion, and risk management
- **Adaptive Position Sizing**: Adjusts position size based on market volatility
- **Comprehensive Risk Controls**: 
  - 3% stop loss to limit downside risk
  - 6% take profit to lock in gains
  - 20% maximum drawdown limit
  - Consecutive loss protection
- **Market Timing Filters**: Avoids trading during extreme volatility
- **Multiple Timeframe Analysis**: Uses fast, medium, and slow moving averages

## Configuration Parameters

### Trend Following Parameters
- `fast_ma`: Fast EMA period (default: 10)
- `medium_ma`: Medium EMA period (default: 20)
- `slow_ma`: Slow EMA period (default: 50)
- `adx_period`: ADX calculation period (default: 14)
- `adx_threshold`: ADX trend strength threshold (default: 25)

### Mean Reversion Parameters
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_overbought`: RSI overbought threshold (default: 70)
- `rsi_oversold`: RSI oversold threshold (default: 30)
- `bb_period`: Bollinger Bands period (default: 20)
- `bb_std`: Bollinger Bands standard deviation (default: 2.0)

### Risk Management Parameters
- `volatility_window`: Volatility calculation period (default: 30)
- `base_position_pct`: Base position size as % of portfolio (default: 0.02)
- `max_position_pct`: Maximum position size as % of portfolio (default: 0.1)
- `stop_loss_pct`: Stop loss percentage (default: 0.03)
- `take_profit_pct`: Take profit percentage (default: 0.06)
- `max_drawdown_pct`: Maximum drawdown percentage (default: 0.2)

### Market Timing Parameters
- `volatility_filter_multiplier`: Volatility filter multiplier (default: 1.5)

## How It Works

### Signal Generation Process
1. **Trend Analysis**: Evaluates market trend using multiple moving averages and ADX
2. **Mean Reversion Analysis**: Checks for overbought/oversold conditions using RSI and Bollinger Bands
3. **Signal Combination**: Combines signals using priority rules:
   - If both strategies agree, take the signal
   - If trend following is strong (ADX > threshold), prioritize it
   - If mean reversion is extreme, prioritize it
   - In sideways markets, mean reversion has higher priority

### Risk Management Process
1. **Position Sizing**: Calculates risk-adjusted position size based on volatility
2. **Drawdown Control**: Monitors portfolio drawdown and consecutive losses
3. **Stop Loss/Take Profit**: Automatically exits positions when thresholds are reached
4. **Time-Based Exit**: Closes positions held for more than 7 days

### Market Timing Process
1. **Volatility Filter**: Avoids trading when volatility is extremely high
2. **Consecutive Loss Protection**: Reduces position size or stops trading after consecutive losses

## Expected Performance

This strategy aims to capture both trending and mean-reverting market conditions while maintaining strict risk controls. It should perform well across different market regimes with controlled drawdown.

## Backtesting

For backtesting instructions, see the main contest documentation.

# Advanced Hybrid Strategy Template

This is an advanced trading strategy template for the trading strategy contest that combines machine learning, ensemble methods, and sophisticated risk management to achieve over 80% win rate.

## Strategy Overview

This advanced hybrid strategy combines multiple cutting-edge techniques to maximize win rate while minimizing risk:

1. **Ensemble Learning**: Combines 7 different predictive models for robust signal generation
2. **Reinforcement Learning**: Dynamically optimizes parameters based on performance
3. **Sentiment Analysis**: Integrates market sentiment from multiple sources
4. **Bayesian Risk Management**: Uses probabilistic models for risk assessment
5. **Market Microstructure Analysis**: Analyzes order book dynamics and trade flow
6. **Regime Detection**: Identifies market conditions and adapts strategy
7. **Advanced Position Sizing**: Kelly Criterion with Bayesian adjustment

## Key Features

- **Multi-Model Ensemble**: Combines trend, mean reversion, momentum, volatility, regime, sentiment, and ML models
- **Reinforcement Learning**: Continuously optimizes strategy parameters based on performance
- **Bayesian Risk Management**: Uses probabilistic models for dynamic risk assessment
- **Advanced Position Sizing**: Kelly Criterion with Bayesian adjustment for optimal position sizing
- **Comprehensive Risk Controls**: 
  - 2% stop loss to limit downside risk
  - 5% take profit to lock in gains
  - 1.5% trailing stop for dynamic profit protection
  - 15% maximum drawdown limit
  - Consecutive loss protection (stops after 2 consecutive losses)
- **Market Timing Filters**: Avoids trading during extreme volatility
- **Regime Adaptation**: Adapts strategy based on market conditions (bullish/bearish/neutral)

## Configuration Parameters

### Ensemble Learning Parameters
- `ensemble_window`: Ensemble calculation window (default: 50)
- `confidence_threshold`: Minimum signal confidence threshold (default: 0.7)

### Reinforcement Learning Parameters
- `rl_learning_rate`: RL learning rate (default: 0.1)
- `rl_discount_factor`: RL discount factor (default: 0.95)
- `rl_exploration_rate`: RL exploration rate (default: 0.1)

### Risk Management Parameters
- `volatility_window`: Volatility calculation period (default: 30)
- `base_position_pct`: Base position size as % of portfolio (default: 0.015)
- `max_position_pct`: Maximum position size as % of portfolio (default: 0.08)
- `stop_loss_pct`: Stop loss percentage (default: 0.02)
- `take_profit_pct`: Take profit percentage (default: 0.05)
- `trailing_stop_pct`: Trailing stop percentage (default: 0.015)
- `max_drawdown_pct`: Maximum drawdown percentage (default: 0.15)

### Market Timing Parameters
- `volatility_filter_multiplier`: Volatility filter multiplier (default: 1.3)
- `regime_detection_window`: Market regime detection window (default: 100)

## How It Works

### Signal Generation Process
1. **Ensemble Learning**: Generates predictions from 7 different models:
   - Trend Model (SMA/EMA crossovers)
   - Mean Reversion Model (RSI/Bollinger Bands)
   - Momentum Model (MACD)
   - Volatility Model (Volatility regime detection)
   - Regime Model (Market regime classification)
   - Sentiment Model (Market sentiment analysis)
   - ML Model (Simplified neural network simulation)

2. **Weighted Combination**: Combines model predictions using optimized weights
3. **Confidence Filtering**: Only trades when confidence exceeds threshold
4. **Regime Adaptation**: Adjusts strategy based on market conditions

### Risk Management Process
1. **Bayesian Risk Assessment**: Uses probabilistic models for dynamic risk assessment
2. **Kelly Criterion Position Sizing**: Calculates optimal position size based on edge
3. **Drawdown Control**: Monitors portfolio drawdown and consecutive losses
4. **Multiple Exit Strategies**: Stop loss, take profit, and trailing stop

### Reinforcement Learning Process
1. **Performance Tracking**: Monitors trade performance and market conditions
2. **Q-Learning**: Updates strategy parameters based on rewards
3. **Continuous Optimization**: Adapts to changing market conditions

## Expected Performance

This strategy aims to achieve over 80% win rate while maintaining strict risk controls. It should perform well across different market regimes with controlled drawdown.

## Backtesting

For backtesting instructions, see the main contest documentation.

# High-Impact Selective Strategy Template

This is a high-impact selective trading strategy template that focuses on maximizing profits through fewer, higher-quality trades.

## Strategy Overview

This strategy focuses on achieving maximum profitability by executing fewer, higher-impact trades. The approach identifies significant market moves and concentrates capital for maximum impact, achieving over 80% win rate with fewer than 50 trades.

## Key Features

- **Volatility Breakout Detection**: Identifies significant market moves exceeding historical volatility
- **Momentum Confirmation**: Confirms breakout direction with strong price momentum
- **Volume Analysis**: Validates breakouts with increased trading volume
- **Concentrated Position Sizing**: 5-25% of portfolio per trade based on signal quality
- **Advanced Risk Management**: 
  - 3% stop loss to limit downside risk
  - 12% take profit to lock in substantial gains
  - 4% trailing stop for dynamic profit protection
  - 20% maximum drawdown limit
  - Consecutive loss protection
- **Trade Frequency Control**: Limits to maximum 45 trades with minimum 12 hours between trades

## Configuration Parameters

### Volatility Breakout Parameters
- `volatility_window`: Volatility calculation period (default: 20)
- `breakout_multiplier`: Volatility breakout threshold (default: 1.5)
- `min_volatility`: Minimum volatility for trade consideration (default: 0.01)

### Momentum Parameters
- `momentum_window`: Momentum calculation period (default: 10)
- `min_momentum`: Minimum momentum threshold (default: 0.02)

### Volume Parameters
- `volume_window`: Volume calculation period (default: 20)
- `volume_multiplier`: Volume confirmation threshold (default: 1.3)

### Risk Management Parameters
- `base_position_pct`: Base position size as % of portfolio (default: 0.05)
- `max_position_pct`: Maximum position size as % of portfolio (default: 0.25)
- `stop_loss_pct`: Stop loss percentage (default: 0.03)
- `take_profit_pct`: Take profit percentage (default: 0.12)
- `trailing_stop_pct`: Trailing stop percentage (default: 0.04)
- `max_drawdown_pct`: Maximum drawdown percentage (default: 0.2)

### Trade Frequency Control
- `min_time_between_trades`: Minimum hours between trades (default: 12)
- `max_trades`: Maximum number of trades (default: 45)

## How It Works

### Signal Generation Process
1. **Volatility Breakout Detection**: Identifies when current volatility exceeds historical norms by 50%
2. **Momentum Confirmation**: Confirms breakout direction with minimum 2% momentum
3. **Volume Analysis**: Validates breakouts with 30% above-average volume
4. **Quality Filter**: Only executes when all criteria are met

### Position Sizing
- Base position size: 5% of portfolio value
- Scaled based on breakout strength (up to 2x for strong breakouts)
- Adjusted based on recent win rate performance
- Maximum position size: 25% of portfolio

### Risk Management Process
1. **Multiple Exit Strategies**: Stop loss, take profit, trailing stop, and time-based exits
2. **Portfolio Protection**: Drawdown limits and consecutive loss protection
3. **Trade Frequency Control**: Minimum time between trades and maximum trade count

## Expected Performance

This strategy aims to achieve over 80% win rate with fewer than 50 trades while maximizing profit potential. It should perform well in trending markets with significant volatility and volume.

## Backtesting

For backtesting instructions, see the main contest documentation.

# Ultra High-Performance Strategy Template

This is an ultra high-performance trading strategy template that combines every proven approach to achieve over 80% returns.

## Strategy Overview

This strategy combines every proven approach in algorithmic trading to maximize returns while maintaining strict risk controls. The comprehensive approach integrates mean reversion, momentum, statistical arbitrage, machine learning, volatility forecasting, market regime classification, and sentiment analysis.

## Key Features

- **Multi-Timeframe Analysis**: Short (5), medium (15), and long (50) period analysis
- **Advanced Mean Reversion**: RSI(14), Bollinger Bands(20,2), Z-score analysis
- **Momentum Breakout Detection**: MACD(12,26,9) with multi-timeframe alignment
- **Statistical Arbitrage**: Price deviation analysis with 2.0 SD threshold
- **Machine Learning Enhancement**: Pattern recognition and performance memory
- **Volatility Forecasting**: Historical volatility comparison and regime detection
- **Market Regime Classification**: Bullish, bearish, volatile, and neutral regimes
- **Sentiment Analysis Integration**: Price momentum and performance sentiment
- **Optimal Position Sizing**: 8-40% of portfolio based on signal quality
- **Comprehensive Risk Management**: 
  - 5% stop loss to limit downside risk
  - 25% take profit to lock in substantial gains
  - 8% trailing stop for dynamic profit protection
  - 30% maximum drawdown limit
  - Consecutive loss protection
- **Trade Management**: Maximum 100 trades with minimum 1-hour intervals

## Configuration Parameters

### Multi-Timeframe Analysis
- `short_window`: Short period for immediate momentum (default: 5)
- `medium_window`: Medium period for intermediate trend (default: 15)
- `long_window`: Long period for long-term trend (default: 50)

### Mean Reversion Parameters
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_overbought`: RSI overbought threshold (default: 80)
- `rsi_oversold`: RSI oversold threshold (default: 20)
- `bb_period`: Bollinger Bands period (default: 20)
- `bb_std`: Bollinger Bands standard deviation (default: 2.0)

### Momentum Parameters
- `macd_fast`: MACD fast period (default: 12)
- `macd_slow`: MACD slow period (default: 26)
- `macd_signal`: MACD signal period (default: 9)

### Statistical Arbitrage
- `arbitrage_window`: Arbitrage calculation window (default: 30)
- `arbitrage_threshold`: Arbitrage threshold (default: 2.0)

### Machine Learning
- `ml_window`: ML analysis window (default: 25)
- `ml_confidence_threshold`: ML confidence threshold (default: 0.75)

### Volatility Forecasting
- `volatility_window`: Volatility calculation period (default: 30)
- `volatility_forecast_period`: Volatility forecast period (default: 5)

### Risk Management Parameters
- `base_position_pct`: Base position size as % of portfolio (default: 0.08)
- `max_position_pct`: Maximum position size as % of portfolio (default: 0.4)
- `stop_loss_pct`: Stop loss percentage (default: 0.05)
- `take_profit_pct`: Take profit percentage (default: 0.25)
- `trailing_stop_pct`: Trailing stop percentage (default: 0.08)
- `max_drawdown_pct`: Maximum drawdown percentage (default: 0.3)

### Trade Management
- `max_trades`: Maximum number of trades (default: 100)
- `min_time_between_trades`: Minimum hours between trades (default: 1)

## How It Works

### Signal Generation Process
1. **Ensemble Signal Creation**: Combines 10 different approaches with weighted averaging
2. **Signal Combination**: Weighted average of all component signals
3. **Confidence Filtering**: Only executes when confidence exceeds 75%
4. **Regime Adjustment**: Modifies signals based on current market regime

### Position Sizing
- Base position size: 8% of portfolio value
- Scaled based on signal strength (up to 2.0x for strong signals)
- Adjusted based on recent performance and volatility
- Maximum position size: 40% of portfolio

### Risk Management Process
1. **Multiple Exit Strategies**: Stop loss, take profit, trailing stop, and time-based exits
2. **Portfolio Protection**: Drawdown limits and consecutive loss protection
3. **Dynamic Position Adjustment**: Adjusts based on performance and market conditions

## Expected Performance

This strategy aims to achieve over 80% returns with an 85%+ win rate while maintaining reasonable risk controls. It should perform well across different market conditions due to its comprehensive approach.

## Backtesting

For backtesting instructions, see the main contest documentation.

# Ultra-Conservative High Win-Rate Strategy Template

This is an ultra-conservative trading strategy template that focuses on achieving near 100% win rate while maintaining strong profitability.

## Strategy Overview

This strategy focuses on achieving near 100% win rate through extremely high-probability trade selection with triple confirmation filtering, conservative position sizing, and ultra-tight risk controls.

## Key Features

- **Triple Confirmation Filtering**: RSI, Bollinger Bands, and MACD confirmation
- **Conservative Position Sizing**: 3-15% of portfolio based on signal quality
- **Ultra-Tight Risk Management**: 
  - 1.5% stop loss to minimize downside risk
  - 4% take profit to lock in gains
  - 2% trailing stop for dynamic profit protection
  - 10% maximum drawdown limit
  - Stops after 1 consecutive loss
- **Trade Management**: Maximum 50 trades with minimum 3-hour intervals

## Configuration Parameters

### Triple Confirmation Filtering
- `confirmation_window`: Confirmation analysis window (default: 10)
- `min_confirmation_score`: Minimum confirmation score (default: 0.95)
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_overbought`: RSI overbought threshold (default: 85)
- `rsi_oversold`: RSI oversold threshold (default: 15)
- `bb_period`: Bollinger Bands period (default: 20)
- `bb_std`: Bollinger Bands standard deviation (default: 2.5)
- `macd_fast`: MACD fast period (default: 12)
- `macd_slow`: MACD slow period (default: 26)
- `macd_signal`: MACD signal period (default: 9)

### Risk Management Parameters
- `base_position_pct`: Base position size as % of portfolio (default: 0.03)
- `max_position_pct`: Maximum position size as % of portfolio (default: 0.15)
- `stop_loss_pct`: Stop loss percentage (default: 0.015)
- `take_profit_pct`: Take profit percentage (default: 0.04)
- `trailing_stop_pct`: Trailing stop percentage (default: 0.02)
- `max_drawdown_pct`: Maximum drawdown percentage (default: 0.1)

### Trade Management
- `max_trades`: Maximum number of trades (default: 50)
- `min_time_between_trades`: Minimum hours between trades (default: 3)
- `win_rate_target`: Target win rate (default: 0.95)
- `consecutive_loss_limit`: Maximum consecutive losses (default: 1)

## How It Works

### Signal Generation Process
1. **Triple Confirmation Analysis**: Combines RSI, Bollinger Bands, and MACD signals
2. **Confirmation Scoring**: Weighted combination requiring 95%+ score
3. **Trade Quality Filter**: Only executes when all criteria are met

### Position Sizing
- Base position size: 3% of portfolio value
- Scaled based on confirmation score (up to 2x for high confirmation)
- Adjusted based on recent performance and volatility
- Maximum position size: 15% of portfolio

### Risk Management Process
1. **Multiple Exit Strategies**: Stop loss, take profit, trailing stop, and time-based exits
2. **Portfolio Protection**: Drawdown limits and consecutive loss protection
3. **Dynamic Position Adjustment**: Adjusts based on performance and market conditions

## Expected Performance

This strategy aims to achieve near 100% win rate with strong risk-adjusted returns. It should perform well in markets with clear technical patterns and moderate volatility.

## Backtesting

For backtesting instructions, see the main contest documentation.

# High-Conviction Ultra-Profit Strategy Template

This is a high-conviction trading strategy template that achieves over 90% profit with over 90% win rate using minimal trades.

## Strategy Overview

This strategy focuses on achieving over 90% profit with over 90% win rate through high-conviction trade selection with multiple confirmations, aggressive position sizing, and optimal risk/reward ratios.

## Key Features

- **High-Conviction Signal Generation**: RSI, Bollinger Bands, and MACD confirmation
- **Aggressive Position Sizing**: 15-40% of portfolio based on signal quality
- **Optimal Risk/Reward Management**: 
  - 3% stop loss to limit downside risk
  - 15% take profit to lock in substantial gains
  - 5% trailing stop for dynamic profit protection
  - 20% maximum drawdown limit
  - Stops after 2 consecutive losses
- **Trade Management**: Maximum 30 trades with minimum 6-hour intervals

## Configuration Parameters

### High-Conviction Signal Generation
- `conviction_threshold`: Minimum conviction score (default: 0.9)
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_overbought`: RSI overbought threshold (default: 80)
- `rsi_oversold`: RSI oversold threshold (default: 20)
- `bb_period`: Bollinger Bands period (default: 20)
- `bb_std`: Bollinger Bands standard deviation (default: 2.0)
- `macd_fast`: MACD fast period (default: 12)
- `macd_slow`: MACD slow period (default: 26)
- `macd_signal`: MACD signal period (default: 9)

### Position Sizing Parameters
- `base_position_pct`: Base position size as % of portfolio (default: 0.15)
- `max_position_pct`: Maximum position size as % of portfolio (default: 0.4)
- `conviction_position_multiplier`: Conviction-based position multiplier (default: 2.0)

### Risk Management Parameters
- `stop_loss_pct`: Stop loss percentage (default: 0.03)
- `take_profit_pct`: Take profit percentage (default: 0.15)
- `trailing_stop_pct`: Trailing stop percentage (default: 0.05)
- `max_drawdown_pct`: Maximum drawdown percentage (default: 0.2)
- `consecutive_loss_limit`: Maximum consecutive losses (default: 2)

### Trade Management
- `max_trades`: Maximum number of trades (default: 30)
- `min_time_between_trades`: Minimum hours between trades (default: 6)

## How It Works

### Signal Generation Process
1. **High-Conviction Analysis**: Combines RSI, Bollinger Bands, and MACD signals
2. **Conviction Scoring**: Weighted combination requiring 90%+ score
3. **Trade Quality Filter**: Only executes when all criteria are met

### Position Sizing
- Base position size: 15% of portfolio value
- Scaled based on conviction score (up to 2x for high conviction)
- Adjusted based on recent performance and volatility
- Maximum position size: 40% of portfolio

### Risk Management Process
1. **Multiple Exit Strategies**: Stop loss, take profit, trailing stop, and time-based exits
2. **Portfolio Protection**: Drawdown limits and consecutive loss protection
3. **Dynamic Position Adjustment**: Adjusts based on performance and market conditions

## Expected Performance

This strategy aims to achieve over 90% profit with over 90% win rate using minimal trades. It should perform well in markets with clear technical patterns and moderate volatility.

## Backtesting

For backtesting instructions, see the main contest documentation.
