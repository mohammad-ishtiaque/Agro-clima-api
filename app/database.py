from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os



load_dotenv()

# Docker এর ভেতরে ডাটাবেসের ঠিকানা
# user:password123 -> ইউজারনেম ও পাসওয়ার্ড (যা docker-compose.yml এ দিয়েছিলাম)
# db:3306 -> সার্ভার নাম (Docker Service Name) ও পোর্ট
# agroclima -> ডাটাবেস নাম
# আগে যা ছিল:
# SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "mysql+pymysql://...")

# এখন এটা দাও (SQLite - file based database):
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    "sqlite:///./agroclima.db"
)

# Engine তৈরি - SQLite এর জন্য connect_args লাগে
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)


# SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# # ইঞ্জিন তৈরি করছি (গাড়ির ইঞ্জিনের মতো, এটাই সব চালাবে)
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# সেশন মেকার (প্রতিটি রিকোয়েস্টে ডাটাবেসের সাথে কানেকশন ওপেন করার জন্য)
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