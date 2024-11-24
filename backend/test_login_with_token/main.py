import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from sign_views import router as sing_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",  # Common React dev server port
    "http://localhost:5173",  # Add this line for Vite
    "http://192.168.138.69",  # Add this line for your backend IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(sing_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Backend!"}

# if __name__ == '__main__':
#     uvicorn.run("main:app", reload=True)

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True, host="0.0.0.0")

