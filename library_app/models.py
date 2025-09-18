# library_app/models.py
# Definiert die Datenmodelle der Anwendung, wie z.B. die `User`-Klasse für Flask-Login.

from flask_login import UserMixin
from bson.objectid import ObjectId

from .db import users_collection

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.role = user_data.get('role', 'user')

def load_user_for_login(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    return User(user_data) if user_data else None