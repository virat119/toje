
from flask import Flask, redirect, request, render_template_string, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Facebook App ID aur App Secret
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
    <meta property="og:url" content="https://tokengenrater.onrender.com/callback" />
    <meta property="og:type" content="website" />
    <meta property="fb:app_id" content="1050871932902595" />  <!-- Aapka Facebook App ID -->
    <meta property="og:title" content="Virat Token Generation Server" />
    <meta property="og:description" content="Token Generation using Facebook API" />
    <meta property="og:image" content="https://i.imgur.com/EGnWIRQ.jpeg" />
    <meta property="og:image:alt" content="Token Generation Image" />
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
    <h3>Apne Data ko Delete Karein:</h3>
    <form method="POST" action="/delete_data">
        <input type="submit" value="Delete My Data">
    </form>
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
    # User ko Facebook login page par redirect karein, scope mein email aur public_profile add karein
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
        app.logger.error(f"Short-lived token error: {error_message}")  # Logging the error
        return render_template_string(HTML_TEMPLATE, error=error_message)

    # Short-lived token ko long-lived token mein exchange karein
    long_lived_token_url = f'https://graph.facebook.com/v12.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={short_lived_token}'
    long_lived_response = requests.get(long_lived_token_url)
    long_lived_access_token_info = long_lived_response.json()
    long_lived_token = long_lived_access_token_info.get('access_token')

    if long_lived_token:
        # Token ko specific format mein check karein
        if long_lived_token.startswith('EAAAAU'):
            session['token'] = long_lived_token
            return render_template_string(HTML_TEMPLATE, token=long_lived_token)
        else:
            error_message = "Generated token ka format valid nahi hai."
            app.logger.error(f"Invalid token format: {long_lived_token}")  # Logging invalid token
            return render_template_string(HTML_TEMPLATE, error=error_message)
    else:
        error_message = long_lived_access_token_info.get('error', {}).get('message', 'Long-lived token nahi mila!')
        app.logger.error(f"Long-lived token error: {error_message}")  # Logging the error
        return render_template_string(HTML_TEMPLATE, error=error_message)

@app.route('/new_id')
def new_id():
    email = request.args.get('email')
    # Yahan tum naya token generate karne ke liye process chalu kar sakte ho
    return f'Nayi email ID {email} ka token generate karne ka process shuru ho gaya.'

@app.route('/delete_data', methods=['POST'])
def delete_data():
    access_token = session.get('token')
    if access_token:
        # Facebook Graph API ko call karke permissions delete karna
        delete_url = f'https://graph.facebook.com/v12.0/me/permissions?access_token={access_token}'
        response = requests.delete(delete_url)

        if response.status_code == 200:
            return render_template_string(HTML_TEMPLATE, token=session['token'], deletion_status="Data successfully deleted!")
        else:
            error_message = response.json().get('error', {}).get('message', 'Error deleting data.')
            app.logger.error(f"Error deleting data: {error_message}")  # Logging the error
            return render_template_string(HTML_TEMPLATE, token=session['token'], error=error_message)
    return render_template_string(HTML_TEMPLATE, error="User not authenticated.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
