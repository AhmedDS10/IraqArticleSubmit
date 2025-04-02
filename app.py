import os
import logging
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")

# Webhook URL
WEBHOOK_URL = "https://auto.ahmedds.us/webhook-test/iraqination"

@app.route('/', methods=['GET'])
def index():
    """Render the article submission form."""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Process the form submission and send data to webhook."""
    # Get form data
    author_name = request.form.get('author_name', '')
    article_title = request.form.get('article_title', '')
    article_content = request.form.get('article_content', '')
    
    # Validate data
    errors = []
    if not author_name:
        errors.append("اسم الكاتب مطلوب")
    if not article_title:
        errors.append("عنوان المقال مطلوب")
    if not article_content:
        errors.append("محتوى المقال مطلوب")
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('index'))
    
    # Prepare data for webhook
    data = {
        "author_name": author_name,
        "article_title": article_title,
        "article_content": article_content
    }
    
    # Send data to webhook
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Log response
        logger.debug(f"Webhook response: {response.status_code} - {response.text}")
        
        # Store success info in session
        session['submission_success'] = True
        session['submission_data'] = data
        
        # Redirect to success page
        return redirect(url_for('success'))
        
    except requests.RequestException as e:
        logger.error(f"Webhook request failed: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/success', methods=['GET'])
def success():
    """Display success page after successful submission."""
    if not session.get('submission_success'):
        return redirect(url_for('index'))
    
    data = session.get('submission_data', {})
    
    # Clear session data after displaying success page
    session.pop('submission_success', None)
    session.pop('submission_data', None)
    
    return render_template('success.html', data=data)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error="حدث خطأ في الخادم"), 500
