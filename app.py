from flask import Flask, request, render_template_string, redirect, url_for, session
import json
import random
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # needed for sessions

USERS_FILE = "users.json"

# Ensure users.json exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# Load users
def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        insta_id = request.form.get('insta_id')
        password = request.form.get('instagram_password')
        users = load_users()

        if insta_id in users and users[insta_id] == password:
            session['user'] = insta_id
            session['number'] = random.randint(1, 20)  # game number
            return redirect(url_for('game'))
        else:
            return render_template_string("""
            <script>alert("❌ Invalid login! Check Insta ID and password.");</script>
            <meta http-equiv="refresh" content="0; url=/" />
            """)

    return render_template_string("""
    <html>
    <head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; font-family:sans-serif;'>
        <h1>Login</h1>
        <form method='POST'>
            <input name='insta_id' placeholder='Instagram ID' required><br><br>
            <input type='password' name='password' placeholder='Password' required><br><br>
            <button type='submit'>Login</button>
        </form>
        <p>Want to see/add users? <a href="/admin">Admin Panel</a></p>
    </body>
    </html>
    """)

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
            session['number'] = random.randint(1, 20)  # reset game
    
    return render_template_string(f"""
    <html>
    <head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; font-family:sans-serif;'>
        <h1>Welcome {session['user']}!</h1>
        <p>Guess the number between 1 and 20:</p>
        <form method='POST'>
            <input type='number' name='guess' required min='1' max='20'>
            <button type='submit'>Guess</button>
        </form>
        <h2>{message}</h2>
        <p><a href="/logout">Logout</a></p>
    </body>
    </html>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Admin panel for viewing/adding users
    users = load_users()
    msg = ""
    if request.method == 'POST':
        new_id = request.form.get('new_id')
        new_pass = request.form.get('new_pass')
        if new_id in users:
            msg = "User already exists!"
        else:
            users[new_id] = new_pass
            save_users(users)
            msg = f"User {new_id} added!"

    # Show all users and passwords
    user_list_html = "<ul>"
    for u, p in users.items():
        user_list_html += f"<li>{u} : {p}</li>"
    user_list_html += "</ul>"

    return render_template_string(f"""
    <html>
    <head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; font-family:sans-serif;'>
        <h1>Admin Panel</h1>
        <h2>Add New User</h2>
        <form method='POST'>
            <input name='new_id' placeholder='Instagram ID' required><br><br>
            <input name='new_pass' placeholder='Password' required><br><br>
            <button type='submit'>Add User</button>
        </form>
        <h2>Existing Users</h2>
        {user_list_html}
        <p style='color:green;'>{msg}</p>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    """)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
