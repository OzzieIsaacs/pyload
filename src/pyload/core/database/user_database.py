import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..utils.struct.style import style


# TODO: rewrite using scrypt or argon2_cffi
def _salted_password(password, salt):
    # Use PBKDF2 via cryptography to derive a 32-byte key with 100,000 iterations (SHA-256)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes.fromhex(salt),
        iterations=100000,
    )
    dk = kdf.derive(password.encode())
    return salt + dk.hex()


def _gensalt():
    return os.urandom(16).hex()


def _check_password(hashed, clear):
    salt = hashed[:32]
    to_compare = _salted_password(clear, salt)

    return hashed == to_compare


class UserDatabaseMethods:
    @style.queue
    def check_auth(self, user, password):
        self.c.execute(
            "SELECT id, name, password, role, permission, template, email FROM users WHERE name=?",
            (user,),
        )
        r = self.c.fetchone()
        if not r:
            return {}

        stored_password = r[2]
        if not _check_password(stored_password, password):
            return {}

        return User(r[0], r[1], r[2], r[3], r[4], r[5], r[6])

    @style.queue
    def load_user(self, user_id):
        self.c.execute(
            "SELECT id, name, password, role, permission, template, email FROM users WHERE id=?",
            (user_id,),
        )
        r = self.c.fetchone()
        if not r:
            return {}
        return User(r[0], r[1], r[2], r[3], r[4], r[5], r[6])

    '''@style.queue
    def load_user_by_name(self, user_name):
        self.c.execute(
            "SELECT id, name, password, role, permission, template, email FROM users WHERE name=?",
            (user_name,),
        )
        r = self.c.fetchone()
        if not r:
            return {}
        return {
            "id": r[0],
            "name": r[1],
            "role": r[3],
            "permission": r[4],
            "template": r[5],
            "email": r[6],
        }'''

    @style.queue
    def add_user(self, user, password, role=0, perms=0, reset=False):
        salt_pw = _salted_password(password, _gensalt())

        self.c.execute("SELECT name FROM users WHERE name=?", (user,))
        if self.c.fetchone() is not None:
            if reset:
                self.c.execute(
                    "UPDATE users SET password=?, role=?, permission=? WHERE name=?",
                    (salt_pw, role, perms, user),
                )
                return True
            else:
                return False
        else:
            self.c.execute(
                "INSERT INTO users (name, password, role, permission) VALUES (?, ?, ?, ?)",
                (user, salt_pw, role, perms),
            )
            return True

    @style.queue
    def change_password(self, user, old_password, new_password):
        self.c.execute("SELECT id, name, password FROM users WHERE name=?", (user,))
        r = self.c.fetchone()
        if not r:
            return False

        stored_password = r[2]
        if not _check_password(stored_password, old_password):
            return False

        newpw = _salted_password(new_password, _gensalt())

        self.c.execute("UPDATE users SET password=? WHERE name=?", (newpw, user))
        return True

    @style.async_
    def set_permission(self, user, perms):
        self.c.execute("UPDATE users SET permission=? WHERE name=?", (perms, user))

    @style.async_
    def set_role(self, user, role):
        self.c.execute("UPDATE users SET role=? WHERE name=?", (role, user))

    @style.queue
    def user_exists(self, user):
        self.c.execute("SELECT name FROM users WHERE name=?", (user,))
        return self.c.fetchone() is not None

    @style.queue
    def list_users(self):
        self.c.execute("SELECT name FROM users")
        users = []
        for row in self.c:
            users.append(row[0])
        return users

    @style.queue
    def get_all_user_data(self):
        self.c.execute("SELECT id, name, permission, role, template, email FROM users")
        user = {}
        for r in self.c:
            user[r[0]] = {
                "name": r[1],
                "permission": r[2],
                "role": r[3],
                "template": r[4],
                "email": r[5],
            }

        return user

    @style.queue
    def get_user_id(self, user):
        self.c.execute("SELECT id, name FROM users WHERE name=?", (user,))
        r = self.c.fetchone()
        if not r:
            return False
        else:
            return r[0]

    @style.queue
    def remove_user(self, user):
        self.c.execute("DELETE FROM users WHERE name=?", (user,))
        return self.c.rowcount > 0

class User():

    def __init__(self, id, name, password, role, permission, template, email):
        self.id = id
        self.name = name
        self.password = password
        self.role = role
        self.permission = permission
        self.template = template
        self.email = email

    @property
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_admin(self):
        return self.role == 0,
