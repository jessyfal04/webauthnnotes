from flask import Flask, jsonify, request, session
import sqlite3
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response, options_to_json
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, UserVerificationRequirement
import secret
from cryptography.fernet import Fernet

# Variables
app = Flask(__name__)
app.secret_key = secret.secret_key

with open("/home/yepssy/code/webauthnnotes/data/secret.key", "rb") as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# Database Connection
def get_db_connection():
    conn = sqlite3.connect('/home/yepssy/code/webauthnnotes/data/webauthnnotes.sqlite3')
    return conn

def execute_query(query, params):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return (True, result)
    except Exception as e:
        return (False, str(e))        

# Hello World
@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"code": "success", "data": "Hello, World, on webauthnnotes!"})

# WebAuthn
# Register Begin
@app.route('/webauthn/register/begin', methods=['POST'])
def register_begin():
    data = request.get_json() 
    username = data.get('username').strip().lower()

    # Verify if the username not empty and only contains letters and digits
    if not username or not username.isalnum():
        return jsonify({"code": "error", "message": "Invalid username, it must be not empty and only contains letters and digits", "data": None})

    # Verify if the username is already registered
    query = "SELECT * FROM users WHERE username = ?"
    params = (username,)
    result = execute_query(query, params)

    if result[1]:
        return jsonify({"code": "error", "message": "Username already exists", "data": None})
    
    # Generate Registration Options
    options = generate_registration_options(
        rp_id = "jessyfal04.dev",
        rp_name = "WebAuthnNotes",
        user_name = username
    )

    session['current_registration_challenge'] = options.challenge
    session['current_registration_username'] = username

    return jsonify({"code": "success", "message":"", "data": options_to_json(options)})

# Register Complete
@app.route('/webauthn/register/complete', methods=['POST'])
def register_complete():
    data = request.get_json()
    credential = data.get('credential')

    username = session['current_registration_username']
    expected_challenge = session['current_registration_challenge']
    
    try:
        verification = verify_registration_response(
            credential = credential,
            expected_challenge = expected_challenge,
            expected_rp_id = "jessyfal04.dev",
            expected_origin = "https://jessyfal04.dev",
            require_user_verification = True
        )
    except Exception as e:
        return jsonify({"code": "error", "message": str(e), "data": None})

    # Save the public key and username and credential_id in db ; byte to base64
    public_key = verification.credential_public_key
    credential_id = verification.credential_id
    
    query = "INSERT INTO users (username, public_key, credential_id, note) VALUES (?, ?, ?, ?)"
    params = (username, public_key, credential_id, cipher_suite.encrypt(f"Hello, I'm {username}...".encode()))
    result = execute_query(query, params)

    if result[0]:
        # Delete session variables
        del session['current_registration_challenge']
        del session['current_registration_username']

        # Set the session variable
        session["username"] = username
    
        return jsonify({"code": "success", "message": f"User {username} registered successfully", "data": None})
    else:
        return jsonify({"code": "error", "message": str(result[1]), "data": None})

# Authenticate Begin
@app.route('/webauthn/authenticate/begin', methods=['POST'])
def authenticate_begin():
    data = request.get_json()
    username = data.get('username').strip().lower()

    # Verify if the username is already registered
    query = "SELECT credential_id, public_key FROM users WHERE username = ?"
    params = (username,)
    result = execute_query(query, params)

    if not result[1]:
        return jsonify({"code": "error", "message": "Username not found", "data": None})

    # Generate Authentication Options
    options = generate_authentication_options(
        rp_id = "jessyfal04.dev",
        allow_credentials = [PublicKeyCredentialDescriptor(id=result[1][0][0])],
        user_verification = UserVerificationRequirement.REQUIRED
    )

    session['current_authentication_challenge'] = options.challenge
    session['current_authentication_username'] = username
    session['current_authentication_public_key'] = result[1][0][1]

    return jsonify({"code": "success", "message":"", "data": options_to_json(options)})

# Authenticate Complete
@app.route('/webauthn/authenticate/complete', methods=['POST'])
def authenticate_complete():
    data = request.get_json()
    credential = data.get('credential')

    username = session['current_authentication_username']
    expected_challenge = session['current_authentication_challenge']
    credential_public_key = session['current_authentication_public_key']
    
    try:
        verification = verify_authentication_response(
            credential = credential,
            expected_challenge = expected_challenge,
            expected_rp_id = "jessyfal04.dev",
            expected_origin = "https://jessyfal04.dev",
            require_user_verification=True,
            credential_public_key=credential_public_key,
            credential_current_sign_count=0
        )
    except Exception as e:
        return jsonify({"code": "error", "message": str(e), "data": None})

    # Delete session variables
    del session['current_authentication_challenge']
    del session['current_authentication_username']
    del session['current_authentication_public_key']

    # Set the session variable
    session["username"] = username

    return jsonify({"code": "success", "message": f"User {username} authenticated successfully", "data": None})

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    if session.get('username'):
        del session['username']
        return jsonify({"code": "success", "message": "User logged out successfully", "data": None})
    else:
        return jsonify({"code": "error", "message": "User not logged in", "data": None})

# User exists
@app.route('/user-exists', methods=['POST'])
def user_exists():
    data = request.get_json()
    username = data.get('username').strip().lower()

    query = "SELECT * FROM users WHERE username = ?"
    params = (username,)
    result = execute_query(query, params)

    return jsonify({"code": "success", "message": "", "data": {"exists": bool(result[1])}})

# Who Am I
@app.route('/whoami', methods=['GET'])
def whoami():
    username = session.get('username')
    return jsonify({"code": "success", "message": "", "data": {"username": username}})

# Note
# Get Note
@app.route('/note', methods=['GET'])
def get_note():
    username = session.get('username')

    if not username:
        return jsonify({"code": "error", "message": "User not logged in", "data": None})

    query = "SELECT note FROM users WHERE username = ?"
    params = (username,)
    result = execute_query(query, params)

    if result[0]:
        note = cipher_suite.decrypt(result[1][0][0]).decode()
        return jsonify({"code": "success", "message": "", "data": {"note": note}})
    else:
        return jsonify({"code": "error", "message": str(result[1]), "data": None})


# Set Note
@app.route('/note', methods=['POST'])
def set_note():
    data = request.get_json()
    note = data.get('note')

    username = session.get('username')

    if not username:
        return jsonify({"code": "error", "message": "User not logged in", "data": None})

    note = cipher_suite.encrypt(note.encode())

    # update
    query = "UPDATE users SET note = ? WHERE username = ?"
    params = (note, username)
    result = execute_query(query, params)

    if result[0]:
        return jsonify({"code": "success", "message": "Note updated successfully", "data": None})
    else:
        return jsonify({"code": "error", "message": str(result[1]), "data": None})

if __name__ == "__main__":
    app.run(debug=True)  # Debug mode can help in development