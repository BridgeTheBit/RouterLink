<#
.SYNOPSIS
    RouterLink GitHub Initial Release and Automation Script
.DESCRIPTION
    Initializes git repository, commits code, adds remote origin,
    pushes main branch (triggering Docker & Android builds),
    and creates release tag v1.0.0 (triggering GitHub Releases).
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$RepoUrl = ""
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   RouterLink - GitHub Publisher & Release Tool   " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed or not found in PATH. Please install Git for Windows."
    exit 1
}

# 2. Get Repository URL if not provided
if ([string]::IsNullOrWhiteSpace($RepoUrl)) {
    Write-Host "`nPlease enter your GitHub Repository URL:" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Gray
    Write-Host "  HTTPS: https://github.com/<your-username>/RouterLink.git" -ForegroundColor Gray
    Write-Host "  SSH:   git@github.com:<your-username>/RouterLink.git" -ForegroundColor Gray
    $RepoUrl = Read-Host "GitHub Repo URL"
}

if ([string]::IsNullOrWhiteSpace($RepoUrl)) {
    Write-Error "Repository URL cannot be empty."
    exit 1
}

# 3. Initialize Git if needed
if (-not (Test-Path ".git")) {
    Write-Host "`n[1/6] Initializing local Git repository (main branch)..." -ForegroundColor Green
    git init -b main
} else {
    Write-Host "`n[1/6] Git repository already initialized. Ensuring 'main' branch..." -ForegroundColor Green
    git checkout -B main
}

# 4. Stage all files
Write-Host "`n[2/6] Staging files (honoring .gitignore)..." -ForegroundColor Green
git add .

# 5. Check git status and commit
$status = git status --porcelain
if ($status) {
    Write-Host "`n[3/6] Committing initial release files..." -ForegroundColor Green
    git commit -m "feat: initial production release of RouterLink v1.0.0 (FastAPI Backend, Embedded WebUI, Android App, MikroTik ROS7 scripts)"
} else {
    Write-Host "`n[3/6] Working directory clean, nothing new to commit." -ForegroundColor Yellow
}

# 6. Configure remote origin
Write-Host "`n[4/6] Setting remote origin to: $RepoUrl" -ForegroundColor Green
$remotes = git remote
if ($remotes -contains "origin") {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

# 7. Push main branch
Write-Host "`n[5/6] Pushing 'main' branch to GitHub..." -ForegroundColor Green
Write-Host "This will automatically trigger GitHub Actions:" -ForegroundColor Cyan
Write-Host "  -> Multi-Arch Docker Build (linux/amd64, linux/arm64) to GHCR" -ForegroundColor Cyan
Write-Host "  -> Android APK compilation (Debug & Release)" -ForegroundColor Cyan
git push -u origin main

# 8. Create and Push Tag v1.0.0
Write-Host "`n[6/6] Creating release tag v1.0.0..." -ForegroundColor Green
$existingTags = git tag
if ($existingTags -notcontains "v1.0.0") {
    git tag -a v1.0.0 -m "Release v1.0.0: Full RouterLink VPN delivery system for MikroTik ROS7"
    Write-Host "Pushing tag v1.0.0 to GitHub..." -ForegroundColor Green
    git push origin v1.0.0
} else {
    Write-Host "Tag v1.0.0 already exists locally. Pushing to remote..." -ForegroundColor Yellow
    git push origin v1.0.0
}

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "   SUCCESS! Project pushed to GitHub successfully! " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "`nWhat happens next:" -ForegroundColor Cyan
Write-Host "1. Visit your repository: $RepoUrl"
Write-Host "2. Go to the 'Actions' tab to watch real-time CI/CD builds:"
Write-Host "   - Multi-arch Docker container (Alpine 3.20) building & publishing to GHCR"
Write-Host "   - Android APK building (assembleRelease & assembleDebug)"
Write-Host "3. Go to 'Releases' (v1.0.0) once complete to download:"
Write-Host "   - RouterLink-Release.apk"
Write-Host "   - routerlink-mikrotik-scripts.zip"
Write-Host "   - install.rsc`n"
