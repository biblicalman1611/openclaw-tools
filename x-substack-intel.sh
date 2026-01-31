#!/bin/bash
# X & Substack Intel Extractor
# Extract competitive intelligence from X posts and Substack articles

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to extract X post content using nitter instances
extract_x_post() {
    local url="$1"
    local post_id=$(echo "$url" | grep -oE '[0-9]{15,20}' | head -1)
    
    if [ -z "$post_id" ]; then
        echo -e "${RED}Error: Could not extract post ID from URL${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Extracting X post: $post_id${NC}"
    
    # Try multiple nitter instances for redundancy
    local nitter_instances=(
        "nitter.privacydev.net"
        "nitter.poast.org"
        "nitter.adminforge.de"
    )
    
    local content=""
    for instance in "${nitter_instances[@]}"; do
        echo "Trying $instance..."
        # Extract username from URL
        local username=$(echo "$url" | grep -oE '/[a-zA-Z0-9_]+/status' | sed 's|/||g' | sed 's|status||g')
        local nitter_url="https://$instance/$username/status/$post_id"
        
        content=$(curl -s -L "$nitter_url" | \
            grep -A 20 'tweet-content' | \
            sed 's/<[^>]*>//g' | \
            sed '/^[[:space:]]*$/d' | \
            head -20)
        
        if [ -n "$content" ]; then
            echo -e "${GREEN}Successfully extracted from $instance${NC}"
            break
        fi
    done
    
    if [ -z "$content" ]; then
        echo -e "${RED}Failed to extract content from all instances${NC}"
        return 1
    fi
    
    # Save to file
    local filename="x_post_${post_id}_$(date +%Y%m%d_%H%M%S).txt"
    echo "=== X Post Intelligence ===" > "$filename"
    echo "URL: $url" >> "$filename"
    echo "Post ID: $post_id" >> "$filename"
    echo "Extracted: $(date)" >> "$filename"
    echo "" >> "$filename"
    echo "=== Content ===" >> "$filename"
    echo "$content" >> "$filename"
    
    echo -e "${GREEN}Saved to: $filename${NC}"
    return 0
}

# Function to extract Substack article
extract_substack() {
    local url="$1"
    
    echo -e "${BLUE}Extracting Substack article: $url${NC}"
    
    # Download the page
    local html_file="substack_temp_$$.html"
    curl -s -L "$url" > "$html_file"
    
    # Extract title
    local title=$(grep -oP '(?<=<title>)[^<]+' "$html_file" | head -1)
    
    # Extract main content
    local content=$(cat "$html_file" | \
        grep -A 1000 'available-content' | \
        sed 's/<[^>]*>//g' | \
        sed 's/&nbsp;/ /g' | \
        sed 's/&quot;/"/g' | \
        sed "s/&apos;/'/g" | \
        sed 's/&amp;/\&/g' | \
        sed '/^[[:space:]]*$/d' | \
        head -500)
    
    # Extract subscriber count if visible
    local subscribers=$(grep -oE '[0-9,]+\s*subscribers?' "$html_file" | head -1)
    
    # Clean up temp file
    rm -f "$html_file"
    
    # Generate filename from title
    local safe_title=$(echo "$title" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-50)
    local filename="substack_${safe_title}_$(date +%Y%m%d_%H%M%S).txt"
    
    # Save to file
    echo "=== Substack Intelligence ===" > "$filename"
    echo "URL: $url" >> "$filename"
    echo "Title: $title" >> "$filename"
    echo "Subscribers: $subscribers" >> "$filename"
    echo "Extracted: $(date)" >> "$filename"
    echo "" >> "$filename"
    echo "=== Content ===" >> "$filename"
    echo "$content" >> "$filename"
    
    echo -e "${GREEN}Saved to: $filename${NC}"
    return 0
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        echo "X & Substack Intel Extractor"
        echo ""
        echo "Usage:"
        echo "  $0 <URL>                Extract content from X or Substack URL"
        echo "  $0 analyze <file>       Analyze extracted content for insights"
        echo ""
        echo "Examples:"
        echo "  $0 https://x.com/someuser/status/1234567890"
        echo "  $0 https://substack.com/@someuser/p/article-title"
        echo "  $0 analyze x_post_1234567890.txt"
        exit 1
    fi
    
    local command="$1"
    
    # Create intel directory if it doesn't exist
    mkdir -p ~/.openclaw/workspace/intel
    cd ~/.openclaw/workspace/intel
    
    if [ "$command" == "analyze" ]; then
        if [ $# -lt 2 ]; then
            echo -e "${RED}Error: Please provide a file to analyze${NC}"
            exit 1
        fi
        
        local file="$2"
        if [ ! -f "$file" ]; then
            echo -e "${RED}Error: File not found: $file${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}Analyzing $file for marketing intelligence...${NC}"
        echo ""
        echo "=== Key Metrics ==="
        echo "Word count: $(wc -w < "$file")"
        echo "Line count: $(wc -l < "$file")"
        echo ""
        echo "=== Emotional Triggers ==="
        grep -i -E "afraid|angry|anxious|broken|desperate|empty|failed|fear|frustrated|guilty|helpless|hopeless|hurt|inadequate|insecure|lonely|lost|overwhelmed|pain|rejected|shame|struggle|stuck|tired|weak|worried" "$file" | head -10 || echo "No strong emotional triggers found"
        echo ""
        echo "=== Call-to-Action Phrases ==="
        grep -i -E "click|join|buy|get|start|download|subscribe|learn|discover|unlock|access|grab|claim|secure|reserve" "$file" | head -10 || echo "No CTAs found"
        echo ""
        echo "=== Power Words ==="
        grep -i -E "proven|secret|breakthrough|transform|revolutionary|exclusive|limited|urgent|powerful|essential|critical|vital" "$file" | head -10 || echo "No power words found"
        
    elif [[ "$command" =~ ^https?:// ]]; then
        # It's a URL
        if [[ "$command" =~ x\.com|twitter\.com ]]; then
            extract_x_post "$command"
        elif [[ "$command" =~ substack\.com ]]; then
            extract_substack "$command"
        else
            echo -e "${RED}Error: Unsupported URL. Only X.com and Substack.com URLs are supported.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Error: Invalid command or URL${NC}"
        exit 1
    fi
}

# Run main function
main "$@"