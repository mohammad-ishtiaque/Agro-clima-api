from fastapi import FastAPI

# অ্যাপ ইনিশিলাইজ করছি
app = FastAPI()

# এটা হলো আমাদের হোম রুট (Home Route)
@app.get("/")
def read_root():
    return {"message": "Hello from AgroClima! API is running perfectly inside Docker 🚀"}

# একটা ডামি ওয়েদার ডেটা চেক করার রুট
@app.get("/weather-check")
def check_weather():
    return {
        "location": "Somerville, TX",
        "status": "Wet",
        "score": 15
    }