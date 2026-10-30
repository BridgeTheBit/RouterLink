#!/usr/bin/env bash
# ==============================================================================
# RouterLink GitHub Initial Release & Automation Script (Bash)
# ==============================================================================

set -e

echo "=================================================="
echo "   RouterLink - GitHub Publisher & Release Tool   "
echo "=================================================="

# Check git
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git."
    exit 1
fi

REPO_URL="$1"

if [ -z "$REPO_URL" ]; then
    echo ""
    echo "Please enter your GitHub Repository URL:"
    echo "  HTTPS: https://github.com/<your-username>/RouterLink.git"
    echo "  SSH:   git@github.com:<your-username>/RouterLink.git"
    read -p "GitHub Repo URL: " REPO_URL
fi

if [ -z "$REPO_URL" ]; then
    echo "Error: Repository URL cannot be empty."
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "[1/6] Initializing local Git repository (main branch)..."
    git init -b main
else
    echo "[1/6] Git repository already initialized. Ensuring 'main' branch..."
    git checkout -B main
fi

# Stage files
echo "[2/6] Staging files..."
git add .

# Commit
if [ -n "$(git status --porcelain)" ]; then
    echo "[3/6] Committing initial release files..."
    git commit -m "feat: initial production release of RouterLink v1.0.0 (FastAPI Backend, Embedded WebUI, Android App, MikroTik ROS7 scripts)"
else
    echo "[3/6] Working tree clean, nothing new to commit."
fi

# Configure remote
echo "[4/6] Setting remote origin to: $REPO_URL"
if git remote | grep -q "origin"; then
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

# Push main
echo "[5/6] Pushing 'main' branch to GitHub..."
echo "This triggers automated GitHub Actions:"
echo "  -> Multi-Arch Docker Build (linux/amd64, linux/arm64) to GHCR"
echo "  -> Android APK compilation (Debug & Release)"
git push -u origin main

# Create and push tag
echo "[6/6] Creating release tag v1.0.0..."
if ! git tag | grep -q "^v1.0.0$"; then
    git tag -a v1.0.0 -m "Release v1.0.0: Full RouterLink VPN delivery system for MikroTik ROS7"
fi

echo "Pushing tag v1.0.0 to GitHub..."
git push origin v1.0.0

echo "=================================================="
echo "   SUCCESS! Project pushed to GitHub successfully! "
echo "=================================================="
echo ""
echo "Next Steps:"
echo "1. Visit your repository: $REPO_URL"
echo "2. Check the 'Actions' tab to see Docker and Android APK builds in progress."
echo "3. Once finished, visit 'Releases' to download RouterLink APK and scripts!"

