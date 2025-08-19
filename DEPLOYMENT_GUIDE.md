# KidQuest Backend - Render Deployment Guide

This guide will help you deploy the KidQuest Flask backend to Render.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Environment Variables**: Prepare your API keys

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Push to GitHub**: Make sure all your code is committed and pushed
2. **Verify Files**: Ensure these files are in your repository root:
   - `requirements.txt` ✅ (Updated with all dependencies)
   - `Procfile` ✅ (Created for Render)
   - `render.yaml` ✅ (Render configuration)

### Step 2: Create Web Service on Render

1. **Login to Render**: Go to [render.com](https://render.com) and sign in
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect Repository**:

   - Choose "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your KidQuest repository

4. **Configure Service**:
   ```
   Name: kidquest-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd backend && gunicorn --bind 0.0.0.0:$PORT app:app
   ```

### Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:

#### Required Variables:

```bash
SECRET_KEY=your-secret-key-here-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-here-32-chars
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
```

#### API Keys (Already in config.py, but can be overridden):

```bash
GROQ_API_KEY=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
OPENROUTER_API_KEY=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
OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
```

### Step 4: Database Setup

#### Option A: PostgreSQL on Render (Recommended)

1. **Create Database**: In Render dashboard, click "New +" → "PostgreSQL"
2. **Configure**:
   ```
   Name: kidquest-db
   Database: kidquest
   User: kidquest_user
   ```
3. **Copy Connection String**: Use the "External Database URL" in your `DATABASE_URL` environment variable

#### Option B: External Database

- Use any PostgreSQL provider (Supabase, Neon, etc.)
- Update `DATABASE_URL` with your connection string

### Step 5: Deploy

1. **Auto-Deploy**: Render will automatically build and deploy
2. **Monitor Logs**: Check the deployment logs for any issues
3. **Test Endpoints**: Once deployed, test your API endpoints

## 🔧 Configuration Files Explained

### `requirements.txt`

Contains all Python dependencies with specific versions for stability:

- Flask and related packages
- Database drivers (SQLAlchemy)
- JWT authentication
- AI/LLM integration (OpenAI)
- Production server (Gunicorn)

### `Procfile`

Tells Render how to run your application:

```
web: cd backend && gunicorn --bind 0.0.0.0:$PORT app:app
```

### `render.yaml` (Optional)

Infrastructure as Code configuration for automated deployment.

## 🌐 Frontend Configuration

After backend deployment, update your frontend environment variables:

### Update `.env.production`:

```bash
VITE_API_BASE_URL=https://your-backend-service.onrender.com
VITE_NODE_ENV=production
```

### Rebuild Frontend:

```bash
cd frontend
npm run build
```

## 🔍 Testing Your Deployment

### 1. Health Check

Visit: `https://your-backend-service.onrender.com/`

### 2. API Endpoints

Test key endpoints:

- `GET /api/auth/verify`
- `POST /api/auth/login`
- `GET /api/admin/dashboard-stats`

### 3. Database Connection

Check if database tables are created properly.

## 🐛 Common Issues & Solutions

### Issue 1: Build Fails

**Solution**: Check `requirements.txt` for version conflicts

```bash
# If needed, you can pin to specific working versions
Flask==3.0.3
SQLAlchemy==2.0.23
```

### Issue 2: Database Connection Error

**Solution**: Verify `DATABASE_URL` format:

```
postgresql://username:password@host:port/database_name
```

### Issue 3: CORS Issues

**Solution**: Update CORS origins in `app.py`:

```python
CORS(app, origins=["https://your-frontend-url.netlify.app", "*"])
```

### Issue 4: Environment Variables Not Loading

**Solution**: Check Render dashboard environment variables section

## 🔄 Auto-Deploy Setup

1. **Connect GitHub**: Link your repository to Render
2. **Auto-Deploy**: Enable auto-deploy on push to main branch
3. **Branch**: Set deployment branch (usually `main` or `master`)

## 📊 Monitoring

### Render Dashboard:

- Monitor CPU and memory usage
- Check deployment logs
- View service metrics

### Health Checks:

Render automatically monitors your service health.

## 💰 Pricing

### Free Tier Limitations:

- Service spins down after 15 minutes of inactivity
- 750 hours/month limit
- Slower cold starts

### Paid Plans:

- Always-on services
- Better performance
- More resources

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Render provides SSL certificates automatically
3. **Database Security**: Use strong passwords and connection strings
4. **API Keys**: Rotate keys regularly

## 🚀 Going Live

1. **Custom Domain**: Add your custom domain in Render dashboard
2. **SSL Certificate**: Automatic with custom domains
3. **Monitoring**: Set up alerts for downtime
4. **Backups**: Regular database backups

## 📝 Next Steps

After successful deployment:

1. **Update Frontend**: Point frontend to your new backend URL
2. **Test All Features**: Verify all functionality works
3. **Monitor Performance**: Watch for any issues
4. **Set Up Monitoring**: Use Render's built-in monitoring or external tools

## 🆘 Support

If you encounter issues:

1. **Check Render Logs**: Most issues are visible in deployment logs
2. **Render Documentation**: [render.com/docs](https://render.com/docs)
3. **Community**: Render community forums
4. **Support**: Render support team (paid plans)

---

🎉 **Congratulations!** Your KidQuest backend should now be successfully deployed on Render!
