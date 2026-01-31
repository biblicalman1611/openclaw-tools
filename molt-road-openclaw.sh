#!/bin/bash
# Molt Road Integration for OpenClaw
# Deploy and manage agent network from OpenClaw

set -euo pipefail

WORKSPACE=~/.openclaw/workspace
PYTHON_SCRIPTS="$WORKSPACE/molt-road-agent.py $WORKSPACE/molt-road-heartbeat.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Function to display help
show_help() {
    echo "🦞 Molt Road Agent Network Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Deploy new agents to Molt Road"
    echo "  status    - Check status of all agents"
    echo "  heartbeat - Run heartbeat check (orders, opportunities)"
    echo "  setup     - Initial setup and configuration"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy   # Deploy the agent network"
    echo "  $0 status   # Check agent balances and orders"
}

# Setup function
setup() {
    echo -e "${BLUE}🔧 Setting up Molt Road integration...${NC}"
    
    # Create directories
    mkdir -p "$WORKSPACE/molt-road-agents"
    mkdir -p "$WORKSPACE/molt-road-reports"
    
    # Make scripts executable
    chmod +x "$WORKSPACE/molt-road-agent.py"
    chmod +x "$WORKSPACE/molt-road-heartbeat.py"
    
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: $0 deploy"
    echo "2. Tweet verification codes for each agent"
    echo "3. Run: $0 heartbeat (periodically)"
}

# Deploy agents
deploy() {
    echo -e "${BLUE}🚀 Deploying Biblical Man Agent Network...${NC}"
    cd "$WORKSPACE"
    python3 molt-road-agent.py
}

# Check status
status() {
    echo -e "${BLUE}📊 Checking agent network status...${NC}"
    cd "$WORKSPACE"
    
    # Quick status check
    if [ -d "molt-road-agents" ] && [ "$(ls -A molt-road-agents)" ]; then
        agent_count=$(ls -1 molt-road-agents/*.json 2>/dev/null | wc -l)
        echo -e "${GREEN}Found $agent_count registered agents${NC}"
        
        # Run heartbeat for detailed status
        python3 molt-road-heartbeat.py
    else
        echo -e "${RED}No agents found. Run '$0 deploy' first.${NC}"
    fi
}

# Run heartbeat
heartbeat() {
    echo -e "${BLUE}💓 Running Molt Road heartbeat...${NC}"
    cd "$WORKSPACE"
    python3 molt-road-heartbeat.py
}

# Main command handler
case "${1:-help}" in
    deploy)
        deploy
        ;;
    status)
        status
        ;;
    heartbeat)
        heartbeat
        ;;
    setup)
        setup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac