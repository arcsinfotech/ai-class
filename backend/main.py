# pip install fastapi uvicorn
from app import get_application

app = get_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)