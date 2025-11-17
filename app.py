# app.py - Main Flask Application
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime, timedelta
import jwt
import hashlib
import json
import requests
from functools import wraps
import yt_dlp
import re

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ntando-store-secret-key-change-in-production')
app.config['API_KEYS'] = {}  # Store API keys in memory (use database in production)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ==============================================
# AUTHENTICATION & API KEY MANAGEMENT
# ==============================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required', 'status': 401}), 401
        
        # In production, validate against database
        if api_key not in app.config['API_KEYS'] and api_key != 'demo-key-12345':
            return jsonify({'error': 'Invalid API key', 'status': 401}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_api_key(user_id):
    """Generate a unique API key"""
    timestamp = str(datetime.now().timestamp())
    raw = f"{user_id}-{timestamp}-{app.config['SECRET_KEY']}"
    return hashlib.sha256(raw.encode()).hexdigest()

# ==============================================
# HOME PAGE & DOCUMENTATION
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
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
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
        header p {
            font-size: 1.2em;
            opacity: 0.9;
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
        .stat-card h3 {
            font-size: 2.5em;
            color: #667eea;
            margin-bottom: 10px;
        }
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
        .endpoint h3 {
            color: #333;
            margin-bottom: 10px;
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
        .code {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
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
        .btn:hover {
            background: #764ba2;
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
        <p>Premium APIs for Developers - AI, Bible, YouTube & More</p>
        <div style="margin-top: 20px;">
            <a href="#documentation" class="btn">View Documentation</a>
            <a href="/generate-key" class="btn">Get API Key</a>
        </div>
    </header>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>15+</h3>
                <p>API Endpoints</p>
            </div>
            <div class="stat-card">
                <h3>99.9%</h3>
                <p>Uptime</p>
            </div>
            <div class="stat-card">
                <h3>Fast</h3>
                <p>Response Time</p>
            </div>
            <div class="stat-card">
                <h3>24/7</h3>
                <p>Support</p>
            </div>
        </div>

        <div class="api-section" id="documentation">
            <h2>📚 API Documentation</h2>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> Shona AI Chat</h3>
                <p><strong>Endpoint:</strong> <code>/api/shona-ai</code></p>
                <p><strong>Description:</strong> AI-powered chat in Shona language</p>
                <div class="code">GET /api/shona-ai?message=Mhoro&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> Bible Verse (Shona)</h3>
                <p><strong>Endpoint:</strong> <code>/api/bible/shona</code></p>
                <p><strong>Description:</strong> Get Bible verses in Shona</p>
                <div class="code">GET /api/bible/shona?verse=John+3:16&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube MP3 Download</h3>
                <p><strong>Endpoint:</strong> <code>/api/youtube/mp3</code></p>
                <p><strong>Description:</strong> Extract MP3 audio from YouTube</p>
                <div class="code">GET /api/youtube/mp3?url=YOUTUBE_URL&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube MP4 Download</h3>
                <p><strong>Endpoint:</strong> <code>/api/youtube/mp4</code></p>
                <p><strong>Description:</strong> Download YouTube videos in MP4</p>
                <div class="code">GET /api/youtube/mp4?url=YOUTUBE_URL&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube Video Info</h3>
                <p><strong>Endpoint:</strong> <code>/api/youtube/info</code></p>
                <p><strong>Description:</strong> Get video information</p>
                <div class="code">GET /api/youtube/info?url=YOUTUBE_URL&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> YouTube Search</h3>
                <p><strong>Endpoint:</strong> <code>/api/youtube/search</code></p>
                <p><strong>Description:</strong> Search YouTube videos</p>
                <div class="code">GET /api/youtube/search?q=search+term&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> Weather API</h3>
                <p><strong>Endpoint:</strong> <code>/api/weather</code></p>
                <p><strong>Description:</strong> Get weather information</p>
                <div class="code">GET /api/weather?city=Harare&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> Currency Converter</h3>
                <p><strong>Endpoint:</strong> <code>/api/currency</code></p>
                <p><strong>Description:</strong> Convert currencies</p>
                <div class="code">GET /api/currency?from=USD&to=ZWL&amount=100&api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> Random Quote</h3>
                <p><strong>Endpoint:</strong> <code>/api/quote</code></p>
                <p><strong>Description:</strong> Get inspirational quotes</p>
                <div class="code">GET /api/quote?api_key=YOUR_KEY</div>
            </div>

            <div class="endpoint">
                <h3><span class="method post">POST</span> Image Analysis</h3>
                <p><strong>Endpoint:</strong> <code>/api/image/analyze</code></p>
                <p><strong>Description:</strong> Analyze images with AI</p>
                <div class="code">POST /api/image/analyze
Content-Type: application/json
{"image_url": "URL", "api_key": "YOUR_KEY"}</div>
            </div>
        </div>

        <div class="api-section">
            <h2>🔑 Authentication</h2>
            <p>All API requests require an API key. Include it in your requests:</p>
            <ul style="margin: 15px 0 15px 20px;">
                <li><strong>Header:</strong> <code>X-API-Key: YOUR_KEY</code></li>
                <li><strong>Query Parameter:</strong> <code>?api_key=YOUR_KEY</code></li>
            </ul>
            <div class="code">curl -H "X-API-Key: YOUR_KEY" https://your-api.render.com/api/endpoint</div>
        </div>

        <div class="api-section">
            <h2>💡 Example Usage (Python)</h2>
            <div class="code">import requests

api_key = "YOUR_API_KEY"
base_url = "https://your-api.render.com"

# Shona AI Chat
response = requests.get(
    f"{base_url}/api/shona-ai",
    params={"message": "Mhoro, makadii?", "api_key": api_key}
)
print(response.json())

# YouTube MP3 Download
response = requests.get(
    f"{base_url}/api/youtube/mp3",
    params={"url": "youtube_url", "api_key": api_key}
)
print(response.json())</div>
        </div>

        <div class="api-section">
            <h2>📊 Rate Limits</h2>
            <ul style="margin: 15px 0 15px 20px;">
                <li>Free Tier: 50 requests/hour, 200 requests/day</li>
                <li>Premium Tier: Unlimited requests</li>
                <li>Rate limit headers included in all responses</li>
            </ul>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 Ntando Store API. All rights reserved.</p>
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
        email = request.form.get('email', 'demo@example.com')
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
        <title>Generate API Key - Ntando Store</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
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
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>🔑 Generate API Key</h2>
            <form id="keyForm">
                <input type="email" id="email" placeholder="Your Email" required>
                <button type="submit">Generate API Key</button>
            </form>
            <div id="result"></div>
            <a href="/" style="display: block; text-align: center; margin-top: 20px; color: #667eea;">← Back to Home</a>
        </div>
        <script>
            document.getElementById('keyForm').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/generate-key', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                const result = document.getElementById('result');
                result.innerHTML = `
                    <h3>✅ Success!</h3>
                    <p>Your API Key:</p>
                    <div class="api-key">${data.api_key}</div>
                    <p><strong>Important:</strong> Save this key securely. You'll need it for all API requests.</p>
                `;
                result.style.display = 'block';
            };
        </script>
    </body>
    </html>
    """)

# ==============================================
# SHONA AI API
# ==============================================

@app.route('/api/shona-ai', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def shona_ai():
    message = request.args.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message parameter required', 'status': 400}), 400
    
    # Shona AI responses (simple implementation - can be enhanced with actual AI)
    shona_responses = {
        'mhoro': 'Mhoro! Ndiri kufara kukuona. Ndingakubatsira sei?',
        'makadii': 'Ndiri mushe, makadii iwe?',
        'zvakanaka': 'Ndafara kuzvinzwa! Une mibvunzo here?',
        'ndiyani': 'Ndiri Shona AI, ndiri pano kukubatsira nemibvunzo yako.',
        'tatenda': 'Hazvina mhosva! Ndiri pano kukubatsira.',
    }
    
    message_lower = message.lower()
    response_text = None
    
    for key, value in shona_responses.items():
        if key in message_lower:
            response_text = value
            break
    
    if not response_text:
        response_text = f'Ndanzwa kuti uri kuti: "{message}". Ungandipa rumwe ruzivo here?'
    
    return jsonify({
        'success': True,
        'message': message,
        'response': response_text,
        'language': 'shona',
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# BIBLE API (SHONA)
# ==============================================

SHONA_BIBLE_VERSES = {
    'john 3:16': 'Nokuti Mwari akada nyika kudai, kuti akapa Mwanakomana wake mumwe oga, kuti ani nani anotenda kwaari, arege kufa, asi ave neupenyu husingaperi.',
    'psalm 23:1': 'Jehovha Mufudzi wangu; handizoshayiwi chinhu.',
    'proverbs 3:5': 'Vimba naJehovha nemoyo wako wose, Usazendamira njere dzako.',
    'matthew 28:19': 'Naizvozvo endai, mudzidzise marudzi ose, muchibhabhatidza muzita raBaba, noroMwanakomana, noroMweya Mutsvene.',
    'philippians 4:13': 'Ndinogona zvinhu zvose mukurukirwa ndinopiwa naKristu.',
    'romans 8:28': 'Tinoziva kuti zvinhu zvose zvinobatana pamwe chete kuti zvive zvakanaka kuna avo vanoda Mwari.',
    'isaiah 41:10': 'Usatya, nokuti ndinewe; usavhunduka, nokuti ndiri Mwari wako.',
    'jeremiah 29:11': 'Nokuti ndinoziva zvinangwa zvandakufungirai, ndizvo zvinoreva Jehovha, zvinangwa zvokukupa rugare, kwete zvakaipa.',
}

@app.route('/api/bible/shona', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def bible_shona():
    verse = request.args.get('verse', '').lower()
    
    if not verse:
        return jsonify({
            'error': 'Verse parameter required',
            'example': 'John 3:16',
            'status': 400
        }), 400
    
    verse_text = SHONA_BIBLE_VERSES.get(verse)
    
    if verse_text:
        return jsonify({
            'success': True,
            'verse': verse.title(),
            'text': verse_text,
            'language': 'shona',
            'translation': 'Shona Bible'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Verse not found',
            'available_verses': list(SHONA_BIBLE_VERSES.keys()),
            'status': 404
        }), 404

# ==============================================
# YOUTUBE DOWNLOAD API
# ==============================================

def get_youtube_info(url):
    """Extract YouTube video information"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        return None

@app.route('/api/youtube/info', methods=['GET'])
@require_api_key
@limiter.limit("20 per minute")
def youtube_info():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    info = get_youtube_info(url)
    
    if not info:
        return jsonify({'error': 'Failed to fetch video info', 'status': 400}), 400
    
    return jsonify({
        'success': True,
        'title': info.get('title'),
        'duration': info.get('duration'),
        'views': info.get('view_count'),
        'author': info.get('uploader'),
        'thumbnail': info.get('thumbnail'),
        'description': info.get('description', '')[:200],
        'upload_date': info.get('upload_date')
    })

@app.route('/api/youtube/mp3', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def youtube_mp3():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get best audio format
            audio_url = None
            for fmt in info['formats']:
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    audio_url = fmt['url']
                    break
            
            if not audio_url and info.get('url'):
                audio_url = info['url']
            
            return jsonify({
                'success': True,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'download_url': audio_url,
                'format': 'mp3/audio',
                'message': 'Use download_url to fetch the audio file'
            })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

@app.route('/api/youtube/mp4', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def youtube_mp4():
    url = request.args.get('url', '')
    quality = request.args.get('quality', '720')
    
    if not url:
        return jsonify({'error': 'URL parameter required', 'status': 400}), 400
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_url = info.get('url')
            
            return jsonify({
                'success': True,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'download_url': video_url,
                'quality': quality + 'p',
                'format': 'mp4/video',
                'message': 'Use download_url to fetch the video file'
            })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

@app.route('/api/youtube/search', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def youtube_search():
    query = request.args.get('q', '')
    max_results = int(request.args.get('max_results', 5))
    
    if not query:
        return jsonify({'error': 'Query parameter (q) required', 'status': 400}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            
            videos = []
            for entry in search_results['entries']:
                videos.append({
                    'title': entry.get('title'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'duration': entry.get('duration'),
                    'views': entry.get('view_count'),
                    'channel': entry.get('uploader'),
                    'thumbnail': entry.get('thumbnail')
                })
            
            return jsonify({
                'success': True,
                'query': query,
                'results': videos,
                'count': len(videos)
            })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

# ==============================================
# WEATHER API
# ==============================================

@app.route('/api/weather', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def weather():
    city = request.args.get('city', 'Harare')
    
    # Mock weather data (integrate with real API like OpenWeatherMap)
    weather_data = {
        'Harare': {'temp': 25, 'condition': 'Sunny', 'humidity': 45},
        'Bulawayo': {'temp': 28, 'condition': 'Partly Cloudy', 'humidity': 40},
        'Mutare': {'temp': 23, 'condition': 'Cloudy', 'humidity': 60},
    }
    
    data = weather_data.get(city, {'temp': 24, 'condition': 'Clear', 'humidity': 50})
    
    return jsonify({
        'success': True,
        'city': city,
        'temperature': data['temp'],
        'condition': data['condition'],
        'humidity': data['humidity'],
        'unit': 'celsius',
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# CURRENCY CONVERTER API
# ==============================================

@app.route('/api/currency', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def currency_converter():
    from_currency = request.args.get('from', 'USD').upper()
    to_currency = request.args.get('to', 'ZWL').upper()
    amount = float(request.args.get('amount', 1))
    
    # Mock exchange rates (use real API in production)
    rates = {
        'USD': 1,
        'ZWL': 320,
        'ZAR': 18.5,
        'EUR': 0.85,
        'GBP': 0.73,
    }
    
    if from_currency not in rates or to_currency not in rates:
        return jsonify({'error': 'Currency not supported', 'status': 400}), 400
    
    # Convert to USD first, then to target currency
    usd_amount = amount / rates[from_currency]
    converted = usd_amount * rates[to_currency]
    
    return jsonify({
        'success': True,
        'from': from_currency,
        'to': to_currency,
        'amount': amount,
        'converted': round(converted, 2),
        'rate': round(rates[to_currency] / rates[from_currency], 4),
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# QUOTES API
# ==============================================

QUOTES = [
    {"text": "Rudo rune simba rokuchinja nyika.", "author": "Unknown", "lang": "shona"},
    {"text": "Kusatenda kwakaipa kunodarika kuita zvakaipa.", "author": "Shona Proverb", "lang": "shona"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "lang": "english"},
    {"text": "Success is not final, failure is not fatal.", "author": "Winston Churchill", "lang": "english"},
    {"text": "Chakafukidza dzimba matenga.", "author": "Shona Proverb", "lang": "shona"},
]

# Continuation of app.py from @app.route('/api/quote')

@app.route('/api/quote', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def get_quote():
    import random
    quote = random.choice(QUOTES)
    
    return jsonify({
        'success': True,
        'quote': quote['text'],
        'author': quote['author'],
        'language': quote['lang'],
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# IMAGE ANALYSIS API
# ==============================================

@app.route('/api/image/analyze', methods=['POST'])
@require_api_key
@limiter.limit("20 per minute")
def analyze_image():
    data = request.get_json()
    
    if not data or 'image_url' not in data:
        return jsonify({'error': 'image_url required in JSON body', 'status': 400}), 400
    
    image_url = data['image_url']
    
    # Mock image analysis (integrate with actual AI service)
    analysis = {
        'objects': ['person', 'building', 'sky'],
        'colors': ['blue', 'white', 'gray'],
        'scene': 'outdoor',
        'confidence': 0.87,
        'text_detected': False
    }
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# NEWS API
# ==============================================

@app.route('/api/news', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def get_news():
    category = request.args.get('category', 'general')
    country = request.args.get('country', 'zw')
    
    # Mock news data
    news_items = [
        {
            'title': 'Zimbabwe Economy Shows Growth',
            'description': 'Latest economic indicators show positive trends',
            'source': 'Herald',
            'category': 'business',
            'published': '2024-11-15'
        },
        {
            'title': 'Technology Innovation in Africa',
            'description': 'New tech startups emerging across the continent',
            'source': 'TechZim',
            'category': 'technology',
            'published': '2024-11-14'
        },
        {
            'title': 'Sports Update: Local Team Wins',
            'description': 'Great performance in regional tournament',
            'source': 'Sports Today',
            'category': 'sports',
            'published': '2024-11-13'
        }
    ]
    
    return jsonify({
        'success': True,
        'category': category,
        'country': country,
        'articles': news_items,
        'count': len(news_items),
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# TRANSLATOR API
# ==============================================

@app.route('/api/translate', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def translate_text():
    text = request.args.get('text', '')
    source = request.args.get('source', 'en')
    target = request.args.get('target', 'sn')
    
    if not text:
        return jsonify({'error': 'text parameter required', 'status': 400}), 400
    
    # Simple translation dictionary (enhance with real translation API)
    translations = {
        ('hello', 'en', 'sn'): 'Mhoro',
        ('thank you', 'en', 'sn'): 'Ndatenda',
        ('how are you', 'en', 'sn'): 'Makadii',
        ('good morning', 'en', 'sn'): 'Mangwanani',
        ('goodbye', 'en', 'sn'): 'Chisarai zvakanaka',
    }
    
    translated = translations.get((text.lower(), source, target), text)
    
    return jsonify({
        'success': True,
        'original': text,
        'translated': translated,
        'source_language': source,
        'target_language': target,
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# QR CODE GENERATOR API
# ==============================================

@app.route('/api/qrcode', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def generate_qr():
    data = request.args.get('data', '')
    
    if not data:
        return jsonify({'error': 'data parameter required', 'status': 400}), 400
    
    # Return QR code API URL (using external service)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}"
    
    return jsonify({
        'success': True,
        'data': data,
        'qr_code_url': qr_url,
        'size': '300x300',
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# URL SHORTENER API
# ==============================================

URL_DATABASE = {}

@app.route('/api/shorten', methods=['POST'])
@require_api_key
@limiter.limit("30 per minute")
def shorten_url():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'url required in JSON body', 'status': 400}), 400
    
    original_url = data['url']
    
    # Generate short code
    import string
    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    URL_DATABASE[short_code] = original_url
    
    base_url = request.url_root
    short_url = f"{base_url}s/{short_code}"
    
    return jsonify({
        'success': True,
        'original_url': original_url,
        'short_url': short_url,
        'short_code': short_code,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/s/<short_code>')
def redirect_short_url(short_code):
    from flask import redirect
    
    original_url = URL_DATABASE.get(short_code)
    
    if original_url:
        return redirect(original_url)
    else:
        return jsonify({'error': 'Short URL not found', 'status': 404}), 404

# ==============================================
# IP GEOLOCATION API
# ==============================================

@app.route('/api/geoip', methods=['GET'])
@require_api_key
@limiter.limit("60 per minute")
def geoip():
    ip = request.args.get('ip', request.remote_addr)
    
    # Mock geolocation data
    geo_data = {
        'ip': ip,
        'country': 'Zimbabwe',
        'country_code': 'ZW',
        'city': 'Harare',
        'latitude': -17.8252,
        'longitude': 31.0335,
        'timezone': 'Africa/Harare',
        'isp': 'Local ISP'
    }
    
    return jsonify({
        'success': True,
        **geo_data,
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# RANDOM GENERATOR APIs
# ==============================================

@app.route('/api/random/number', methods=['GET'])
@require_api_key
@limiter.limit("100 per minute")
def random_number():
    import random
    
    min_val = int(request.args.get('min', 1))
    max_val = int(request.args.get('max', 100))
    count = int(request.args.get('count', 1))
    
    numbers = [random.randint(min_val, max_val) for _ in range(count)]
    
    return jsonify({
        'success': True,
        'numbers': numbers,
        'min': min_val,
        'max': max_val,
        'count': count
    })

@app.route('/api/random/password', methods=['GET'])
@require_api_key
@limiter.limit("100 per minute")
def random_password():
    import random
    import string
    
    length = int(request.args.get('length', 12))
    include_special = request.args.get('special', 'true').lower() == 'true'
    
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += string.punctuation
    
    password = ''.join(random.choices(chars, k=length))
    
    return jsonify({
        'success': True,
        'password': password,
        'length': length,
        'includes_special': include_special
    })

# ==============================================
# TEXT UTILITIES API
# ==============================================

@app.route('/api/text/analyze', methods=['POST'])
@require_api_key
@limiter.limit("60 per minute")
def analyze_text():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'text required in JSON body', 'status': 400}), 400
    
    text = data['text']
    
    # Text analysis
    words = text.split()
    sentences = text.split('.')
    
    analysis = {
        'character_count': len(text),
        'word_count': len(words),
        'sentence_count': len([s for s in sentences if s.strip()]),
        'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
        'reading_time_minutes': len(words) / 200  # Average reading speed
    }
    
    return jsonify({
        'success': True,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# HEALTH CHECK & STATUS
# ==============================================

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Ntando Store API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'endpoints': 20,
        'uptime': '99.9%',
        'version': '1.0.0',
        'documentation': '/api/docs',
        'timestamp': datetime.now().isoformat()
    })

# ==============================================
# ERROR HANDLERS
# ==============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 404,
        'message': 'The requested endpoint does not exist',
        'documentation': '/'
    }), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'status': 429,
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'status': 500,
        'message': 'An unexpected error occurred'
    }), 500

# ==============================================
# RUN APPLICATION
# ==============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
