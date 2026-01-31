#!/bin/bash

# Script to push OpenClaw tools to GitHub

echo "🚀 GitHub Push Script for OpenClaw Tools"
echo "========================================"
echo ""
echo "This will create a new private repo and push your tools."
echo ""
echo "First, you need a GitHub Personal Access Token:"
echo "1. Go to: https://github.com/settings/tokens/new"
echo "2. Give it a name like 'OpenClaw Push'"
echo "3. Select scopes:"
echo "   ✓ repo (all)"
echo "4. Generate token and copy it"
echo ""
echo -n "Paste your GitHub token here: "
read -s GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Configure git to use the token
cd ~/.openclaw/workspace

echo "Setting up GitHub authentication..."
export GH_TOKEN=$GITHUB_TOKEN

# Create the repo
echo "Creating private repository on GitHub..."
gh repo create biblicalman1611/openclaw-tools --private --description "OpenClaw tools and scripts for content intelligence" --source=. --push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Repository created and pushed to:"
    echo "   https://github.com/biblicalman1611/openclaw-tools"
    echo ""
    echo "Share this with Claude to fix issues:"
    echo "   'Fix the TinyFish scraper in github.com/biblicalman1611/openclaw-tools'"
    echo ""
    echo "⚠️  Remember: This repo is PRIVATE. Only you can see it."
else
    echo ""
    echo "❌ Something went wrong. Common issues:"
    echo "   - Token doesn't have 'repo' scope"
    echo "   - Repository name already exists"
    echo "   - Network issues"
fi