# library_app/db.py
# Konfiguriert die Verbindung zur MongoDB-Datenbank und stellt die Collections bereit.

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/', tz_aware = True)
db = client['library_db']

# Kollektionen exportieren, um sie in anderen Dateien zu nutzen
users_collection = db['users']
books_collection = db['books']
authors_collection = db['authors']
loans_collection = db['loans']