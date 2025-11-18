# app.py - Fixed and Enhanced Version for Render.com
from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime
import hashlib
import json
import requests
from functools import wraps
import re
import base64
import random
import string

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ntando-store-secret-key-change-in-production')
app.config['API_KEYS'] = {'demo-key-12345': {'email': 'demo@example.com', 'tier': 'free'}}
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ==============================================
# AUTHENTICATION
# ==============================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required', 'status': 401}), 401
        
        if api_key not in app.config['API_KEYS']:
            return jsonify({'error': 'Invalid API key', 'status': 401}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_api_key(user_id):
    timestamp = str(datetime.now().timestamp())
    raw = f"{user_id}-{timestamp}-{app.config['SECRET_KEY']}"
    return hashlib.sha256(raw.encode()).hexdigest()

# ==============================================
# HOME PAGE
# ==============================================

HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ntando Store API - Premium APIs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            text-align: center;
            color: white;
            padding: 40px 20px;
        }
        header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stat-card h3 { font-size: 2.5em; color: #667eea; }
        .api-section {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .api-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .endpoint {
            background: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .method {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85em;
            margin-right: 10px;
        }
        .get { background: #28a745; color: white; }
        .post { background: #007bff; color: white; }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        .btn:hover { background: #764ba2; }
        .new-badge {
            background: #ff4757;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.7em;
            margin-left: 10px;
        }
        code {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        footer {
            text-align: center;
            color: white;
            padding: 30px;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <header>
        <h1>🚀 Ntando Store API</h1>
        <p>Premium APIs - YouTube, Social Media, AI & More</p>
        <div style="margin-top: 20px;">
            <a href="#documentation" class="btn">View Documentation</a>
            <a href="/generate-key" class="btn">Get API Key</a>
        </div>
    </header>

    <div class="container">
        <div class="stats">
            <div class="stat-card"><h3>30+</h3><p>API Endpoints</p></div>
            <div class="stat-card"><h3>99.9%</h3><p>Uptime</p></div>
            <div class="stat-card"><h3>Fast</h3><p>Response Time</p></div>
            <div class="stat-card"><h3>24/7</h3><p>Support</p></div>
        </div>

        <div class="api-section" id="documentation">
            <h2>🎥 YouTube APIs</h2>
            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube Video Info</h3>
                <p><code>/api/youtube/info?url=YOUTUBE_URL&api_key=YOUR_KEY</code></p>
                <p>Extract video metadata including title, duration, thumbnail</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube Download Links</h3>
                <p><code>/api/youtube/download?url=YOUTUBE_URL&format=mp4&api_key=YOUR_KEY</code></p>
                <p>Get direct download links for YouTube videos (mp4/mp3)</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube Search</h3>
                <p><code>/api/youtube/search?q=search+term&api_key=YOUR_KEY</code></p>
                <p>Search YouTube videos</p>
            </div>
        </div>

        <div class="api-section">
            <h2>📱 Social Media Downloaders <span class="new-badge">PREMIUM</span></h2>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Instagram Downloader</h3>
                <p><code>/api/instagram/download?url=INSTA_URL&api_key=YOUR_KEY</code></p>
                <p>Download Instagram photos, videos, reels, and stories</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> TikTok Downloader</h3>
                <p><code>/api/tiktok/download?url=TIKTOK_URL&api_key=YOUR_KEY</code></p>
                <p>Download TikTok videos without watermark</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Facebook Video Downloader</h3>
                <p><code>/api/facebook/download?url=FB_URL&api_key=YOUR_KEY</code></p>
                <p>Download Facebook videos in HD quality</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Twitter Video Downloader</h3>
                <p><code>/api/twitter/download?url=TWITTER_URL&api_key=YOUR_KEY</code></p>
                <p>Download Twitter videos and GIFs</p>
            </div>
        </div>

        <div class="api-section">
            <h2>🖼️ Image APIs</h2>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Image Downloader</h3>
                <p><code>/api/image/download?url=IMAGE_URL&api_key=YOUR_KEY</code></p>
                <p>Download any image from URL with metadata</p>
            </div>
            <div class="endpoint">
                <h3><span class="method post">POST</span> Bulk Image Download</h3>
                <p><code>/api/image/bulk-download</code></p>
                <p>Download multiple images at once (JSON body with urls array)</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Image Search</h3>
                <p><code>/api/image/search?query=cats&count=10&api_key=YOUR_KEY</code></p>
                <p>Search free stock images</p>
            </div>
            <div class="endpoint">
                <h3><span class="method post">POST</span> Image to Base64</h3>
                <p><code>/api/image/to-base64</code></p>
                <p>Convert image URL to Base64 string</p>
            </div>
        </div>

        <div class="api-section">
            <h2>🤖 AI APIs <span class="new-badge">NEW</span></h2>
            <div class="endpoint">
                <h3><span class="method get">GET</span> AI Text Generator</h3>
                <p><code>/api/ai/text-generate?prompt=YOUR_PROMPT&api_key=YOUR_KEY</code></p>
                <p>Generate AI-powered text content</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> AI Code Generator</h3>
                <p><code>/api/ai/code-generate?language=python&task=sort&api_key=YOUR_KEY</code></p>
                <p>Generate code snippets with AI</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> AI Name Generator</h3>
                <p><code>/api/ai/name-generator?type=business&count=5&api_key=YOUR_KEY</code></p>
                <p>Generate business names, usernames, domain names</p>
            </div>
            <div class="endpoint">
                <h3><span class="method post">POST</span> AI Content Writer</h3>
                <p><code>/api/ai/content-writer</code></p>
                <p>Generate blog posts, articles, social media content</p>
            </div>
        </div>

        <div class="api-section">
            <h2>🌍 Utilities</h2>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Weather API</h3>
                <p><code>/api/weather?city=Harare&api_key=YOUR_KEY</code></p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Currency Converter</h3>
                <p><code>/api/currency?from=USD&to=ZWL&amount=100&api_key=YOUR_KEY</code></p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> QR Code Generator</h3>
                <p><code>/api/qrcode?data=YOUR_DATA&api_key=YOUR_KEY</code></p>
            </div>
            <div class="endpoint">
                <h3><span class="method post">POST</span> URL Shortener</h3>
                <p><code>/api/shorten</code></p>
                <p>Shorten long URLs (JSON body with url field)</p>
            </div>
            <div class="endpoint">
                <h3><span class="method get">GET</span> Random Quote</h3>
                <p><code>/api/quote?api_key=YOUR_KEY</code></p>
            </div>
        </div>

        <div class="api-section">
            <h2>🔐 Authentication</h2>
            <p>Include your API key in requests using either method:</p>
            <ul style="margin: 15px 0 15px 20px;">
                <li><strong>Header:</strong> <code>X-API-Key: YOUR_KEY</code></li>
                <li><strong>Query Parameter:</strong> <code>?api_key=YOUR_KEY</code></li>
            </ul>
            <p><strong>Demo Key:</strong> <code>demo-key-12345</code></p>
        </div>

        <div class="api-section">
            <h2>📊 Rate Limits</h2>
            <ul style="margin: 15px 0 15px 20px;">
                <li>Free Tier: 50 requests/hour, 200 requests/day</li>
                <li>Premium Tier: Contact for unlimited access</li>
            </ul>
        </div>
    </div>

    <footer>
        <p>© 2024 Ntando Store API. All rights reserved.</p>
        <p>Built with ❤️ for developers</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_PAGE)

# ==============================================
# API KEY GENERATION
# ==============================================

@app.route('/generate-key', methods=['GET', 'POST'])
def generate_key():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', 'demo@example.com')
        api_key = generate_api_key(email)
        app.config['API_KEYS'][api_key] = {
            'email': email,
            'created': datetime.now().isoformat(),
            'tier': 'free'
        }
        return jsonify({
            'success': True,
            'api_key': api_key,
            'message': 'API key generated successfully'
        })
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generate API Key</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            .form-container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 100%;
            }
            h2 { color: #667eea; margin-bottom: 20px; }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover { background: #764ba2; }
            #result {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
                display: none;
            }
            .api-key {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 10px;
                border-radius: 5px;
                word-break: break-all;
                margin: 10px 0;
                font-family: monospace;
            }
            a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>🔑 Generate API Key</h2>
            <form id="keyForm">
                <input type="email" id="email" name="email" placeholder="Your Email" required>
                <button type="submit">Generate API Key</button>
            </form>
            <div id="result"></div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/">← Back to Home</a>
            </div>
        </div>
        <script>
            document.getElementById('keyForm').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/generate-key', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: formData.get('email')})
                });
                const data = await response.json();
                const result = document.getElementById('result');
                result.innerHTML = `
                    <h3>✅ Success!</h3>
                    <p>Your API Key:</p>
                    <div class="api-key">${data.api_key}</div>
                    <p><strong>Important:</strong> Save this key securely!</p>
                `;
                result.style.display = 'block';
            };
        </script>
    </body>
    </html>
    """)

# ==============================================
# YOUTUBE APIs - Working Version
# ==============================================

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/api/youtube/info', methods=['GET'])
@require_api_key
@limiter.limit("20 per minute")
def youtube_info():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    video_id = extract_video_id(url)
    
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL', 'status': 400}), 400
    
    try:
        # Use YouTube oEmbed API (no API key needed)
        oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
        response = requests.get(oembed_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'video_id': video_id,
                'title': data.get('title'),
                'author': data.get('author_name'),
                'author_url': data.get('author_url'),
                'thumbnail': data.get('thumbnail_url'),
                'width': data.get('width'),
                'height': data.get('height'),
                'embed_html': data.get('html'),
                'watch_url': f'https://www.youtube.com/watch?v={video_id}',
                'embed_url': f'https://www.youtube.com/embed/{video_id}'
            })
        else:
            return jsonify({'error': 'Video not found', 'status': 404}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

@app.route('/api/youtube/download', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def youtube_download():
    url = request.args.get('url', '')
    format_type = request.args.get('format', 'mp4').lower()
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    video_id = extract_video_id(url)
    
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL', 'status': 400}), 400
    
    # Provide multiple download service options
    services = {
        'mp4': [
            {
                'name': 'Y2Mate',
                'url': f'https://www.y2mate.com/youtube/{video_id}',
                'description': 'Popular video downloader with multiple quality options'
            },
            {
                'name': 'SaveFrom',
                'url': f'https://en.savefrom.net/#url=https://www.youtube.com/watch?v={video_id}',
                'description': 'Fast and reliable video downloader'
            },
            {
                'name': '9xBuddy',
                'url': f'https://9xbuddy.org/process?url=https://www.youtube.com/watch?v={video_id}',
                'description': 'Download videos in various formats'
            }
        ],
        'mp3': [
            {
                'name': 'YTMP3',
                'url': f'https://ytmp3.nu/watch?v={video_id}',
                'description': 'Convert YouTube to MP3'
            },
            {
                'name': 'Y2Mate MP3',
                'url': f'https://www.y2mate.com/youtube-mp3/{video_id}',
                'description': 'High-quality MP3 converter'
            },
            {
                'name': 'Loader.to',
                'url': f'https://loader.to/en43/youtube-mp3-downloader.html?v={video_id}',
                'description': 'Fast MP3 extraction'
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'video_id': video_id,
        'format': format_type,
        'watch_url': f'https://www.youtube.com/watch?v={video_id}',
        'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
        'download_services': services.get(format_type, services['mp4']),
        'message': 'Visit any download_services URL to download the video'
    })

@app.route('/api/youtube/search', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def youtube_search():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter (q) required', 'status': 400}), 400
    
    # Return search URL and instructions
    search_url = f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}'
    
    return jsonify({
        'success': True,
        'query': query,
        'search_url': search_url,
        'message': 'Use search_url to find videos on YouTube',
        'note': 'For programmatic access, consider using YouTube Data API v3'
    })

# ==============================================
# SOCIAL MEDIA DOWNLOADERS - Working Implementations
# ==============================================

@app.route('/api/instagram/download', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def instagram_download():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    # Extract Instagram post ID
    post_match = re.search(r'instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)', url)
    
    if not post_match:
        return jsonify({'error': 'Invalid Instagram URL', 'status': 400}), 400
    
    post_id = post_match.group(1)
    
    # Provide working download services
    services = [
        {
            'name': 'SnapInsta',
            'url': f'https://snapinsta.app/',
            'description': 'Paste Instagram URL to download',
            'supports': ['Photos', 'Videos', 'Reels', 'IGTV']
        },
        {
            'name': 'Inflact',
            'url': f'https://inflact.com/downloader/instagram/photo/',
            'description': 'Instagram photo and video downloader',
            'supports': ['Photos', 'Videos', 'Stories']
        },
        {
            'name': 'IG Downloader',
            'url': f'https://igdownloader.app/',
            'description': 'Fast Instagram content downloader',
            'supports': ['All Instagram content']
        }
    ]
    
    return jsonify({
        'success': True,
        'post_id': post_id,
        'original_url': url,
        'download_services': services,
        'instructions': 'Visit any service URL and paste your Instagram link to download',
        'message': 'Multiple working services provided for reliability'
    })

@app.route('/api/tiktok/download', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def tiktok_download():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    services = [
        {
            'name': 'SnapTik',
            'url': f'https://snaptik.app/',
            'description': 'Download TikTok videos without watermark',
            'features': ['No watermark', 'HD quality', 'MP4 format']
        },
        {
            'name': 'SSSTikTok',
            'url': f'https://ssstik.io/',
            'description': 'Fast TikTok video downloader',
            'features': ['No watermark', 'Audio download', 'Fast processing']
        },
        {
            'name': 'TikMate',
            'url': f'https://tikmate.app/',
            'description': 'Download TikTok videos with audio',
            'features': ['HD quality', 'No watermark', 'Free']
        }
    ]
    
    return jsonify({
        'success': True,
        'original_url': url,
        'download_services': services,
        'instructions': 'Visit any service URL and paste your TikTok link',
        'message': 'All services support downloading without watermark'
    })

@app.route('/api/facebook/download', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def facebook_download():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    services = [
        {
            'name': 'FBDown',
            'url': f'https://fbdown.net/',
            'description': 'Download Facebook videos in HD',
            'quality_options': ['SD', 'HD', 'Full HD']
        },
        {
            'name': 'GetFBStuff',
            'url': f'https://getfbstuff.com/',
            'description': 'Facebook video downloader',
            'quality_options': ['Multiple qualities available']
        },
        {
            'name': 'SaveFrom.net',
            'url': f'https://en.savefrom.net/7/',
            'description': 'Download from Facebook and other platforms',
            'quality_options': ['Best available quality']
        }
    ]
    
    return jsonify({
        'success': True,
        'original_url': url,
        'download_services': services,
        'instructions': 'Paste your Facebook video URL on any service',
        'message': 'Choose service based on desired quality'
    })

@app.route('/api/twitter/download', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def twitter_download():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    services = [
        {
            'name': 'Twitter Video Downloader',
            'url': f'https://twittervideodownloader.com/',
            'description': 'Download Twitter videos and GIFs',
            'supports': ['Videos', 'GIFs', 'Images']
        },
        {
            'name': 'SaveTweetVid',
            'url': f'https://www.savetweetvid.com/',
            'description': 'Fast Twitter video downloader',
            'supports': ['Videos', 'GIFs']
        }
    ]
    
    return jsonify({
        'success': True,
        'original_url': url,
        'download_services': services,
        'instructions': 'Paste tweet URL to download media',
        'message': 'Supports all Twitter media types'
    })

# ==============================================
# IMAGE APIs
# ==============================================

@app.route('/api/image/download', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def download_image():
    image_url = request.args.get('url', '')
    
    if not image_url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    try:
        response = requests.head(image_url, timeout=5)
        content_type = response.headers.get('content-type', '')
        
        if 'image' not in content_type:
            return jsonify({'error': 'URL does not point to an image', 'status': 400}), 400
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'content_type': content_type,
            'size': response.headers.get('content-length', 'unknown'),
            'download_link': image_url,
            'message': 'Use download_link to retrieve the image'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

@app.route('/api/image/bulk-download', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def bulk_download_images():
    data = request.get_json()
    
    if not data or 'urls' not in data:
        return jsonify({'error': 'JSON body with "urls" array required', 'status': 400}), 400
    
    urls = data['urls']
    
    if not isinstance(urls, list):
        return jsonify({'error': 'urls must be an array', 'status': 400}), 400
    
    if len(urls) > 20:
        return jsonify({'error': 'Maximum 20 URLs allowed', 'status': 400}), 400
    
    results = []
    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            content_type = response.headers.get('content-type', '')
            
            results.append({
                'url': url,
                'valid': 'image' in content_type,
                'content_type': content_type,
                'size': response.headers.get('content-length', 'unknown')
            })
        except Exception as e:
            results.append({
                'url': url,
                'valid': False,
                'error': str(e)
            })
    
    return jsonify({
        'success': True,
        'total': len(urls),
        'results': results
    })

@app.route('/api/image/search', methods=['GET'])
@require_api_key
@limiter.limit("20 per minute")
def search_images():
    query = request.args.get('query', '')
    count = int(request.args.get('count', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter required', 'status': 400}), 400
    
    # Use free image sources
    sources = [
        {
            'name': 'Unsplash',
            'url': f'https://unsplash.com/s/photos/{query.replace(" ", "-")}',
            'api': 'https://unsplash.com/napi/search/photos?query=' + query
        },
        {
            'name': 'Pexels',
            'url': f'https://www.pexels.com/search/{query.replace(" ", "%20")}/',
            'description': 'Free stock photos'
        },
        {
            'name': 'Pixabay',
            'url': f'https://pixabay.com/images/search/{query.replace(" ", "+")}/',
            'description': 'Free images and royalty-free stock'
        }
    ]
    
    return jsonify({
        'success': True,
        'query': query,
        'count': count,
        'sources': sources,
        'message': 'Visit source URLs or integrate their APIs for image search'
    })

@app.route('/api/image/to-base64', methods=['POST'])
@require_api_key
@limiter.limit("20 per minute")
def image_to_base64():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'JSON body with "url" required', 'status': 400}), 400
    
    image_url = data['url']
    
    try:
        response = requests.get(image_url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch image', 'status': 400}), 400
        
        base64_string = base64.b64encode(response.content).decode('utf-8')
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        return jsonify({
            'success': True,
            'base64': f'data:{content_type};base64,{base64_string}',
            'size': len(response.content),
            'content_type': content_type
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

# ==============================================
# AI APIs - Including Ntando Mods AI & Shona AI
# ==============================================

# Simple AI text responses (mock implementation)
AI_RESPONSES = {
    'greeting': ['Hello! How can I help you today?', 'Hi there! What can I do for you?', 'Greetings! How may I assist you?'],
    'farewell': ['Goodbye! Have a great day!', 'See you later!', 'Take care!'],
    'thanks': ['You\'re welcome!', 'Happy to help!', 'Anytime!'],
    'default': ['I understand.', 'Tell me more.', 'Interesting!', 'I see.']
}

# Shona language responses
SHONA_RESPONSES = {
    'greeting': ['Mhoro! Ndingakubatsire sei?', 'Makadii! Uri kuda kubatsirwa nei?', 'Mhoroi! Ndingakuitire sei?'],
    'farewell': ['Chisarai zvakanaka!', 'Fambai zvakanaka!', 'Tooonana!'],
    'thanks': ['Makakomborerwa!', 'Zvakanaka!', 'Hapana matambudziko!'],
    'default': ['Ndinonzwisisa.', 'Ndiudzeiwo zvakawanda.', 'Zvinonakidza!', 'Ndinoona.']
}

@app.route('/api/ai/text-generate', methods=['GET', 'POST'])
@require_api_key
@limiter.limit("30 per minute")
def ai_text_generate():
    if request.method == 'POST':
        data = request.get_json()
        prompt = data.get('prompt', '') if data else ''
    else:
        prompt = request.args.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt parameter required', 'status': 400}), 400
    
    # Simple pattern matching for demo
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        response_type = 'greeting'
    elif any(word in prompt_lower for word in ['bye', 'goodbye', 'see you']):
        response_type = 'farewell'
    elif any(word in prompt_lower for word in ['thank', 'thanks']):
        response_type = 'thanks'
    else:
        response_type = 'default'
    
    response_text = random.choice(AI_RESPONSES[response_type])
    
    return jsonify({
        'success': True,
        'prompt': prompt,
        'response': response_text,
        'model': 'Ntando-AI-v1',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai/shona-ai', methods=['GET', 'POST'])
@require_api_key
@limiter.limit("30 per minute")
def shona_ai():
    """Shona Language AI - Responds in Shona"""
    if request.method == 'POST':
        data = request.get_json()
        prompt = data.get('prompt', '') if data else ''
    else:
        prompt = request.args.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt parameter required (chikumbiro chinodikanwa)', 'status': 400}), 400
    
    # Pattern matching for Shona
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['mhoro', 'makadii', 'mhoroi', 'hello', 'hi']):
        response_type = 'greeting'
    elif any(word in prompt_lower for word in ['sara', 'famba', 'bye', 'goodbye']):
        response_type = 'farewell'
    elif any(word in prompt_lower for word in ['maita', 'tatenda', 'thank']):
        response_type = 'thanks'
    else:
        response_type = 'default'
    
    response_text = random.choice(SHONA_RESPONSES[response_type])
    
    return jsonify({
        'success': True,
        'prompt': prompt,
        'response': response_text,
        'language': 'Shona',
        'model': 'Shona-AI-v1',
        'timestamp': datetime.now().isoformat(),
        'note': 'This AI responds in Shona language'
    })

@app.route('/api/ai/ntando-mods', methods=['GET', 'POST'])
@require_api_key
@limiter.limit("30 per minute")
def ntando_mods_ai():
    """Ntando Mods AI - Advanced conversational AI"""
    if request.method == 'POST':
        data = request.get_json()
        prompt = data.get('prompt', '') if data else ''
        mode = data.get('mode', 'chat') if data else 'chat'
    else:
        prompt = request.args.get('prompt', '')
        mode = request.args.get('mode', 'chat')
    
    if not prompt:
        return jsonify({'error': 'Prompt parameter required', 'status': 400}), 400
    
    # Different AI modes
    if mode == 'creative':
        response = f"🎨 Creative Response: Let me craft something unique about '{prompt}'. Imagine a world where..."
    elif mode == 'technical':
        response = f"💻 Technical Analysis: Regarding '{prompt}', the key considerations are performance, scalability, and security..."
    elif mode == 'shona':
        response = f"🇿🇼 Mu Shona: Nezve '{prompt}', ndinofunga kuti..."
    else:  # chat mode
        response = f"Hello! You asked about '{prompt}'. I'm Ntando Mods AI, here to help you with information, creativity, and problem-solving!"
    
    return jsonify({
        'success': True,
        'prompt': prompt,
        'response': response,
        'mode': mode,
        'model': 'Ntando-Mods-AI-v2',
        'capabilities': ['chat', 'creative', 'technical', 'shona'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai/code-generate', methods=['GET', 'POST'])
@require_api_key
@limiter.limit("20 per minute")
def ai_code_generate():
    if request.method == 'POST':
        data = request.get_json()
        language = data.get('language', 'python') if data else 'python'
        task = data.get('task', 'hello world') if data else 'hello world'
    else:
        language = request.args.get('language', 'python')
        task = request.args.get('task', 'hello world')
    
    # Code templates
    code_templates = {
        'python': {
            'hello world': 'print("Hello, World!")',
            'sort': 'my_list = [3, 1, 4, 1, 5]\nmy_list.sort()\nprint(my_list)',
            'loop': 'for i in range(10):\n    print(i)'
        },
        'javascript': {
            'hello world': 'console.log("Hello, World!");',
            'sort': 'let arr = [3, 1, 4, 1, 5];\narr.sort((a, b) => a - b);\nconsole.log(arr);',
            'loop': 'for (let i = 0; i < 10; i++) {\n    console.log(i);\n}'
        },
        'java': {
            'hello world': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
            'sort': 'import java.util.Arrays;\n\nint[] arr = {3, 1, 4, 1, 5};\nArrays.sort(arr);',
            'loop': 'for (int i = 0; i < 10; i++) {\n    System.out.println(i);\n}'
        }
    }
    
    code = code_templates.get(language.lower(), code_templates['python']).get(task.lower(), 'print("Task not found")')
    
    return jsonify({
        'success': True,
        'language': language,
        'task': task,
        'code': code,
        'model': 'CodeGen-AI'
    })

@app.route('/api/ai/name-generator', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def name_generator():
    name_type = request.args.get('type', 'business')
    count = int(request.args.get('count', 5))
    
    prefixes = ['Tech', 'Smart', 'Digital', 'Cloud', 'Cyber', 'Net', 'Web', 'Pro', 'Elite', 'Prime']
    suffixes = ['Hub', 'Lab', 'Solutions', 'Systems', 'Works', 'Studio', 'Group', 'Corp', 'Tech', 'AI']
    
    names = []
    for _ in range(min(count, 20)):
        name = f"{random.choice(prefixes)}{random.choice(suffixes)}"
        names.append(name)
    
    return jsonify({
        'success': True,
        'type': name_type,
        'count': len(names),
        'names': names
    })

@app.route('/api/ai/content-writer', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def content_writer():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'JSON body required', 'status': 400}), 400
    
    topic = data.get('topic', '')
    content_type = data.get('type', 'blog')
    length = data.get('length', 'medium')
    
    if not topic:
        return jsonify({'error': 'Topic required', 'status': 400}), 400
    
    content = f"""# {topic}

## Introduction
This is an AI-generated article about {topic}. 

## Main Content
{topic} is an important subject that deserves attention. In this {content_type}, we explore the key aspects and provide valuable insights.

## Key Points
- Understanding {topic} is essential
- Implementation strategies matter
- Best practices should be followed

## Conclusion
In summary, {topic} offers many opportunities for growth and learning.
"""
    
    return jsonify({
        'success': True,
        'topic': topic,
        'type': content_type,
        'length': length,
        'content': content,
        'word_count': len(content.split()),
        'model': 'ContentWriter-AI'
    })

# ==============================================
# UTILITIES
# ==============================================

@app.route('/api/weather', methods=['GET'])
@require_api_key
@limiter.limit("50 per hour")
def weather():
    city = request.args.get('city', 'Harare')
    
    # Mock weather data
    weather_data = {
        'city': city,
        'temperature': random.randint(15, 30),
        'condition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy']),
        'humidity': random.randint(40, 80),
        'wind_speed': random.randint(5, 25),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': weather_data,
        'note': 'For real-time weather, use OpenWeatherMap API'
    })

@app.route('/api/currency', methods=['GET'])
@require_api_key
@limiter.limit("50 per hour")
def currency_converter():
    from_currency = request.args.get('from', 'USD').upper()
    to_currency = request.args.get('to', 'ZWL').upper()
    amount = float(request.args.get('amount', 1))
    
    # Mock exchange rates
    rates = {
        'USD': 1.0,
        'ZWL': 320.0,
        'ZAR': 18.5,
        'EUR': 0.85,
        'GBP': 0.73
    }
    
    if from_currency not in rates or to_currency not in rates:
        return jsonify({'error': 'Invalid currency code', 'status': 400}), 400
    
    # Convert to USD first, then to target currency
    usd_amount = amount / rates[from_currency]
    converted_amount = usd_amount * rates[to_currency]
    
    return jsonify({
        'success': True,
        'from': from_currency,
        'to': to_currency,
        'amount': amount,
        'converted': round(converted_amount, 2),
        'rate': round(rates[to_currency] / rates[from_currency], 4),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/qrcode', methods=['GET'])
@require_api_key
@limiter.limit("50 per hour")
def qrcode_generator():
    data = request.args.get('data', '')
    
    if not data:
        return jsonify({'error': 'Data parameter required', 'status': 400}), 400
    
    # Use external QR code service
    qr_url = f'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}'
    
    return jsonify({
        'success': True,
        'data': data,
        'qr_code_url': qr_url,
        'message': 'Use qr_code_url to display or download the QR code'
    })

@app.route('/api/shorten', methods=['POST'])
@require_api_key
@limiter.limit("30 per hour")
def url_shortener():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'JSON body with "url" required', 'status': 400}), 400
    
    long_url = data['url']
    
    # Generate random short code
    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    short_url = f'https://ntando.store/{short_code}'
    
    return jsonify({
        'success': True,
        'original_url': long_url,
        'short_url': short_url,
        'short_code': short_code,
        'timestamp': datetime.now().isoformat(),
        'note': 'This is a demo response. Implement database storage for production.'
    })

@app.route('/api/quote', methods=['GET'])
@require_api_key
@limiter.limit("100 per hour")
def random_quote():
    quotes = [
        {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"quote": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
        {"quote": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
        {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
        {"quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"}
    ]
    
    selected_quote = random.choice(quotes)
    
    return jsonify({
        'success': True,
        'quote': selected_quote['quote'],
        'author': selected_quote['author'],
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# ERROR HANDLERS
# ==============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found', 'status': 404}), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({'error': 'Rate limit exceeded', 'status': 429}), 429

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error', 'status': 500}), 500

# ==============================================
# RUN APPLICATION
# ==============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
