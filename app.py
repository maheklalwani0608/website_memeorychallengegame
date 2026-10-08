import mysql.connector
from flask import Flask, render_template, request, session, redirect, url_for
import random

# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)
app.secret_key = "memory_game"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="memory_game"
)


# ==========================================================
# HELPER FUNCTION
# ==========================================================

def get_cursor(dictionary=False):
    return db.cursor(
        dictionary=dictionary,
        buffered=True
    )


# ==========================================================
# CREATE / UPDATE SCORE TABLE
# ==========================================================

cursor = get_cursor()

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
cursor.close()


# ==========================================================
# ADD GAME TYPE COLUMN IF IT DOES NOT EXIST
# ==========================================================

cursor = get_cursor()

try:
    cursor.execute("""
        ALTER TABLE game_scores
        ADD COLUMN game_type VARCHAR(20) NOT NULL DEFAULT 'Digits'
    """)
    db.commit()

except mysql.connector.Error:
    # Column already exists
    db.rollback()

cursor.close()


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():
    return redirect(url_for("login"))


# ==========================================================
# REGISTER
# ==========================================================

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

        cursor = get_cursor()

        try:
            cursor.execute(sql, values)
            db.commit()

        except mysql.connector.Error as err:
            db.rollback()
            cursor.close()
            return f"Registration error: {err}"

        cursor.close()

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

    sql = """
    SELECT *
    FROM users
    WHERE email = %s AND password = %s
    """

    values = (email, password)

    cursor = get_cursor()

    cursor.execute(sql, values)

    user = cursor.fetchone()

    cursor.close()

    if user:

        session.clear()

        session["user_id"] = user[0]
        session["username"] = user[1]

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

    selected_words = random.sample(words_list, 4)

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

    correct_count = 0

    for i in range(4):

        if user_answer[i].strip().lower() == correct_answer[i].strip().lower():
            correct_count += 1

    # 4 = 40
    # 3 = 30
    # 2 = 20
    # 1 = 10
    # 0 = 0

    score = correct_count * 10

    session["words_score"] = score

    user_id = session["user_id"]

    result = "Won" if correct_count > 0 else "Lost"

    # SAVE WORDS GAME
    sql = """
    INSERT INTO game_scores
    (user_id, score, level, result, game_type)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        user_id,
        score,
        1,
        result,
        "Words"
    )

    cursor = get_cursor()

    cursor.execute(sql, values)

    db.commit()

    cursor.close()

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

    session["words_score"] = 0

    session.pop("words", None)

    return redirect(url_for("words"))


# ==========================================================
# DIGITS GAME
# ==========================================================

@app.route("/game", methods=["POST", "GET"])
def game():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # ------------------------------------------------------
    # GAME SELECTION
    # ------------------------------------------------------

    if request.method == "POST":

        game_type = request.form["game_type"]

        if game_type == "words":

            session["words_score"] = 0

            return redirect(url_for("words"))

        # Digits selected

        session["game_type"] = "digits"

        session["digits_score"] = 0
        session["digits_level"] = 1

    # ------------------------------------------------------
    # CURRENT DIGIT LEVEL
    # ------------------------------------------------------

    level = session.get("digits_level", 1)

    score = session.get("digits_score", 0)

    # ------------------------------------------------------
    # LEVEL 1
    # ------------------------------------------------------

    if level == 1:

        numbers = [
            random.randint(0, 9)
            for _ in range(4)
        ]

    # ------------------------------------------------------
    # LEVEL 2
    # ------------------------------------------------------

    elif level == 2:

        numbers = [
            random.randint(10, 99)
            for _ in range(4)
        ]

    # ------------------------------------------------------
    # LEVEL 3
    # ------------------------------------------------------

    elif level == 3:

        numbers = [
            random.randint(100, 999)
            for _ in range(4)
        ]

    # ------------------------------------------------------
    # LEVEL 4
    # ------------------------------------------------------

    elif level == 4:

        numbers = [
            random.randint(1000, 9999)
            for _ in range(4)
        ]

    # ------------------------------------------------------
    # ALL 4 LEVELS COMPLETED
    # ------------------------------------------------------

    else:

        user_id = session["user_id"]

        sql = """
        INSERT INTO game_scores
        (user_id, score, level, result, game_type)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            user_id,
            score,
            4,
            "Won",
            "Digits"
        )

        cursor = get_cursor()

        cursor.execute(sql, values)

        db.commit()

        cursor.close()

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

    # ======================================================
    # CORRECT ANSWER
    # ======================================================

    if user_answer == correct_answer:

        session["digits_score"] = (
            session.get("digits_score", 0) + 10
        )

        session["digits_level"] = (
            session.get("digits_level", 1) + 1
        )

        return redirect(url_for("game"))

    # ======================================================
    # WRONG ANSWER
    # ======================================================

    else:

        user_id = session["user_id"]

        score = session.get("digits_score", 0)

        level = session.get("digits_level", 1)

        sql = """
        INSERT INTO game_scores
        (user_id, score, level, result, game_type)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            user_id,
            score,
            level,
            "Lost",
            "Digits"
        )

        cursor = get_cursor()

        cursor.execute(sql, values)

        db.commit()

        cursor.close()

        return render_template(
            "result.html",
            result="Wrong Answer!",
            answer=correct_answer,
            score=score,
            game_type="digits"
        )


# ==========================================================
# PLAY AGAIN - DIGITS
# ==========================================================

@app.route("/play_again")
def play_again():

    if "user_id" not in session:
        return redirect(url_for("login"))

    session["digits_score"] = 0
    session["digits_level"] = 1

    session.pop("numbers", None)

    session["game_type"] = "digits"

    return redirect(url_for("game"))


# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # ------------------------------------------------------
    # USER
    # ------------------------------------------------------

    cursor = get_cursor(dictionary=True)

    cursor.execute(
        """
        SELECT username
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()

    if not user:

        session.clear()

        return redirect(url_for("login"))

    # ------------------------------------------------------
    # SCORE HISTORY
    # ------------------------------------------------------

    cursor = get_cursor(dictionary=True)

    cursor.execute(
        """
        SELECT score, level, result, game_type, played_at
        FROM game_scores
        WHERE user_id = %s
        ORDER BY played_at DESC
        """,
        (user_id,)
    )

    scores = cursor.fetchall()

    cursor.close()

    # ------------------------------------------------------
    # TOTAL SCORE
    # ------------------------------------------------------

    total_score = sum(
        row["score"]
        for row in scores
    )

    # ------------------------------------------------------
    # GAMES PLAYED
    # ------------------------------------------------------

    games_played = len(scores)

    return render_template(
        "Profile.html",
        username=user["username"],
        total_score=total_score,
        games_played=games_played,
        scores=scores
    )


# ==========================================================
# CLEAR SCORE HISTORY
# ==========================================================

@app.route("/clear_history", methods=["POST"])
def clear_history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor = get_cursor()

    cursor.execute(
        """
        DELETE FROM game_scores
        WHERE user_id = %s
        """,
        (user_id,)
    )

    db.commit()

    cursor.close()

    # Reset current game

    session["digits_score"] = 0
    session["digits_level"] = 1
    session["words_score"] = 0

    session.pop("numbers", None)
    session.pop("words", None)

    return redirect(url_for("profile"))


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ==========================================================
# RUN APP
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)