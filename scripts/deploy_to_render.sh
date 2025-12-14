#!/bin/bash
# Helper script to deploy to Render
# This automates git push which triggers Render auto-deployment

set -e

echo "=========================================="
echo "White Agent - Deploy to Render"
echo "=========================================="
echo ""

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    echo "Initialize with: git init"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "You have uncommitted changes. Stage them first."
    echo ""
    git status --short
    echo ""
    read -p "Stage all changes and commit? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
    else
        echo "Aborting deployment."
        exit 1
    fi
fi

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "No git remote configured."
    echo ""
    echo "Add remote with:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
    exit 1
fi

echo "Pushing to GitHub (this will trigger Render deployment)..."
echo ""

git push origin main

echo ""
echo "=========================================="
echo "✓ Code pushed to GitHub"
echo "=========================================="
echo ""
echo "Render will automatically deploy your changes."
echo "Monitor deployment at: https://dashboard.render.com"
echo ""
echo "View logs with:"
echo "  - Render dashboard → Your service → Logs tab"
echo ""
