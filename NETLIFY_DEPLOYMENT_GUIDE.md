# KidQuest - Netlify Deployment Guide

This guide will help you deploy the KidQuest frontend application to Netlify.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **GitHub Repository**: Your code should be pushed to a GitHub repository
2. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
3. **Backend Deployed**: Your Flask backend should be deployed (Heroku, Railway, etc.)

## 🚀 Step-by-Step Deployment Process

### Step 1: Prepare Your Backend

First, deploy your Flask backend to a cloud service:

**Option A: Deploy to Heroku**

1. Create a Heroku account
2. Install Heroku CLI
3. Deploy your backend folder to Heroku
4. Note your backend URL (e.g., `https://your-app.herokuapp.com`)

**Option B: Deploy to Railway**

1. Create a Railway account
2. Connect your GitHub repo
3. Deploy the backend folder
4. Note your backend URL

### Step 2: Update Environment Variables

1. **Update the production environment file:**

   ```bash
   # Edit frontend/.env.production
   VITE_API_BASE_URL=https://your-actual-backend-url.herokuapp.com
   VITE_NODE_ENV=production
   ```

2. **Test the build locally:**
   ```bash
   cd frontend
   npm run build
   npm run preview
   ```

### Step 3: Deploy to Netlify

#### Method 1: GitHub Integration (Recommended)

1. **Push your code to GitHub:**

   ```bash
   git add .
   git commit -m "Prepare for Netlify deployment"
   git push origin main
   ```

2. **Connect to Netlify:**

   - Log in to [Netlify](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Choose "GitHub" and authorize access
   - Select your repository

3. **Configure Build Settings:**

   - **Base directory**: `frontend/`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist/`
   - **Node version**: `18` (set in Environment variables)

4. **Set Environment Variables:**

   - Go to Site settings → Environment variables
   - Add: `VITE_API_BASE_URL` = `https://your-backend-url.herokuapp.com`
   - Add: `VITE_NODE_ENV` = `production`

5. **Deploy:**
   - Click "Deploy site"
   - Wait for the build to complete
   - Your site will be available at a Netlify URL

#### Method 2: Manual Upload

1. **Build the project locally:**

   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Upload to Netlify:**
   - Go to [Netlify](https://app.netlify.com)
   - Drag and drop the `frontend/dist/` folder to the deploy area

### Step 4: Configure Custom Domain (Optional)

1. **In Netlify Dashboard:**
   - Go to Site settings → Domain management
   - Add your custom domain
   - Configure DNS settings as instructed

## ⚙️ Configuration Files Explained

### `netlify.toml`

```toml
[build]
  base = "frontend/"
  publish = "frontend/dist/"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

This file:

- Sets the build directory and command
- Configures SPA redirects for Vue Router
- Sets Node.js version
- Adds security headers

### Environment Variables

The app uses these environment variables:

- `VITE_API_BASE_URL`: Your backend API URL
- `VITE_NODE_ENV`: Environment mode (production/development)

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails:**

   - Check Node.js version (should be 18+)
   - Ensure all dependencies are installed
   - Check for syntax errors in code

2. **API Calls Fail:**

   - Verify `VITE_API_BASE_URL` is correct
   - Check CORS settings in your backend
   - Ensure backend is deployed and accessible

3. **Routes Don't Work:**

   - Ensure `netlify.toml` has the redirect rule
   - Check Vue Router configuration

4. **Environment Variables Not Working:**
   - Variables must start with `VITE_`
   - Set them in Netlify dashboard, not just in files
   - Rebuild after changing environment variables

### Debugging Steps:

1. **Check Build Logs:**

   - Go to Deploys tab in Netlify
   - Click on failed deploy to see logs

2. **Test Locally:**

   ```bash
   cd frontend
   npm run build
   npm run preview
   ```

3. **Check Network Tab:**
   - Open browser dev tools
   - Check if API calls are going to correct URLs

## 🎯 Post-Deployment Checklist

- [ ] Site loads without errors
- [ ] All routes work (test navigation)
- [ ] API calls reach the backend successfully
- [ ] Authentication works
- [ ] All dashboard features function correctly
- [ ] Mobile responsiveness is maintained
- [ ] Performance is acceptable

## 🔄 Updating Your Deployment

When you make changes:

1. **Push to GitHub:**

   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. **Auto-deploy:**
   - Netlify will automatically rebuild and deploy
   - Check the Deploys tab for status

## 📊 Performance Optimization

For better performance:

1. **Enable Build Optimizations:**

   - Netlify automatically minifies assets
   - Gzip compression is enabled by default

2. **Monitor Performance:**
   - Use Netlify Analytics
   - Check Lighthouse scores
   - Monitor Core Web Vitals

## 🔐 Security Considerations

- Environment variables are secure in Netlify
- HTTPS is enabled by default
- Security headers are configured in `netlify.toml`
- Ensure your backend has proper CORS settings

## 📞 Support

If you encounter issues:

1. Check [Netlify Documentation](https://docs.netlify.com)
2. Review build logs in Netlify dashboard
3. Test your build locally first
4. Check that your backend is properly deployed and accessible

---

## 🎉 Success!

Once deployed, your KidQuest application will be available at your Netlify URL, and users can access all the features including:

- User authentication and role-based access
- Child, Parent, Teacher, and Admin dashboards
- Educational modules and activities
- Real-time chat and notifications
- Progress tracking and analytics

Remember to update your backend CORS settings to allow requests from your Netlify domain!
