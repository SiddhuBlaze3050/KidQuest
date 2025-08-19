#!/bin/bash

# KidQuest Netlify Deployment Script
# This script helps prepare and deploy your application to Netlify

echo "🚀 KidQuest Netlify Deployment Script"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "📦 Installing dependencies..."
npm install

echo "🔍 Checking for environment variables..."
if [ ! -f ".env.production" ]; then
    echo "⚠️  Warning: .env.production not found"
    echo "📝 Please create .env.production with your backend URL"
    echo "   Example: VITE_API_BASE_URL=https://your-backend.herokuapp.com"
    read -p "   Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔨 Building the application..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Build files are in: frontend/dist/"
    echo ""
    echo "🌐 Next steps for Netlify deployment:"
    echo "   1. Push your code to GitHub"
    echo "   2. Connect your GitHub repo to Netlify"
    echo "   3. Set build settings:"
    echo "      - Base directory: frontend/"
    echo "      - Build command: npm run build"
    echo "      - Publish directory: frontend/dist/"
    echo "   4. Set environment variables in Netlify:"
    echo "      - VITE_API_BASE_URL=your-backend-url"
    echo "      - VITE_NODE_ENV=production"
    echo ""
    echo "📖 See NETLIFY_DEPLOYMENT_GUIDE.md for detailed instructions"
    
    # Optional: Test the build locally
    read -p "🔍 Test the build locally? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🌐 Starting preview server..."
        npm run preview
    fi
else
    echo "❌ Build failed! Please check the errors above."
    exit 1
fi
