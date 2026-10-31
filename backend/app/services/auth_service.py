import os, sqlite3, hashlib, hmac, base64, json, time, secrets
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "netcoop_users.db"
SECRET = os.getenv("NETCOOP_AUTH_SECRET", "CHANGE_THIS_NETCOOP_SECRET_BEFORE_DEPLOYMENT")

def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    return conn

def _hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
    return base64.urlsafe_b64encode(salt + digest).decode()

def _verify_password(password, encoded):
    try:
        raw = base64.urlsafe_b64decode(encoded.encode())
        salt, expected = raw[:16], raw[16:]
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def create_user(name, email, password):
    name, email = name.strip(), email.strip().lower()
    if len(name) < 2 or len(name) > 80:
        raise ValueError("Name must be between 2 and 80 characters.")
    if "@" not in email or len(email) > 254:
        raise ValueError("Enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    conn = _db()
    try:
        cur = conn.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                           (name, email, _hash_password(password)))
        conn.commit()
        return {"id": cur.lastrowid, "name": name, "email": email}
    except sqlite3.IntegrityError:
        raise ValueError("An account with this email already exists.")
    finally:
        conn.close()

def authenticate(email, password):
    conn = _db()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
        if not row or not _verify_password(password, row["password_hash"]):
            return None
        return {"id": row["id"], "name": row["name"], "email": row["email"]}
    finally:
        conn.close()

def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def issue_token(user):
    payload = {"sub": user["id"], "name": user["name"], "email": user["email"],
               "exp": int(time.time()) + 60 * 60 * 12}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).digest())
    return body + "." + signature

def read_token(token):
    try:
        body, signature = token.split(".", 1)
        expected = _b64(hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if payload["exp"] < int(time.time()):
            return None
        return {"id": payload["sub"], "name": payload["name"], "email": payload["email"]}
    except Exception:
        return None
