@app.route('/game')
def game():
    if 'user' not in session:
        return redirect(url_for('login'))

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
                justify-content: flex-start;
                margin:0; padding:0;
            }}
            h1 {{
                margin-top:20px;
                text-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            }}
            #gameContainer {{
                background:#70c5ce;
                border-radius:20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
                width: 400px;
                padding: 10px;
                margin:20px 0;
            }}
            canvas {{
                display:block;
                background: #70c5ce;
                border-radius: 10px;
                margin:0 auto;
            }}
            p {{
                font-size:16px;
            }}
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
            a:hover {{
                background:#ff3b2e;
            }}
        </style>
    </head>
    <body>
        <h1>Flappy Bird 🎮</h1>
        <p>Player: {session['user']}</p>
        <div id="gameContainer">
            <canvas id="gameCanvas" width="400" height="600"></canvas>
            <p>Score: <span id="score">0</span></p>
            <p id="message"></p>
        </div>
        <a href="/logout">Logout</a>

        <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const messageEl = document.getElementById('message');

        let bird = {{ x:50, y:300, width:30, height:30, velocity:0, gravity:0.6, lift:-10 }};
        let pipes = [];
        let frame = 0;
        let score = 0;
        let gameOver = false;

        document.addEventListener('keydown', e => {{ if(e.code==='Space') flap(); }});
        document.addEventListener('click', flap);

        function flap() {{
            bird.velocity = bird.lift;
        }}

        function createPipe() {{
            let gap = 150;
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
        }}

        function draw() {{
            ctx.clearRect(0,0,canvas.width,canvas.height);

            // Bird
            ctx.fillStyle = 'yellow';
            ctx.fillRect(bird.x, bird.y, bird.width, bird.height);

            // Pipes
            ctx.fillStyle = 'green';
            pipes.forEach(pipe => {{
                ctx.fillRect(pipe.x, pipe.y, pipe.width, pipe.height);
            }});

            // Update bird
            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            // Update pipes
            pipes.forEach(pipe => {{ pipe.x -= 2; }});

            // Remove offscreen pipes
            pipes = pipes.filter(pipe => pipe.x + pipe.width > 0);

            // Add new pipe every 120 frames
            if(frame % 120 === 0) createPipe();

            // Check collision
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

            // Update score
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

        function gameLoop() {{
            if(gameOver) resetGame();
            draw();
        }}

        draw();
        </script>
    </body>
    </html>
    """)
