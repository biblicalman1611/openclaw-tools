#!/bin/bash
# TinyFish Intelligence Extractor
# Your secret weapon for scraping anything

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if python dependencies are installed
check_dependencies() {
    if ! python3 -c "import requests" 2>/dev/null; then
        echo -e "${BLUE}Installing dependencies...${NC}"
        pip3 install requests python-dotenv --user
    fi
}

# Main function
main() {
    case "${1:-help}" in
        "setup")
            echo -e "${BLUE}🐟 TinyFish Setup${NC}"
            check_dependencies
            chmod +x tinyfish-scraper.py
            echo -e "${GREEN}✅ TinyFish ready!${NC}"
            echo "Your API key is stored in .env.tinyfish"
            ;;
            
        "test")
            echo -e "${BLUE}🐟 Testing TinyFish...${NC}"
            python3 tinyfish-scraper.py https://biblicalman.substack.com
            ;;
            
        "help"|"-h"|"--help")
            echo "🐟 TinyFish Intelligence Extractor"
            echo ""
            echo "This uses your TinyFish API to scrape ANY website"
            echo "- Bypasses anti-scraping measures"
            echo "- Works on X, Substack, LinkedIn, etc"
            echo "- Analyzes for Jake triggers & marketing angles"
            echo ""
            echo "Usage:"
            echo "  ./tinyfish-intel.sh setup               # First time setup"
            echo "  ./tinyfish-intel.sh <URL>               # Scrape single URL"
            echo "  ./tinyfish-intel.sh batch urls.txt      # Batch scraping"
            echo "  ./tinyfish-intel.sh test                # Test with your site"
            echo ""
            echo "Examples:"
            echo "  ./tinyfish-intel.sh https://x.com/paulcmaxwell/status/123"
            echo "  ./tinyfish-intel.sh https://substack.com/@johndoe/p/article"
            echo ""
            echo "Intel saved to: ~/. openclaw/workspace/intel/"
            ;;
            
        "batch")
            shift
            python3 tinyfish-scraper.py batch "$@"
            ;;
            
        *)
            # Assume it's a URL
            check_dependencies
            python3 tinyfish-scraper.py "$1"
            ;;
    esac
}

# Navigate to workspace
cd ~/.openclaw/workspace

# Run main function
main "$@"