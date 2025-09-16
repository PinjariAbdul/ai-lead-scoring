# Lead Qualification API - Deployment Guide

This guide covers multiple deployment options for the Lead Qualification API.

## 🚀 Quick Deploy Options

### Option 1: Heroku (Recommended for beginners)
### Option 2: Railway (Modern, easy)
### Option 3: Render (Free tier available)
### Option 4: DigitalOcean App Platform
### Option 5: Docker (Any platform)

---

## 🟣 **Heroku Deployment**

### Prerequisites
- Heroku CLI installed
- Git repository initialized
- Heroku account

### Steps

1. **Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku App**
```bash
heroku create your-lead-qualification-api
```

4. **Set Environment Variables**
```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set OPENAI_API_KEY=your-openai-api-key
```

5. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

6. **Run Migrations**
```bash
heroku run python manage.py migrate
```

7. **Open Your App**
```bash
heroku open
```

**Your API will be available at:** `https://your-app-name.herokuapp.com/`

---

## 🚂 **Railway Deployment**

### Steps

1. **Connect Repository**
   - Go to [railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository

2. **Environment Variables**
   Add these in Railway dashboard:
   ```
   DEBUG=False
   SECRET_KEY=your-super-secret-key-here
   ALLOWED_HOSTS=*
   OPENAI_API_KEY=your-openai-api-key
   PORT=8000
   ```

3. **Deploy**
   - Railway auto-deploys on push
   - Your app will be available at the generated URL

---

## 🎨 **Render Deployment**

### Steps

1. **Connect Repository**
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repository

2. **Configure Build & Deploy**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn lead_qualification_api.wsgi:application`

3. **Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=your-super-secret-key-here
   ALLOWED_HOSTS=*
   OPENAI_API_KEY=your-openai-api-key
   PYTHON_VERSION=3.10.0
   ```

4. **Deploy**
   - Render auto-deploys on push
   - Free tier available!

---

## 🌊 **DigitalOcean App Platform**

### Steps

1. **Create App**
   - Go to DigitalOcean App Platform
   - Create app from GitHub repository

2. **Configure**
   - **Source:** Your GitHub repo
   - **Type:** Web Service
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `gunicorn --worker-tmp-dir /dev/shm lead_qualification_api.wsgi`

3. **Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=your-super-secret-key-here
   ALLOWED_HOSTS=*
   OPENAI_API_KEY=your-openai-api-key
   ```

---

## 🐳 **Docker Deployment**

### Local Docker

1. **Build Image**
```bash
docker build -t lead-qualification-api .
```

2. **Run Container**
```bash
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e OPENAI_API_KEY=your-openai-key \
  lead-qualification-api
```

### Docker Compose

```bash
docker-compose up -d
```

---

## 🔧 **Environment Variables Required**

For all deployments, set these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEBUG` | Yes | `False` | Django debug mode |
| `SECRET_KEY` | Yes | - | Django secret key |
| `ALLOWED_HOSTS` | Yes | `*` | Allowed hostnames |
| `OPENAI_API_KEY` | No | - | OpenAI API key (optional) |
| `CORS_ALLOWED_ORIGINS` | No | `*` | CORS origins |
| `MAX_FILE_SIZE` | No | `10485760` | Max upload size |
| `MAX_LEADS_PER_UPLOAD` | No | `1000` | Max leads per CSV |

---

## 🔐 **Security Notes**

1. **Generate Strong Secret Key**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Set ALLOWED_HOSTS properly**
   - For production: `your-domain.com,www.your-domain.com`
   - For development: `localhost,127.0.0.1`

3. **HTTPS Only in Production**
   - Most platforms provide HTTPS automatically
   - Update CORS settings for production domains

---

## 📊 **Post-Deployment Testing**

Test your deployed API:

```bash
# Replace YOUR_DOMAIN with your actual domain
curl https://YOUR_DOMAIN.herokuapp.com/

# Create offer
curl -X POST https://YOUR_DOMAIN.herokuapp.com/offer/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Offer","value_props":["test"],"ideal_use_cases":["test"]}'
```

---

## 🐛 **Troubleshooting**

### Common Issues

1. **Static Files Not Loading**
   - Run: `python manage.py collectstatic`
   - Check STATIC_ROOT in settings

2. **Database Issues**
   - Run migrations: `python manage.py migrate`
   - For Heroku: `heroku run python manage.py migrate`

3. **Environment Variables**
   - Check all required variables are set
   - Use platform-specific syntax

4. **OpenAI API Errors**
   - API works without OpenAI key (uses fallback)
   - Verify API key format if using OpenAI

### Logs

- **Heroku:** `heroku logs --tail`
- **Railway:** Check logs in dashboard
- **Render:** Check logs in dashboard
- **Docker:** `docker logs <container_id>`

---

## 🎯 **Recommended Deployment Flow**

1. **Development:** Local Django server
2. **Staging:** Railway or Render (free tier)
3. **Production:** Heroku, DigitalOcean, or AWS

---

## 📝 **Production Checklist**

- [ ] Environment variables configured
- [ ] ALLOWED_HOSTS set correctly
- [ ] DEBUG=False
- [ ] Strong SECRET_KEY generated
- [ ] Database migrations run
- [ ] Static files collected
- [ ] OpenAI API key added (optional)
- [ ] CORS settings configured
- [ ] API endpoints tested
- [ ] Error monitoring setup (optional)

---

Choose the platform that best fits your needs and follow the specific steps above! 🚀