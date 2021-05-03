import firebase_admin
from firebase_admin import credentials, auth

import pyrebase

class User_manage:

    def __init__(self):
        config = {
            "apiKey": "AIzaSyDsH3BH4xktZ7HHqkEP5sb5RLGDe4BKIyU",
            "authDomain": "notzoom-43554.firebaseapp.com",
            "databaseURL":"https://notzoom-43554.firebaseio.com",
            "projectId": "notzoom-43554",
            "storageBucket": "notzoom-43554.appspot.com",
            "messagingSenderId": "197926019175",
            "appId": "1:197926019175:web:f41802445716ed25e9b4c2",
            "measurementId": "G-MERD3BSP95"
          }
        firebase = pyrebase.initialize_app(config)
        self.auth1 = firebase.auth()
        cred = credentials.Certificate("sdk.json")
        firebase_admin.initialize_app(cred)

    def add_user(self, name, email, password):
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name,
                disabled=False)
            print('Sucessfully created new user:', user.uid)
            return True
        except:
            return False

    def get_user(self, email, password):
        try:
            return self.auth1.sign_in_with_email_and_password(email, password)
        except:
            return False