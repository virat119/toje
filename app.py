
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Token Generator</title>
    </head>
    <body>
        <h1>Facebook Token Generator</h1>
        <button id="loginBtn">Login with Facebook</button>
        <div id="tokenDisplay" style="display:none;">
            <h2>Your Access Token:</h2>
            <textarea id="token" rows="4" cols="50" readonly></textarea>
        </div>

        <script>
            const appId = '1050871932902595'; // Yahan apna App ID daalein
            const redirectUri = 'https://tokengenrater.onrender.com/callback'; // Yahan apna redirect URI daalein

            document.getElementById('loginBtn').onclick = function() {
                const authUrl = `https://www.facebook.com/v17.0/dialog/oauth?client_id=${appId}&redirect_uri=${redirectUri}&scope=public_profile,email&response_type=token`;
                window.location.href = authUrl;
            };

            // Access Token retrieve karne ka process
            window.onload = function() {
                const hash = window.location.hash;
                if (hash) {
                    const token = hash.split('&')[0].split('=')[1];
                    document.getElementById('token').value = token;
                    document.getElementById('tokenDisplay').style.display = 'block';
                }
            };
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Port 5000 par run karega
