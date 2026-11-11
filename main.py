from fastapi import FastAPI

from app.routers import auth as auth_routers
from app.routers import users as user_routers


app = FastAPI(title="InsightHub Users API")

app.include_router(user_routers.router)
app.include_router(auth_routers.router)

# --------------------------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "InsightHub FastAPI is running"}



