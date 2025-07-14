# Deployment Guide

This guide will help you deploy your Telegram Bot application to cloud platforms like Render, Heroku, or Railway.

## Prerequisites

- A GitHub repository with your code
- An account on your chosen deployment platform

## Files Added for Deployment

### 1. `requirements.txt`
Contains all necessary Python dependencies including:
- `gunicorn==21.2.0` - WSGI server for production
- `whitenoise==6.6.0` - Static file serving
- All your existing dependencies

### 2. `Procfile`
Tells the deployment platform how to run your application:
```
web: gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 3. `runtime.txt`
Specifies the Python version:
```
python-3.11.7
```

## Deployment Steps

### For Render.com:

1. **Connect Repository**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `your-app-name`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

3. **Environment Variables**
   Add these environment variables in your Render dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   MONGODB_URI=your-mongodb-connection-string
   TELEGRAM_API_ID=your-telegram-api-id
   TELEGRAM_API_HASH=your-telegram-api-hash
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for the build to complete

### For Heroku:

1. **Install Heroku CLI**
   ```bash
   # Download and install from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set MONGODB_URI=your-mongodb-connection-string
   heroku config:set TELEGRAM_API_ID=your-telegram-api-id
   heroku config:set TELEGRAM_API_HASH=your-telegram-api-hash
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## Environment Variables

Make sure to set these environment variables in your deployment platform:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `MONGODB_URI` | MongoDB connection string | No (uses file storage if not set) |
| `TELEGRAM_API_ID` | Your Telegram API ID | Yes |
| `TELEGRAM_API_HASH` | Your Telegram API Hash | Yes |
| `PORT` | Port number (usually set automatically) | No |

## Troubleshooting

### Common Issues:

1. **"gunicorn: command not found"**
   - Make sure `gunicorn` is in your `requirements.txt`
   - Check that the build completed successfully

2. **Port binding issues**
   - The app now uses `$PORT` environment variable automatically
   - Make sure your Procfile is correct

3. **Environment variables not found**
   - Double-check that all required environment variables are set in your deployment platform
   - Verify the variable names match exactly

4. **MongoDB connection issues**
   - If MongoDB is not available, the app will fall back to file storage
   - Check your MongoDB connection string format

### Logs

To view deployment logs:
- **Render**: Go to your service → "Logs" tab
- **Heroku**: `heroku logs --tail`

## Local Testing

To test the deployment configuration locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PORT=5000
export SECRET_KEY=your-secret-key

# Run with gunicorn
gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## Security Notes

1. **Never commit sensitive data** like API keys to your repository
2. **Use environment variables** for all sensitive configuration
3. **Set a strong SECRET_KEY** for production
4. **Enable HTTPS** in your deployment platform settings

## Support

If you encounter issues:
1. Check the deployment logs
2. Verify all environment variables are set
3. Test locally with the same configuration
4. Check the platform's documentation for specific requirements 