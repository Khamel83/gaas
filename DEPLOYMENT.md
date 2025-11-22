# GAAS Deployment Guide

This document explains how to deploy and manage the GAAS (Gami As A Service) website.

## Current Setup

**Public Site:** `https://gaas.zoheri.com/`

### DNS Configuration
The site uses a custom domain with these DNS records:
```
Host: @     Type: A    Data: 185.199.108.153
Host: @     Type: A    Data: 185.199.109.153
Host: @     Type: A    Data: 185.199.110.153
Host: @     Type: A    Data: 185.199.111.153
Host: gaas  Type: CNAME    Data: khamel83.github.io
```

### GitHub Pages Configuration
- **Repository:** `Khamel83/gaas`
- **Custom Domain:** `gaas.zoheri.com`
- **Source:** Deploy from `main` branch
- **HTTPS:** Enabled
- **Workflow:** Custom GitHub Actions (`.github/workflows/deploy-pages.yml`)

## How to Update the Site

### 1. Make Changes
```bash
# Update GAAS data
python src/gaas.py

# Or manually update files in the repository
```

### 2. Push to GitHub
```bash
git add .
git commit -m "Update GAAS results"
git push origin main
```

### 3. Automatic Deployment
- GitHub Actions will automatically deploy changes to `https://gaas.zoheri.com/`
- Deployment typically takes 1-2 minutes
- Check Actions tab in GitHub for deployment status

## Important Files

### Site Structure
```
/
├── index.html              # Main dashboard
├── index.json              # Site metadata
├── nfl/                    # NFL data
│   ├── rb_latest.html      # Running backs page
│   ├── rb_latest.json      # Running backs data
│   └── ...                 # Other NFL positions
├── nba/                    # NBA data
├── mlb/                    # MLB data
├── f1/                     # F1 data
├── champions_league/       # Champions League data
├── nhl/                    # NHL data
├── .nojekyll               # Tells GitHub to serve static files
└── .github/workflows/
    └── deploy-pages.yml    # Deployment workflow
```

### Key Configuration Files

**`.nojekyll`** - Critical file that tells GitHub Pages to serve files as static content instead of processing with Jekyll.

**`.github/workflows/deploy-pages.yml`** - GitHub Actions workflow that:
- Runs on pushes to `main` branch
- Excludes problematic files (source code, logs, etc.)
- Deploys only the static web content to GitHub Pages

## Changing Domain Configuration

### To Switch Domain:
1. **DNS:** Update your domain's DNS records to point to GitHub Pages:
   ```
   Host: @     Type: A    Data: 185.199.108.153
   Host: @     Type: A    Data: 185.199.109.153
   Host: @     Type: A    Data: 185.199.110.153
   Host: @     Type: A    Data: 185.199.111.153
   ```

2. **GitHub Pages:** Go to repository Settings → Pages:
   - Remove current custom domain
   - Add new custom domain
   - Wait for DNS verification
   - Enable HTTPS enforcement

### To Use GitHub Pages Domain:
1. **GitHub Pages:** Go to Settings → Pages:
   - Remove custom domain
   - Site will be available at `https://khamel83.github.io/gaas/`

## Troubleshooting

### Common Issues:

**"Site not found" error:**
- Check that `index.html` exists in repository root
- Ensure GitHub Pages is enabled in repository settings
- Verify custom domain DNS records are correct

**GitHub Actions deployment fails:**
- Check Actions tab for error details
- Ensure `.nojekyll` file exists in repository root
- Verify workflow file permissions are correct

**Custom domain not working:**
- Check DNS propagation (can take 24-48 hours)
- Verify DNS records match GitHub Pages requirements
- Check domain status in GitHub Pages settings

### Manual Deployment Commands:
```bash
# Force redeployment
git commit --allow-empty -m "Trigger redeploy"
git push origin main

# Check deployment status
gh run list --repo Khamel83/gaas --limit 3
```

## Content Management

### Adding New Sports:
1. Generate data files in `data/` directory
2. Create JSON files in appropriate sport directory
3. Update `index.html` to link to new sport
4. Push changes to trigger deployment

### Updating Website Design:
1. Modify HTML/CSS files directly
2. Test locally before pushing
3. GitHub Actions will deploy changes automatically

## Performance Considerations

- **JSON files** should be kept reasonably sized for fast loading
- **Images** should be optimized for web
- **GitHub Pages** has bandwidth limits (100GB/month for free tier)
- **Deployment** happens automatically, no manual steps needed

## Security Notes

- No API keys or sensitive data should be committed to repository
- HTTPS is enforced for secure connections
- GitHub Actions has minimal permissions needed for deployment
- Custom domain configuration should include HTTPS certificates

This deployment setup provides automatic, reliable hosting for the GAAS website with minimal maintenance required.