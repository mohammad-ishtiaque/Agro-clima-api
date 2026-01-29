from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Docker এর ভেতরে ডাটাবেসের ঠিকানা
# user:password123 -> ইউজারনেম ও পাসওয়ার্ড (যা docker-compose.yml এ দিয়েছিলাম)
# db:3306 -> সার্ভার নাম (Docker Service Name) ও পোর্ট
# agroclima -> ডাটাবেস নাম

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password123@db:3306/agroclima"

# ইঞ্জিন তৈরি করছি (গাড়ির ইঞ্জিনের মতো, এটাই সব চালাবে)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# সেশন মেকার (প্রতিটি রিকোয়েস্টে ডাটাবেসের সাথে কানেকশন ওপেন করার জন্য)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# বেস মডেল (এটা দিয়েই আমরা টেবিল বানাবো)
Base = declarative_base()

# ডিপেন্ডেন্সি (কানেকশন ওপেন করে আবার ক্লোজ করার ফাংশন)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()