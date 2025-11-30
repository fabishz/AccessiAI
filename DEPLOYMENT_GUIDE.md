# AccessiAI Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying AccessiAI to production environments. It includes pre-deployment verification, deployment steps, and post-deployment validation.

## Pre-Deployment Checklist

### 1. Environment Verification

Before deploying, ensure your environment meets these requirements:

- **Python Version**: 3.8 or higher
- **Disk Space**: At least 2GB (for model cache)
- **RAM**: Minimum 4GB (8GB recommended)
- **Internet Connection**: Required for initial model download
- **Operating System**: Linux, macOS, or Windows

### 2. Dependency Installation

```bash
# Install all required dependencies
pip install -r requirements.txt

# Verify installation
python test_deployment.py
```

### 3. Run Deployment Tests

Execute the comprehensive deployment test suite:

```bash
python test_deployment.py
```

This will verify:
- All dependencies are installed
- All modules can be imported
- Analysis works with valid URLs
- Error handling works with invalid URLs
- Export functionality (JSON and HTML) works
- Streamlit UI is properly configured
- requirements.txt contains all dependencies

**Expected Output**: All tests should pass with status "✓ APPLICATION IS READY FOR DEPLOYMENT"

## Deployment Steps

### Local Deployment (Development/Testing)

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd accessiai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open browser to `http://localhost:8501`
   - The application is now ready for testing

### Server Deployment (Production)

#### Option 1: Using Streamlit Cloud (Recommended for Quick Deployment)

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your GitHub repository
   - Select branch and file (`app.py`)
   - Click "Deploy"

3. **Configure secrets** (if needed)
   - Add any API keys or environment variables in Streamlit Cloud settings

#### Option 2: Using Docker (Recommended for Full Control)

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements
   COPY requirements.txt .
   
   # Install Python dependencies
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY . .
   
   # Expose port
   EXPOSE 8501
   
   # Run Streamlit
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build Docker image**
   ```bash
   docker build -t accessiai:latest .
   ```

3. **Run Docker container**
   ```bash
   docker run -p 8501:8501 accessiai:latest
   ```

4. **Access the application**
   - Open browser to `http://localhost:8501` (or your server's IP)

#### Option 3: Using Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **View logs**
   ```bash
   heroku logs --tail
   ```

#### Option 4: Using AWS EC2

1. **Launch EC2 instance**
   - Use Ubuntu 20.04 LTS or later
   - Minimum: t3.medium (2GB RAM)
   - Recommended: t3.large (8GB RAM)

2. **Connect to instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev build-essential
   ```

4. **Clone repository**
   ```bash
   git clone <repository-url>
   cd accessiai
   ```

5. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

6. **Run with systemd service** (for persistent deployment)
   
   Create `/etc/systemd/system/accessiai.service`:
   ```ini
   [Unit]
   Description=AccessiAI Web Service
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/accessiai
   ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl enable accessiai
   sudo systemctl start accessiai
   ```

## Post-Deployment Validation

### 1. Health Check

```bash
# Test with a simple URL
curl -X POST http://your-deployment-url/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 2. Functional Testing

1. **Access the UI**
   - Navigate to your deployment URL
   - Verify the interface loads correctly

2. **Test with sample URLs**
   - https://example.com
   - https://www.wikipedia.org
   - Your own website

3. **Verify all features**
   - Alt text generation works
   - Contrast checking works
   - ARIA suggestions work
   - Export functionality works

4. **Test error handling**
   - Try invalid URLs
   - Try unreachable URLs
   - Verify error messages are user-friendly

### 3. Performance Monitoring

Monitor these metrics:
- **Response Time**: Should be < 60 seconds for most pages
- **Memory Usage**: Should stay below 2GB
- **CPU Usage**: Should not exceed 80% sustained
- **Error Rate**: Should be < 1%

### 4. Log Monitoring

Check application logs for:
- Errors or exceptions
- Warnings about failed image processing
- Performance issues
- Unusual access patterns

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Model cache directory
MODEL_CACHE_DIR=/tmp/model_cache

# Maximum images to analyze per page
MAX_IMAGES=10

# Request timeout (seconds)
REQUEST_TIMEOUT=5

# Image download timeout (seconds)
IMAGE_DOWNLOAD_TIMEOUT=10
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2c3e50"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#ecf0f1"
textColor = "#333333"
font = "sans serif"

[server]
port = 8501
headless = true
runOnSave = false
maxUploadSize = 200

[client]
showErrorDetails = false
```

## Troubleshooting Deployment Issues

### Issue: Model Download Fails

**Symptoms**: Application hangs on first run, "Connection timeout" errors

**Solutions**:
1. Ensure stable internet connection
2. Pre-download model on deployment machine:
   ```bash
   python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"
   ```
3. Increase timeout in `src/image_analyzer.py`

### Issue: Out of Memory Errors

**Symptoms**: Application crashes with "Out of memory" error

**Solutions**:
1. Increase available RAM on deployment machine
2. Reduce `MAX_IMAGES` in `src/parser.py` (default: 10)
3. Clear model cache more frequently
4. Use a machine with more RAM (minimum 8GB recommended)

### Issue: Slow Performance

**Symptoms**: Analysis takes > 2 minutes

**Solutions**:
1. Check network connectivity
2. Verify CPU/RAM availability
3. Try with simpler pages (fewer images)
4. Check if model is cached (first run is slower)

### Issue: Port Already in Use

**Symptoms**: "Address already in use" error

**Solutions**:
```bash
# Find process using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use a different port
streamlit run app.py --server.port=8502
```

### Issue: HTTPS/SSL Errors

**Symptoms**: "SSL certificate verify failed" errors

**Solutions**:
1. Update certificates:
   ```bash
   pip install --upgrade certifi
   ```
2. For testing only (not recommended for production):
   ```bash
   export PYTHONHTTPSVERIFY=0
   ```

## Security Considerations

### 1. Input Validation

- All URLs are validated before processing
- HTML is sanitized before display
- File uploads are restricted

### 2. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from streamlit_throttle import throttle

@throttle(calls=10, period=60)  # 10 calls per minute
def analyze_webpage_throttled(url):
    return analyze_webpage_safe(url)
```

### 3. Authentication (Optional)

For private deployments, add authentication:

```python
import streamlit as st

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        password = st.text_input("Enter password:", type="password")
        if password == "your-secure-password":
            st.session_state.password_correct = True
        else:
            st.error("Incorrect password")
            return False
    return True

if check_password():
    # Your app code here
    pass
```

### 4. HTTPS/SSL

Always use HTTPS in production:

```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d your-domain.com

# Configure Streamlit to use SSL
streamlit run app.py --server.sslCertFile=/etc/letsencrypt/live/your-domain.com/fullchain.pem --server.sslKeyFile=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

## Monitoring and Maintenance

### 1. Regular Backups

```bash
# Backup application code
tar -czf accessiai-backup-$(date +%Y%m%d).tar.gz /path/to/accessiai

# Backup logs
tar -czf accessiai-logs-$(date +%Y%m%d).tar.gz /var/log/accessiai
```

### 2. Log Rotation

Configure log rotation in `/etc/logrotate.d/accessiai`:

```
/var/log/accessiai/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 3. Health Checks

Set up automated health checks:

```bash
#!/bin/bash
# health_check.sh

URL="http://localhost:8501"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✓ Application is healthy"
    exit 0
else
    echo "✗ Application health check failed (HTTP $RESPONSE)"
    # Send alert
    exit 1
fi
```

### 4. Updates and Patches

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Test after update
python test_deployment.py

# Restart application
systemctl restart accessiai
```

## Performance Optimization

### 1. Model Caching

The application automatically caches the BLIP model after first download. To pre-warm the cache:

```bash
python -c "from src.image_analyzer import _load_model; _load_model()"
```

### 2. Image Optimization

Limit image processing:
- Maximum 10 images per page (configurable)
- Images are resized to 384x384 for processing
- Failed images are skipped gracefully

### 3. Database Optimization (if adding persistence)

```python
# Example: Add caching for repeated URLs
import functools
import hashlib

@functools.lru_cache(maxsize=100)
def cached_analysis(url_hash):
    # Return cached result
    pass
```

## Rollback Procedures

If deployment fails:

```bash
# Revert to previous version
git revert HEAD

# Reinstall dependencies
pip install -r requirements.txt

# Restart application
systemctl restart accessiai

# Verify
python test_deployment.py
```

## Support and Troubleshooting

For issues:

1. Check logs: `journalctl -u accessiai -f`
2. Run tests: `python test_deployment.py`
3. Review README.md troubleshooting section
4. Check GitHub issues
5. Contact support

## Conclusion

AccessiAI is now ready for deployment. Follow this guide carefully to ensure a smooth deployment process. Monitor the application after deployment and address any issues promptly.

For questions or issues, refer to the README.md or contact the development team.
