from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import generate_with_mlx
from datetime import timedelta
import mysql.connector
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True
)

app.config["JWT_SECRET_KEY"] = "test"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_SECURE"] = False  # True jika HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

jwt = JWTManager(app)

DATABASE = "database.db"


def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="local_llm"
    )
    return conn


@app.route("/")
@jwt_required()
def home():
    user_id = get_jwt_identity()

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, title, created_at
        FROM conversations
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    conversations = cursor.fetchall()
    return render_template("home.html", user_id=user_id, conversations=conversations)



@app.route("/history/<int:id>")
@jwt_required()
def conversation(id):
    user_id = int(get_jwt_identity())

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Pastikan conversation milik user
    cursor.execute(
        """
        SELECT id FROM conversations
        WHERE id = %s AND user_id = %s
        """,
        (id, user_id)
    )
    if not cursor.fetchone():
        cursor.close()
        db.close()
        return "Unauthorized", 403

    # Ambil messages
    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        """,
        (id,)
    )
    messages = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(messages)



@app.route("/history", methods=["GET"])
@jwt_required()
def get_conversations():
    user_id = int(get_jwt_identity())

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, title, created_at
        FROM conversations
        WHERE user_id = %s
        ORDER BY created_at DESC
        """
        , (user_id,)
    )

    conversations = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(conversations)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user is None or not check_password_hash(user["password_hash"], password):
                return render_template(
                "login.html",
                error_username="Invalid username or password",
                username=username,
            )

        access_token = create_access_token(identity=str(user["id"]))

        response = redirect(url_for("home"))
        set_access_cookies(response, access_token)
        return response

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error_username = None
    error_password = None
    username = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # ❌ Password tidak cocok
        if password != confirmation:
            error_password = "Password dan konfirmasi password tidak sama"

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # ❌ Username sudah dipakai
        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (username,)
        )
        existing_user = cursor.fetchone()
        

        if existing_user:
            error_username = "Username sudah digunakan"

        # Jika ada error, render ulang form
        if error_username or error_password:
            cursor.close()
            db.close()
            return render_template(
                "register.html",
                error_username=error_username,
                error_password=error_password,
                username=username,
            )

        # ✅ Simpan user
        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("login"))

    return render_template("register.html")




@app.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()  # ✅ Gunakan JSON, bukan form!
        
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        prompt = data.get("prompt")
        conversation_id = data.get("conversation_id")  # None jika chat baru

        if not prompt or not isinstance(prompt, str) or not prompt.strip():
            return jsonify({"error": "Valid 'prompt' is required"}), 400

        db = get_db()
        cursor = db.cursor()

        # 🔹 CHAT BARU
        if conversation_id is None:
            logger.info(f"User {user_id} memulai chat baru dengan prompt: {prompt[:30]}...")
            cursor.execute(
                "INSERT INTO conversations (user_id, title) VALUES (%s, %s)",
                (user_id, prompt[:50] or "New Chat")
            )
            conversation_id = cursor.lastrowid
        else:
            # 🔹 Validasi bahwa conversation_id milik user ini
            cursor.execute(
                "SELECT id FROM conversations WHERE id = %s AND user_id = %s",
                (conversation_id, user_id)
            )
            if not cursor.fetchone():
                logger.warning(f"User {user_id} mengakses conversation {conversation_id} yang tidak sah")
                return jsonify({"error": "Invalid conversation ID"}), 403

        # Simpan pesan user
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
            (conversation_id, "user", prompt)
        )

        # Generate AI response
        logger.info(f"Memanggil LLM untuk prompt: {prompt[:50]}...")
        ai_response = generate_with_mlx(prompt)
        logger.info(f"LLM merespons: {ai_response[:50]}...")

        # Simpan respons AI
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
            (conversation_id, "assistant", ai_response)
        )

        db.commit()
        cursor.close()
        db.close()

        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "user_message": prompt,
            "assistant_message": ai_response
        })

    except Exception as e:
        logger.exception("Terjadi error di /chat endpoint")  # ← Ini akan print full traceback!
        # Jangan kembalikan detail error ke client di production
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
    

@app.route("/logout", methods=["POST"])
def logout():
    response = redirect(url_for("login"))
    unset_jwt_cookies(response)
    return response

if __name__ == "__main__":
    app.run(debug=True)
