#!/bin/bash
# Generate competitive intelligence report from all sources

cd ~/.openclaw/workspace/intel

echo "📊 Biblical Man Competitive Intelligence Report"
echo "Generated: $(date)"
echo ""

# Count intel files
total_intel=$(ls -1 *.json 2>/dev/null | wc -l)
echo "Total intel gathered: $total_intel sources"
echo ""

# Top hooks
echo "🎯 Top Hooks Found:"
grep -h '"hook"' *.json 2>/dev/null | cut -d'"' -f4 | sort | uniq -c | sort -nr | head -5
echo ""

# Common Jake triggers
echo "💔 Most Common Jake Triggers:"
grep -h "jake_triggers" *.json 2>/dev/null | grep -oE '"[^"]+"' | grep -v jake_triggers | sort | uniq -c | sort -nr | head -10
echo ""

# Marketing angles
echo "📈 Winning Marketing Angles:"
grep -h "marketing_angle" *.json 2>/dev/null | grep -oE '"[^"]+"' | grep -v marketing_angle | sort | uniq -c | sort -nr
echo ""

# High emotional density content
echo "🔥 High Emotional Density Content (>5%):"
for file in *.json; do
    if [ -f "$file" ]; then
        pain_density=$(grep -o '"pain_density": [0-9.]*' "$file" | cut -d' ' -f2)
        if (( $(echo "$pain_density > 5" | bc -l) )); then
            url=$(grep '"url"' "$file" | head -1 | cut -d'"' -f4)
            echo "  - $url (Pain: ${pain_density}%)"
        fi
    fi
done 2>/dev/null
echo ""

echo "📁 Full intel reports in: $(pwd)"