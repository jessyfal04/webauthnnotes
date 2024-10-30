from cryptography.fernet import Fernet
import sqlite3

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
    

# get all note from user table and encrypt it
query = "SELECT * FROM users"
params = ()
result = execute_query(query, params)

for user in result[1]:
	username = user[0]
	note = user[3]
     
	print(username, note)

	# Encrypt the note
	encrypted_note = cipher_suite.encrypt(note.encode())

	# Update the note in the database
	query = "UPDATE users SET note = ? WHERE username = ?"
	params = (encrypted_note, username)
	result = execute_query(query, params)

	
