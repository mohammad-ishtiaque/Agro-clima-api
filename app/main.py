from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to AgroClima API! 🌿"}

# নতুন রাউট: ডাটাবেস হেলথ চেক
@app.get("/db-check")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # আমরা ডাটাবেসকে বলছি: "SELECT 1" (মানে তুমি কি আছো?)
        result = db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database Connection Successful! 🟢"}
    except Exception as e:
        return {"status": "error", "message": f"Connection Failed: {str(e)} 🔴"}