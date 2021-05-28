import firebase_admin
from firebase_admin import credentials, auth
import config

import pyrebase

class User_manage:

    def __init__(self):
        config = config.api_json
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