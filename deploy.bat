@echo off
REM KidQuest Netlify Deployment Script for Windows
REM This script helps prepare and deploy your application to Netlify

echo 🚀 KidQuest Netlify Deployment Script
echo ======================================

REM Check if we're in the right directory
if not exist "frontend\package.json" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd frontend

echo 📦 Installing dependencies...
call npm install

echo 🔍 Checking for environment variables...
if not exist ".env.production" (
    echo ⚠️  Warning: .env.production not found
    echo 📝 Please create .env.production with your backend URL
    echo    Example: VITE_API_BASE_URL=https://your-backend.herokuapp.com
    set /p continue="   Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

echo 🔨 Building the application...
call npm run build

if %errorlevel% equ 0 (
    echo ✅ Build successful!
    echo 📁 Build files are in: frontend\dist\
    echo.
    echo 🌐 Next steps for Netlify deployment:
    echo    1. Push your code to GitHub
    echo    2. Connect your GitHub repo to Netlify
    echo    3. Set build settings:
    echo       - Base directory: frontend/
    echo       - Build command: npm run build
    echo       - Publish directory: frontend/dist/
    echo    4. Set environment variables in Netlify:
    echo       - VITE_API_BASE_URL=your-backend-url
    echo       - VITE_NODE_ENV=production
    echo.
    echo 📖 See NETLIFY_DEPLOYMENT_GUIDE.md for detailed instructions
    
    set /p test="🔍 Test the build locally? (y/n): "
    if /i "%test%"=="y" (
        echo 🌐 Starting preview server...
        call npm run preview
    )
) else (
    echo ❌ Build failed! Please check the errors above.
    pause
    exit /b 1
)

pause
