# Script to push to GitHub
# Usage: .\push_to_github.ps1 <your-github-username> <repository-name>

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoName
)

$RemoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"

Write-Host "Setting up remote repository..." -ForegroundColor Green
git remote add origin $RemoteUrl 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Remote already exists, updating..." -ForegroundColor Yellow
    git remote set-url origin $RemoteUrl
}

Write-Host "Pushing to GitHub..." -ForegroundColor Green
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: $RemoteUrl" -ForegroundColor Cyan
} else {
    Write-Host "Push failed. Make sure:" -ForegroundColor Red
    Write-Host "1. You've created the repository on GitHub first" -ForegroundColor Yellow
    Write-Host "2. You have the correct permissions" -ForegroundColor Yellow
    Write-Host "3. You're authenticated (use GitHub CLI or SSH keys)" -ForegroundColor Yellow
}

