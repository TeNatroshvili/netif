# ---------------------------------------------------------
# Model for a single User for the Flask Login
# ---------------------------------------------------------
# author:   Baumann Danièl
# created:  2023-03-10
# version:  1.1
# ---------------------------------------------------------

from flask_login import UserMixin
from flask_bcrypt import bcrypt
import uuid

from mongodb import users

class User(UserMixin):

    # constructor for a User Object
    def __init__(self, username, password, _id=None):
        self.username = username
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    # must have functions from flask_login
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self._id

    # get_by_username()
    # 
    # searches for the given username
    # 
    # params: username - username to serach for
    # 
    # returns: the user object when the username exists
    @classmethod
    def get_by_username(cls, username):
        data = users.find_one({"username": username})
        if data is not None:
            return cls(**data)


    # get_by_id()
    # 
    # searches for the given user id
    # 
    # params: _id - user id to serach for
    # 
    # returns: the user object when the user id exists
    @classmethod
    def get_by_id(cls, _id):
        data = users.find_one({"_id": _id})
        if data is not None:
            return cls(**data)


    # login_valid()
    # 
    # validates the given user credentials
    # 
    # params: username - username to validate
    #         password - password to given username
    # 
    # returns: the user object when the user is valid or False when not is valid
    @staticmethod
    def login_valid(username, password):
        verify_user = User.get_by_username(username)
        if verify_user is not None:
            return bcrypt.checkpw(password.encode('utf-8'), verify_user.password)
        return False


    # change_password()
    # 
    # changes the password from the given username when old password is valid
    # 
    # params: username - username to validate
    #         password - password to given username
    #         newpassword - new password for given username
    # 
    # returns: True when password has been changed or False when user object is not valid and password not changed
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


    # json()
    # 
    # jsonifys the (self) user object 
    # 
    # returns: the user object as a JSON Object
    def json(self):
        return {
            "username": self.username,
            "_id": self._id,
            "password": bcrypt.hashpw((self.password).encode('utf-8'), bcrypt.gensalt())
        }