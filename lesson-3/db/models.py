import os

from enum import Enum as pyEnum
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from sqlalchemy import Identity, Integer, BigInteger, String, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv(find_dotenv(), override=True)

engine = create_async_engine(f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}", pool_pre_ping=True)
async_session = async_sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)

class Roles(pyEnum):
  user = 'user'
  model = 'model'

class Base(DeclarativeBase):
  pass

class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
  login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
  password: Mapped[str] = mapped_column(String, nullable=False)
  created: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), default=func.now())

class Room(Base):
  __tablename__ = "rooms"

  id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
  name: Mapped[str] = mapped_column(String(150), nullable=True)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

class ChatHistory(Base):
  __tablename__ = "chat_history"

  id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
  role: Mapped[Roles] = mapped_column(Enum(Roles), nullable=False)
  message: Mapped[str] = mapped_column(String, nullable=False)
  room_id: Mapped[int] = mapped_column(Integer, ForeignKey('rooms.id'), nullable=False)
  created: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)

async def async_main():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)