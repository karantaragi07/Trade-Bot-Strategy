# High-Conviction Ultra-Profit Strategy Bot - Dockerfile
FROM python:3.11-slim

LABEL description="High-Conviction Ultra-Profit Trading Bot with Dashboard Integration"
LABEL strategies="high_conviction_ultra_profit_strategy"
LABEL tier="contest"

# Set working directory
WORKDIR /app

# Copy base bot infrastructure
COPY base-bot-template/ /app/base/

# Copy your strategy-specific files
COPY your-strategy-template/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/base/requirements.txt

# Make startup script executable
RUN chmod +x /app/startup.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')" || exit 1

# Expose ports
EXPOSE 8081 3011

# Default environment
ENV BOT_EXCHANGE=paper
ENV BOT_STRATEGY=high_conviction_ultra_profit_strategy
ENV BOT_SYMBOL=BTC-USD
ENV BOT_STARTING_CASH=10000.0
ENV BOT_SLEEP=60

# Start your strategy bot
CMD ["python", "/app/startup.py", "/app/bot.config.json"]