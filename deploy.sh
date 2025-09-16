#!/bin/bash

# Production deployment script
set -e

echo "🚀 Lead Qualification API - Production Deployment"
echo "=================================================="

# Check if environment variables are set
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY environment variable is not set"
    exit 1
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "❌ ALLOWED_HOSTS environment variable is not set"
    exit 1
fi

echo "✅ Environment variables checked"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist (optional)
echo "👤 Creating superuser (optional)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'change_this_password')
    print('Superuser created: admin/change_this_password')
else:
    print('Superuser already exists')
" 2>/dev/null || echo "Superuser creation skipped"

# Run tests (optional)
if [ "$RUN_TESTS" = "true" ]; then
    echo "🧪 Running tests..."
    python manage.py test
fi

# Start the application
echo "🎯 Starting application..."
if [ "$DEPLOYMENT_TYPE" = "production" ]; then
    echo "Starting with Gunicorn..."
    gunicorn lead_qualification_api.wsgi:application \
        --bind 0.0.0.0:${PORT:-8000} \
        --workers ${WORKERS:-2} \
        --timeout 60 \
        --log-level info \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting Django development server..."
    python manage.py runserver 0.0.0.0:${PORT:-8000}
fi