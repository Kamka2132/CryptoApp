import firebase_admin
from firebase_admin import credentials, firestore

# Inicjalizacja aplikacji Firebase (jeśli jeszcze nie została zainicjalizowana)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

# Klient bazy danych, który jest importowany w innych plikach
db = firestore.client()