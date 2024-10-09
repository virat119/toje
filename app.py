
from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/')
def index():
    return '<a href="/login">Login with Facebook</a>'

@app.route('/login')
def login():
    app_id = '1050871932902595'  # Your App ID
    redirect_uri = 'https://tokengenrater.onrender.com/callback'  # Your redirect URI
    return redirect(f'https://www.facebook.com/v17.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope=public_profile,email&response_type=token')

@app.route('/callback')
def callback():
    # The access token will be in the URL fragment, we can't get it via request.args directly
    # So we need to use JavaScript to extract it from the URL
    return '''
    <html>
        <body>
            <h1>Access Token Retrieved</h1>
            <textarea id="token" rows="4" cols="50" readonly></textarea>
            <script>
                const hash = window.location.hash;
                if (hash) {
                    const token = hash.split('&')[0].split('=')[1];
                    document.getElementById('token').value = token;
                }
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(port=5000)
