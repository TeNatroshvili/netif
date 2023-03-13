from flask_login import UserMixin
from flask_bcrypt import bcrypt
import uuid

from mongodb import users

class User(UserMixin):

    def __init__(self, username, password, _id=None):
        self.username = username
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self._id

    @classmethod
    def get_by_username(cls, username):
        data = users.find_one({"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = users.find_one({"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(username, password):
        verify_user = User.get_by_username(username)
        if verify_user is not None:
            return bcrypt.checkpw(password.encode('utf-8'), verify_user.password)
        return False

    @staticmethod
    def change_password(username, password, newpass):
        user = User.get_by_username(username)
        if User.login_valid(username, password):
            users.update_one({'_id': user._id}, 
                                {"$set": {"password": bcrypt.hashpw((newpass).encode('utf-8'), bcrypt.gensalt())}},
                                 upsert=True)
            return True
        else:
            return False

    def json(self):
        return {
            "username": self.username,
            "_id": self._id,
            "password": bcrypt.hashpw((self.password).encode('utf-8'), bcrypt.gensalt())
        }