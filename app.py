

from flask import Flask, redirect, request, render_template_string, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Aapka Facebook App ID aur App Secret
APP_ID = '1050871932902595'  # Aapka Facebook App ID
APP_SECRET = '6911ba331b1ed97099c5366d36afb3e2'  # Aapka Facebook App Secret
REDIRECT_URI = 'https://tokengenrater.onrender.com/callback'  # Render par callback URL

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Virat Token Generation Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            text-align: center;
            padding-top: 50px;
            color: #333;
        }
        h2 {
            color: #4CAF50;
        }
        form {
            margin-top: 30px;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        .token-box {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 2px solid #4CAF50;
        }
        .error {
            color: red;
        }
        .footer {
            margin-top: 50px;
            font-size: 12px;
            color: #aaa;
        }
    </style>
    <script>
        function removeTokenAfterTimeout() {
            setTimeout(function() {
                document.getElementById('token-box').style.display = 'none';
                document.getElementById('new-id-form').style.display = 'block';  // New ID form dikhana
            }, 60000);  // 60 seconds ke baad token box hide ho jayega
        }
    </script>
</head>
<body onload="removeTokenAfterTimeout()">
    <h2>Virat Token Generate Server</h2>
    <form method="GET" action="/login">
        <input type="submit" value="Get Access Token">
    </form>
    {% if token %}
        <div id="token-box" class="token-box">
            <h3>Aapka Long-Lived Access Token:</h3>
            <p>{{ token }}</p>
        </div>
    {% endif %}
    {% if error %}
        <div class="error">
            <h3>Error:</h3>
            <p>{{ error }}</p>
        </div>
    {% endif %}
    <div id="new-id-form" style="display:none; margin-top: 20px;">
        <h3>Nayi Email ID daal kar naya token hasil karein:</h3>
        <form method="GET" action="/new_id">
            <input type="text" name="email" placeholder="Nayi Email ID" required>
            <input type="submit" value="Naya Token Hasil Karein">
        </form>
    </div>
    <div class="footer">
        <p>Token expire nahi hoga, screen se 60 seconds ke baad gayab ho jayega.</p>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login')
def login():
    # User ko Facebook login page par redirect karein
    return redirect(f'https://www.facebook.com/v12.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=email,public_profile')

@app.route('/callback')
def callback():
    code = request.args.get('code')

    # Short-lived access token ke liye code ko exchange karein
    token_url = f'https://graph.facebook.com/v12.0/oauth/access_token?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&client_secret={APP_SECRET}&code={code}'
    response = requests.get(token_url)
    access_token_info = response.json()

    short_lived_token = access_token_info.get('access_token')

    if not short_lived_token:
        error_message = access_token_info.get('error', {}).get('message', 'Short-lived token nahi mila!')
        return render_template_string(HTML_TEMPLATE, error=error_message)

    # Short-lived token ko long-lived token mein exchange karein
    long_lived_token_url = f'https://graph.facebook.com/v12.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={short_lived_token}'
    long_lived_response = requests.get(long_lived_token_url)
    long_lived_access_token_info = long_lived_response.json()
    long_lived_token = long_lived_access_token_info.get('access_token')

    # Yahan ye check karein ki token mil gaya ya nahi
    if long_lived_token:
        # Token ko specific format mein check karein
        if long_lived_token.startswith('EAAAAU'):
            session['token'] = long_lived_token
            return render_template_string(HTML_TEMPLATE, token=long_lived_token)
        else:
            error_message = "Generated token ka format valid nahi hai."
            return render_template_string(HTML_TEMPLATE, error=error_message)
    else:
        error_message = long_lived_access_token_info.get('error', {}).get('message', 'Koi error aayi hai!')
        return render_template_string(HTML_TEMPLATE, error=error_message)

@app.route('/new_id')
def new_id():
    email = request.args.get('email')
    # Yahan tum naya token generate karne ke liye process chalu kar sakte ho
    # Bas ab yahan Facebook login ka process follow karo nayi email ke liye
    return f'Nayi email ID {email} ka token generate karne ka process shuru ho gaya hai.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
