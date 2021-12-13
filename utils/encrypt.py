import bcrypt


def check_password(password: str, hashed: str) -> bool:
    password = password.encode("utf-8")
    hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password, hashed)


def encrypt_password(password: str) -> str:
    password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode("utf-8")


def encrypt_string(string: str) -> str:
    return encrypt_password(string)
