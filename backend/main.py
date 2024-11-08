import fastapi

from routers import users

app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

