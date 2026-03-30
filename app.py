from flask import Flask, request, render_template_string, redirect, url_for, session
import json
import os
import random

app = Flask(__name__)
app.secret_key = "supersecretkey123"

USERS_FILE = "users.json"

# Auto-create users.json if missing
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ===== SIGNUP / LOGIN =====
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        insta_id = request.form.get('insta_id')
        password = request.form.get('password')
        users = load_users()

        # Add new user if not exist → always pending approval
        if insta_id not in users:
            users[insta_id] = {"password": password, "approved": None}
            save_users(users)

        user = users[insta_id]

        if user['approved'] is True:
            session['user'] = insta_id
            session['number'] = random.randint(1, 20)
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
    <head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; font-family:sans-serif;'>
        <h1>Login / Request Access</h1>
        <form method='POST'>
            <input name='insta_id' placeholder='Instagram ID' required><br><br>
            <input type='password' name='password' placeholder='Password' required><br><br>
            <button type='submit'>Submit</button>
        </form>
        <p>Admin? <a href="/admin">Go to Admin Panel</a></p>
    </body>
    </html>
    """)

# ===== MINI GAME =====
@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = ""
    if request.method == 'POST':
        guess = int(request.form.get('guess'))
        number = session['number']
        if guess < number:
            message = "Too low! 📉"
        elif guess > number:
            message = "Too high! 📈"
        else:
            message = f"🎉 Congrats {session['user']}! You guessed it!"
            session['number'] = random.randint(1, 20)

    return render_template_string(f"""
    <html>
    <body style='text-align:center; font-family:sans-serif;'>
        <h1>Welcome {session['user']}!</h1>
        <p>Guess the number between 1 and 20:</p>
        <form method='POST'>
            <input type='number' name='guess' min='1' max='20' required>
            <button type='submit'>Guess</button>
        </form>
        <h2>{message}</h2>
        <p><a href="/logout">Logout</a></p>
    </body>
    </html>
    """)

# ===== ADMIN PANEL =====
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    master_pass = "slicingyourlife"

    # Check master password
    if request.method == 'POST' and 'master' in request.form:
        entered = request.form.get('master')
        if entered != master_pass:
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

    # Admin sees all pending users
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

    pending = {u:d for u,d in users.items() if d['approved'] is None}
    pending_html = ""
    for u in pending:
        pending_html += f"""
        <li>{u} - Password: {users[u]['password']} - 
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

if __name__ == '__main__':
    app.run(debug=True)
