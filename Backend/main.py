from fastapi import FastAPI

### Backend api definition goes here

app = FastAPI()

@app.get('/')
def status():
    return {'running': True, 'description': "Listening to requests"}

