#!/usr/bin/env bash
# Render build script

set -o errexit  # exit on error

echo "🔨 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build complete!"