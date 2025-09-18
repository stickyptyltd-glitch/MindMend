
#!/bin/bash
# Emergency deployment script

echo "🚨 MindMend Emergency Deployment"

# Option 1: Deploy to Netlify using curl
if command -v curl &> /dev/null; then
    echo "📤 Uploading to Netlify..."
    # zip -r site.zip simple_landing.html
    # curl -H "Content-Type: application/zip" -H "Authorization: Bearer YOUR_TOKEN" --data-binary "@site.zip" https://api.netlify.com/api/v1/sites
fi

# Option 2: Use GitHub Pages
if [ -d ".git" ]; then
    echo "📤 Deploying to GitHub Pages..."
    git add simple_landing.html
    git commit -m "Emergency landing page deployment"
    git push origin main
fi

echo "✅ Emergency deployment initiated"
    