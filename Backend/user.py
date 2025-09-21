import psycopg2
from fastapi import FastAPI
# user logic goes here
class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.details = {}

loginApi = FastAPI()

@loginApi.on_event("startup")
def startup():
    print("Login API started")
    return {'running': True, 'description': "Listening to login requests"}

@loginApi.post('/login-authentication')
def login(email: str, password: str):
    global currentUser
    # code for checking if user already exists goes here
    return {'authenticated': True}

# User who is currently logged in
currentUser: User = None