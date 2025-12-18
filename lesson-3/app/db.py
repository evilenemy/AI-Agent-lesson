from sqlalchemy import text
import bcrypt

def hash_password(password):
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
  return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

class DB:
  def __init__(self, async_session):
    self.async_session = async_session

  async def get_user(self, username: str, password: str):
    async with self.async_session() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE login = :username"),
            {"username": username}
        )
        user = result.mappings().first()

        if not user:
            return None

        if not verify_password(password, user["password"]):
            return None

        return user

  async def check_user(self, username: str):
    async with self.async_session() as session:
      res = await session.execute(text("SELECT 1 FROM users WHERE login = :username"), {"username": username})
      return res.mappings().first()

  async def create_user(self, username: str, password: str):
    async with self.async_session() as session:
      hashed_password = hash_password(password)
      if await self.check_user(username):
        return None
      res = await session.execute(text("INSERT INTO users (login, password) VALUES (:username, :password) RETURNING *"), {"username": username, "password": hashed_password})
      await session.commit()
      return res.mappings().first()

  async def get_room(self, room_id: int):
    async with self.async_session() as session:
      res = await session.execute(text("SELECT * FROM rooms WHERE id = :room_id"), {"room_id": room_id})
      return res.mappings().first()

  async def create_room(self, name: str, user_id: int):
    async with self.async_session() as session:
      res = await session.execute(text("INSERT INTO rooms (name, user_id) VALUES (:name, :user_id) RETURNING *"), {"name": name, "user_id": user_id})
      await session.commit()
      return res.mappings().first()

  async def last_messages(self, room_id: int, default_quantity: int = 5):
    async with self.async_session() as session:
      res = await session.execute(text("SELECT * FROM chat_history WHERE room_id = :room_id ORDER BY created DESC LIMIT :limit"), {"room_id": room_id, "limit": default_quantity * 2})
      return res.mappings().all()

  async def insert_to_chat(self, room_id: int, message: str, role: str):
    async with self.async_session() as session:
      await session.execute(text("INSERT INTO chat_history (room_id, message, role) VALUES (:room_id, :message, :role)"), {"room_id": room_id, "message": message, "role": role})
      await session.commit()

  async def get_users_chat_rooms(self, user_id: int):
    async with self.async_session() as session:
      res = await session.execute(text("SELECT * FROM rooms WHERE user_id = :user_id"), {"user_id": user_id})
      return res.mappings().all()