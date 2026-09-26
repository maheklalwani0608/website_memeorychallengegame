import mysql.connector
from flask import Flask, render_template, request, session, redirect, url_for
import random

# ---------------- DATABASE CONNECTION ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="memory_game"
)

cursor = db.cursor()

app = Flask(__name__)
app.secret_key = "memory_game"


# ---------------- SCORE TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS game_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    level INT NOT NULL,
    result VARCHAR(20),
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

db.commit()


# ==========================================================
# REGISTER
# ==========================================================
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        sql = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """

        values = (username, email, password)

        cursor.execute(sql, values)
        db.commit()

        return render_template("login.html")

    return render_template("register.html")


# ==========================================================
# LOGIN
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"]
    password = request.form["password"]

    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    values = (email, password)

    cursor.execute(sql, values)
    user = cursor.fetchone()

    if user:

        # Clear previous user's session
        session.clear()

        # Store current user's information
        session["user_id"] = user[0]
        session["username"] = user[1]

        # Fresh game scores
        session["digits_score"] = 0
        session["digits_level"] = 1
        session["words_score"] = 0

        return render_template(
            "dashboard.html",
            username=user[1]
        )

    else:
        return "try again"


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username")
    )


# ==========================================================
# WORDS GAME
# ==========================================================

@app.route("/words")
def words():

    if "user_id" not in session:
        return redirect(url_for("login"))

    words_list = [
        "Apple",
        "Tiger",
        "Laptop",
        "Garden",
        "Camera",
        "Rainbow",
        "School",
        "Mountain",
        "Elephant",
        "Notebook"
    ]

    # Generate exactly 4 random words
    selected_words = random.sample(words_list, 4)

    # Store these 4 words
    session["words"] = selected_words

    return render_template(
        "words.html",
        words=selected_words
    )


# ==========================================================
# CHECK WORDS ANSWER
# ==========================================================

@app.route("/check_words", methods=["POST"])
def check_words():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_answer = [
        request.form["word1"],
        request.form["word2"],
        request.form["word3"],
        request.form["word4"]
    ]

    correct_answer = session.get("words", [])

    # Count individually correct answers
    correct_count = 0

    for i in range(4):

        if user_answer[i].strip().lower() == correct_answer[i].strip().lower():
            correct_count += 1

    # ------------------------------------------------------
    # WORDS SCORE
    # 4 correct = 40
    # 3 correct = 30
    # 2 correct = 20
    # 1 correct = 10
    # 0 correct = 0
    # ------------------------------------------------------

    score = correct_count * 10

    # Save this round's score
    session["words_score"] = score

    # Save result in database
    user_id = session["user_id"]

    result = "Won" if correct_count > 0 else "Lost"

    sql = """
    INSERT INTO game_scores (user_id, score, level, result)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        user_id,
        score,
        1,
        result
    )

    cursor.execute(sql, values)
    db.commit()

    # Result message
    if correct_count == 4:
        message = "Correct! 🎉"
    elif correct_count > 0:
        message = f"{correct_count} out of 4 correct! 🎯"
    else:
        message = "Wrong Answer!"

    return render_template(
        "result.html",
        result=message,
        answer=correct_answer,
        score=score,
        game_type="words"
    )


# ==========================================================
# WORDS PLAY AGAIN
# ==========================================================

@app.route("/words/play_again")
def words_play_again():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Start the new Words round from 0
    session["words_score"] = 0

    # Generate a completely new set of 4 words
    return redirect(url_for("words"))


# ==========================================================
# DIGITS GAME
# ==========================================================

@app.route("/game", methods=["POST", "GET"])
def game():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # If user selected a game type from dashboard
    if request.method == "POST":

        game_type = request.form["game_type"]

        if game_type == "words":

            session["words_score"] = 0

            return redirect(url_for("words"))

        # Digits selected
        session["game_type"] = "digits"

        # Start Digits fresh
        session["digits_score"] = 0
        session["digits_level"] = 1

    # ---------------- DIGITS ----------------

    level = session.get("digits_level", 1)

    score = session.get("digits_score", 0)

    if level == 1:

        numbers = [
            random.randint(0, 9)
            for _ in range(4)
        ]

    elif level == 2:

        numbers = [
            random.randint(10, 99)
            for _ in range(4)
        ]

    elif level == 3:

        numbers = [
            random.randint(100, 999)
            for _ in range(4)
        ]

    elif level == 4:

        numbers = [
            random.randint(1000, 9999)
            for _ in range(4)
        ]

    else:

        return render_template(
            "result.html",
            result="Congratulations! 🎉",
            answer=["You completed all levels!"],
            score=score,
            game_type="digits"
        )

    session["numbers"] = numbers

    return render_template(
        "game.html",
        numbers=numbers,
        level=level
    )


# ==========================================================
# CHECK DIGITS ANSWER
# ==========================================================

@app.route("/check", methods=["POST"])
def check():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_answer = [
        request.form["num1"],
        request.form["num2"],
        request.form["num3"],
        request.form["num4"]
    ]

    correct_answer = session.get("numbers", [])

    correct_answer = [
        str(i)
        for i in correct_answer
    ]

    # ---------------- CORRECT ----------------

    if user_answer == correct_answer:

        # +10 for correct level
        session["digits_score"] = session.get("digits_score", 0) + 10

        # Next level
        session["digits_level"] = session.get("digits_level", 1) + 1

        return redirect(url_for("game"))

    # ---------------- WRONG ----------------

    else:

        user_id = session["user_id"]

        score = session.get("digits_score", 0)
        level = session.get("digits_level", 1)

        sql = """
        INSERT INTO game_scores (user_id, score, level, result)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            user_id,
            score,
            level,
            "Lost"
        )

        cursor.execute(sql, values)
        db.commit()

        return render_template(
            "result.html",
            result="Wrong Answer!",
            answer=correct_answer,
            score=score,
            game_type="digits"
        )


# ==========================================================
# RUN APP
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)