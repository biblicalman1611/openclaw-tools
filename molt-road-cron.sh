#!/bin/bash
# Molt Road Cron Job - Run every 4 hours
# Add to cron: 0 */4 * * * /home/ubuntu/.openclaw/workspace/molt-road-cron.sh

cd /home/ubuntu/.openclaw/workspace

# Run heartbeat
./molt-road-openclaw.sh heartbeat > molt-road-last-run.log 2>&1

# Check if any orders need attention
if grep -q "orders waiting for delivery\|deliveries to confirm" molt-road-last-run.log; then
    # Send alert to Telegram
    echo "🦞 Molt Road Alert: Orders need attention! Check molt-road-last-run.log" | \
    curl -s -X POST "http://localhost:18789/api/v1/sessions/send" \
    -H "Content-Type: application/json" \
    -d '{"message": "🦞 Molt Road Alert: Orders need attention! Run: ./molt-road-openclaw.sh heartbeat"}'
fi

# Log completion
echo "Last run: $(date)" >> molt-road-cron-history.log