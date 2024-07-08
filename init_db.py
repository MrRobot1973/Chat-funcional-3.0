from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import hashlib

DATABASE_URL = "sqlite:///chat_app.db"
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True, unique=True)
    password = Column(String)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(String, primary_key=True, unique=True)
    username = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = [
    {"username": "Ager", "password": "1973"},
    {"username": "user2", "password": "password2"},
    {"username": "user3", "password": "password3"}
]

for user in users:
    new_user = User(username=user["username"], password=hash_password(user["password"]))
    session.add(new_user)

session.commit()
