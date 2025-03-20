from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Code Execution Service is running!"}