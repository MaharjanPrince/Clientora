import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Loading the .env file
load_dotenv()

# Get the URL from the environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Creating a session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()


# Dependency to get the DB session in FASTAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
