from flask import Flask, request
import requests
import re

app = Flask(__name__)
app.secret_key = 'checker_2025'

def check_cookies(cookie_str):
    # Parse cookies
    cookies = {}
    for part in cookie_str.split(';'):
        part = part.strip()
        if '=' in part:
            k, v = part.split('=', 1)
            cookies[k] = v

    if 'c_user' not in cookies or 'xs' not in cookies:
        return "DEAD", "Missing c_user or xs"

    session = requests.Session()
    session.cookies.update(cookies)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Referer': 'https://m.facebook.com/',
        'Accept': 'text/html'
    }

    try:
        # Step 1: Open Home
        r = session.get('https://m.facebook.com/home.php', headers=headers, timeout=15, allow_redirects=True)
        if 'login' in r.url.lower() or r.status_code != 200:
            return "DEAD", "Redirected to login"

        # Step 2: Check Name
        name_match = re.search(r'"NAME":"([^"]+)"', r.text)
        if name_match:
            name = name_match.group(1)
            return "ALIVE", f"Logged in as: {name}"
        else:
            return "DEAD", "Name not found"

    except Exception as e:
        return "ERROR", f"Request failed: {str(e)[:50]}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        cookies = request.form.get('cookies', '').strip()
        if not cookies:
            result = '<p style="color:#f00;">Cookies Daalo!</p>'
        else:
            status, msg = check_cookies(cookies)
            color = '#0f0' if status == 'ALIVE' else '#f00' if status == 'DEAD' else '#ff0'
            result = f'<p style="color:{color};font-weight:bold;">[{status}] {msg}</p>'

    return f'''
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>COOKIES CHECKER</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body{{background:#000;color:#0f0;font-family:Courier;text-align:center;padding:20px;}}
      .box{{background:#111;border:1px solid #0f0;padding:20px;border-radius:10px;margin:15px auto;max-width:500px;box-shadow:0 0 20px #0f0;}}
      textarea, button{{width:100%;padding:15px;margin:10px 0;background:#000;border:1px solid #0f0;color:#0f0;border-radius:8px;font-size:16px;}}
      button{{background:#0f0;color:#000;font-weight:bold;}}
      h1{{text-shadow:0 0 25px #0f0;}}
      .alive{{color:#0f0;}} .dead{{color:#f00;}} .error{{color:#ff0;}}
    </style></head><body>
    <h1>COOKIES CHECKER</h1>
    <form method="post">
      <div class="box">
        <textarea name="cookies" rows="6" placeholder="c_user=...; xs=...; fr=..." required>{request.form.get('cookies','')}</textarea>
        <small>SmartCookieWeb → copy(document.cookie)</small>
      </div>
      <button type="submit">CHECK COOKIES</button>
    </form>
    <div class="box">{result}</div>
    <div class="box">
      <small>
        <b>ALIVE</b> = Login successful<br>
        <b>DEAD</b> = Expired / Invalid<br>
        <b>ERROR</b> = Network issue
      </small>
    </div>
    </body></html>
    '''

if __name__ == '__main__':
    print("COOKIES CHECKER → http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)
