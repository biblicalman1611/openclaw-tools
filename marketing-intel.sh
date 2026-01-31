#!/bin/bash
# Marketing Intelligence Extractor - Biblical Man Edition
# Extract and analyze competitor content from X and Substack

WORKSPACE="$HOME/.openclaw/workspace/intel"
PYTHON_SCRIPT="$HOME/.openclaw/workspace/intel_extractor.py"

# Create workspace
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# Function to batch process URLs from a file
batch_process() {
    local url_file="$1"
    if [ ! -f "$url_file" ]; then
        echo "Error: File not found: $url_file"
        exit 1
    fi
    
    echo "🚀 Batch processing URLs from $url_file"
    echo ""
    
    local success=0
    local failed=0
    
    while IFS= read -r url; do
        # Skip empty lines and comments
        [[ -z "$url" || "$url" =~ ^# ]] && continue
        
        echo "Processing: $url"
        if python3 "$PYTHON_SCRIPT" "$url"; then
            ((success++))
        else
            ((failed++))
        fi
        echo "---"
        sleep 2  # Be nice to servers
    done < "$url_file"
    
    echo ""
    echo "✅ Successful: $success"
    echo "❌ Failed: $failed"
}

# Function to create competitive analysis report
create_report() {
    echo "📊 Creating competitive analysis report..."
    
    local report_file="competitive_report_$(date +%Y%m%d_%H%M%S).md"
    
    echo "# Competitive Intelligence Report" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"
    
    # Analyze all JSON files
    for json_file in *.json; do
        [ -f "$json_file" ] || continue
        
        echo "## Source: $json_file" >> "$report_file"
        python3 "$PYTHON_SCRIPT" analyze "$json_file" >> "$report_file"
        echo "" >> "$report_file"
    done
    
    echo "📄 Report saved to: $report_file"
    
    # Create summary statistics
    echo "" >> "$report_file"
    echo "## Summary Statistics" >> "$report_file"
    echo "- Total sources analyzed: $(ls -1 *.json 2>/dev/null | wc -l)" >> "$report_file"
    echo "- Date range: $(date)" >> "$report_file"
}

# Function to monitor competitor
monitor_competitor() {
    local competitor="$1"
    local urls_file="competitors/${competitor}_urls.txt"
    
    mkdir -p competitors
    
    if [ ! -f "$urls_file" ]; then
        echo "Creating new competitor file: $urls_file"
        echo "# Add URLs to monitor for $competitor" > "$urls_file"
        echo "# One URL per line" >> "$urls_file"
        echo "" >> "$urls_file"
        echo "Edit this file and add URLs, then run again."
        return
    fi
    
    echo "🔍 Monitoring $competitor"
    batch_process "$urls_file"
}

# Main menu
show_help() {
    echo "Marketing Intelligence Extractor"
    echo ""
    echo "Usage:"
    echo "  $0 <URL>                     Extract intel from single URL"
    echo "  $0 batch <file>              Process multiple URLs from file"
    echo "  $0 monitor <competitor>      Monitor specific competitor"
    echo "  $0 report                    Generate analysis report"
    echo "  $0 quick <URL>               Quick extract (no analysis)"
    echo ""
    echo "Examples:"
    echo "  $0 https://x.com/user/status/123456"
    echo "  $0 batch urls.txt"
    echo "  $0 monitor john-eldredge"
    echo "  $0 report"
    echo ""
    echo "Your intel files are in: $WORKSPACE"
}

# Process commands
case "$1" in
    "batch")
        batch_process "$2"
        ;;
    "monitor")
        monitor_competitor "$2"
        ;;
    "report")
        create_report
        ;;
    "quick")
        # Use simpler bash extractor for quick results
        "$HOME/.openclaw/workspace/x-substack-intel.sh" "$2"
        ;;
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    *)
        # Assume it's a URL
        python3 "$PYTHON_SCRIPT" "$1"
        ;;
esac