# 🚀 Quick Deployment Guide

Choose your preferred deployment platform and follow the steps below:

## 🟣 **Heroku (Recommended - Easy)**

### Step 1: Prerequisites
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
heroku --version
git --version
```

### Step 2: Login and Create App
```bash
heroku login
heroku create your-lead-api-name
```

### Step 3: Set Environment Variables
```bash
# Generate a secret key first
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set the environment variables (replace with your values)
heroku config:set DEBUG=False
heroku config:set SECRET_KEY="your-generated-secret-key-here"
heroku config:set ALLOWED_HOSTS="your-lead-api-name.herokuapp.com"
heroku config:set OPENAI_API_KEY="your-openai-api-key-here"
```

### Step 4: Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Step 5: Setup Database
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser  # Optional
```

### Step 6: Test Your API
```bash
heroku open
# Or visit: https://your-lead-api-name.herokuapp.com/
```

**🎉 Your API is live!** Test it with:
```bash
curl https://your-lead-api-name.herokuapp.com/
```

---

## 🚂 **Railway (Modern & Fast)**

### Step 1: Connect Repository
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your repository

### Step 2: Environment Variables
Add these in Railway dashboard → Variables:
```
DEBUG=False
SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=*
OPENAI_API_KEY=your-openai-api-key-here
PORT=8000
```

### Step 3: Auto-Deploy
- Railway auto-deploys on every push to main
- Your API URL will be generated automatically

---

## 🎨 **Render (Free Tier Available)**

### Step 1: Create Web Service
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your GitHub repo

### Step 2: Configure
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn lead_qualification_api.wsgi:application`

### Step 3: Environment Variables
```
DEBUG=False
SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=*
OPENAI_API_KEY=your-openai-api-key-here
PYTHON_VERSION=3.10.0
```

---

## 🐳 **Docker (Any Cloud Provider)**

### Step 1: Build and Run Locally
```bash
# Build image
docker build -t lead-qualification-api .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e ALLOWED_HOSTS=localhost \
  -e OPENAI_API_KEY=your-openai-key \
  lead-qualification-api
```

### Step 2: Deploy to Cloud
- **AWS:** Push to ECR and deploy with ECS/Fargate
- **Google Cloud:** Push to Container Registry and deploy with Cloud Run
- **Azure:** Push to Container Registry and deploy with Container Instances

---

## 🔧 **Required Environment Variables**

For any deployment platform, you need these:

| Variable | Value | Example |
|----------|-------|---------|
| `DEBUG` | `False` | `False` |
| `SECRET_KEY` | Generated key | `django-insecure-xxx...` |
| `ALLOWED_HOSTS` | Your domain | `your-app.herokuapp.com` |
| `OPENAI_API_KEY` | Your OpenAI key | `sk-xxx...` (optional) |

### Generate Secret Key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## ✅ **Post-Deployment Checklist**

1. **Test API Status**
   ```bash
   curl https://your-domain.com/
   ```

2. **Test Offer Creation**
   ```bash
   curl -X POST https://your-domain.com/offer/ \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","value_props":["test"],"ideal_use_cases":["test"]}'
   ```

3. **Check Logs** (if issues)
   - **Heroku:** `heroku logs --tail`
   - **Railway/Render:** Check dashboard logs

---

## 🚨 **Common Issues & Solutions**

### Issue: "DisallowedHost" Error
**Solution:** Add your domain to ALLOWED_HOSTS
```bash
heroku config:set ALLOWED_HOSTS="your-app.herokuapp.com,your-custom-domain.com"
```

### Issue: Static files not loading
**Solution:** Already configured with WhiteNoise, should work automatically

### Issue: Database errors
**Solution:** Run migrations
```bash
heroku run python manage.py migrate
```

### Issue: OpenAI errors
**Solution:** API works without OpenAI (uses fallback scoring)

---

## 🎯 **Recommended: Start with Heroku**

Heroku is the easiest for beginners:
1. Good documentation
2. Easy CLI
3. Auto-scaling
4. Add-ons available
5. Free tier (with limitations)

**Quick Heroku Deploy:**
```bash
heroku create your-api-name
heroku config:set DEBUG=False SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" ALLOWED_HOSTS="your-api-name.herokuapp.com"
git push heroku main
heroku run python manage.py migrate
heroku open
```

**🎉 That's it! Your Lead Qualification API is deployed and ready to use!**