from fastapi import FastAPI
from backend.api.routes import router  # Import routes from routes.py

app = FastAPI()

# Include routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
