#!/bin/bash
# YouTube Transcript Fetcher
# Usage: ./youtube-transcript.sh VIDEO_ID_OR_URL

# Extract video ID from URL or use directly
VIDEO_INPUT="$1"
VIDEO_ID=""

# Extract video ID from various YouTube URL formats
if [[ "$VIDEO_INPUT" =~ youtube\.com/watch\?v=([^&]+) ]]; then
    VIDEO_ID="${BASH_REMATCH[1]}"
elif [[ "$VIDEO_INPUT" =~ youtu\.be/([^?]+) ]]; then
    VIDEO_ID="${BASH_REMATCH[1]}"
elif [[ "$VIDEO_INPUT" =~ youtube\.com/shorts/([^?]+) ]]; then
    VIDEO_ID="${BASH_REMATCH[1]}"
elif [[ "$VIDEO_INPUT" =~ ^[a-zA-Z0-9_-]{11}$ ]]; then
    VIDEO_ID="$VIDEO_INPUT"
else
    echo "Error: Invalid YouTube URL or video ID"
    exit 1
fi

echo "Fetching transcript for video ID: $VIDEO_ID"

# Create transcripts directory if it doesn't exist
mkdir -p ~/.openclaw/workspace/transcripts

# Fetch the transcript
cd ~/.openclaw/workspace/mcp-server-youtube-transcript && node --input-type=module -e "
import { getSubtitles } from './dist/youtube-fetcher.js';
const result = await getSubtitles({ videoID: '$VIDEO_ID', lang: 'en' });
console.log(JSON.stringify(result, null, 2));
" > /tmp/yt-transcript-$VIDEO_ID.json

# Check if successful
if [ $? -eq 0 ] && [ -s /tmp/yt-transcript-$VIDEO_ID.json ]; then
    echo "Transcript fetched successfully!"
    echo "Saved to: /tmp/yt-transcript-$VIDEO_ID.json"
    
    # Extract metadata
    TITLE=$(jq -r '.metadata.title // "Unknown Title"' /tmp/yt-transcript-$VIDEO_ID.json 2>/dev/null)
    echo "Video Title: $TITLE"
else
    echo "Error: Failed to fetch transcript"
    exit 1
fi