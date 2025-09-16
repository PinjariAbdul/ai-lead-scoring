@echo off
echo 🚀 Lead Qualification API - Quick Deploy to Heroku
echo ================================================

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Heroku CLI not found. Please install it first:
    echo https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Check if git is initialized
if not exist .git (
    echo 📝 Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit"
)

REM Login to Heroku
echo 🔐 Logging into Heroku...
heroku login

REM Get app name from user
set /p APP_NAME="Enter your Heroku app name (e.g., my-lead-api): "
if "%APP_NAME%"=="" (
    echo ❌ App name cannot be empty
    pause
    exit /b 1
)

REM Create Heroku app
echo 🎯 Creating Heroku app: %APP_NAME%
heroku create %APP_NAME%

REM Generate secret key
echo 🔑 Generating Django secret key...
for /f "delims=" %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set SECRET_KEY=%%i

REM Set environment variables
echo 🔧 Setting environment variables...
heroku config:set DEBUG=False --app %APP_NAME%
heroku config:set SECRET_KEY="%SECRET_KEY%" --app %APP_NAME%
heroku config:set ALLOWED_HOSTS="%APP_NAME%.herokuapp.com" --app %APP_NAME%

REM Ask for OpenAI API key (optional)
set /p OPENAI_KEY="Enter your OpenAI API key (optional, press Enter to skip): "
if not "%OPENAI_KEY%"=="" (
    heroku config:set OPENAI_API_KEY="%OPENAI_KEY%" --app %APP_NAME%
    echo ✅ OpenAI API key set
) else (
    echo ⚠️ OpenAI API key skipped - API will use fallback scoring
)

REM Deploy to Heroku
echo 🚀 Deploying to Heroku...
git add .
git commit -m "Deploy to Heroku" --allow-empty
git push heroku main

REM Run migrations
echo 🗄️ Running database migrations...
heroku run python manage.py migrate --app %APP_NAME%

REM Open the app
echo 🎉 Deployment complete!
echo Your API is available at: https://%APP_NAME%.herokuapp.com/
echo.
echo Opening your app...
heroku open --app %APP_NAME%

REM Test the API
echo 🧪 Testing API...
curl -s https://%APP_NAME%.herokuapp.com/ | echo.

echo.
echo ✅ Deployment successful!
echo 📚 Check the logs: heroku logs --tail --app %APP_NAME%
echo 🔧 Manage app: https://dashboard.heroku.com/apps/%APP_NAME%
pause