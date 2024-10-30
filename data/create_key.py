from cryptography.fernet import Fernet

# Génère une clé de chiffrement
key = Fernet.generate_key()

# Enregistre la clé dans un fichier
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Clé enregistrée dans 'secret.key'")
