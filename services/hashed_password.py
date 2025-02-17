from streamlit_authenticator import Hasher

# Lista de contraseñas que deseas hashear
passwords = ["contraseña1", "contraseña2"]

# Generar los hashes usando el método hash() de la clase Hasher
hashed_passwords = [Hasher.hash(password) for password in passwords]

# Imprimir los hashes
print("Hashes generados:")
for password, hashed in zip(passwords, hashed_passwords):
    print(f"Contraseña: {password} -> Hash: {hashed}")