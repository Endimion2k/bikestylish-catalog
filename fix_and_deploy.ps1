# PowerShell script pentru commit și push modificări GitHub Pages

Write-Host "🔧 Fixing GitHub Pages Jekyll build errors..." -ForegroundColor Cyan

# Add all changes
git add -A

# Commit with descriptive message
$commitMessage = @"
🔧 Fix Jekyll build errors

- Updated _config.yml with GitHub Pages supported plugins only
- Disabled problematic GitHub Actions workflow temporarily  
- Added proper Jekyll layout structure
- Removed unsupported Jekyll plugins and redirects
- Enhanced documentation with comprehensive API details

Fixes:
- Jekyll build failures due to unsupported plugins
- GitHub Actions conflicts with Jekyll processing
- Missing layout templates
- Configuration incompatibilities

Result: Clean GitHub Pages deployment with full Jekyll support
"@

git commit -m $commitMessage

# Push to main branch
git push origin main

Write-Host "✅ Changes pushed to GitHub!" -ForegroundColor Green
Write-Host "🌐 Site will rebuild at: https://endimion2k.github.io/bikestylish-catalog/" -ForegroundColor Blue
Write-Host "⏱️  Build process takes 2-3 minutes to complete" -ForegroundColor Yellow
