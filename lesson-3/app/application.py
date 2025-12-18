import asyncio
import sys
import re
from getpass import getpass

from app.agent import Agent

class App:
  def __init__(self, db):
    self.db = db
    self.agent = None
    self.commands = [None, self.login, self.register, sys.exit]
    self.commands_str = "1. Login\n2. Register\n3. Exit"
    self.default_last_message = 5
    self.user = None

  async def login(self, username: str | None = None):
    if username is None:
      username = input("Login: ")
    else:
      print("Login: " + username)
    password = getpass("Enter password: ")
    user = await self.db.get_user(username, password)
    if not user:
      print("Incorrect login or password")
      return await self.login()
    self.user = user
    return await self.rooms()

  async def register(self, username: str | None = None):
    if not username:
      username = input("Login: ")
      user = await self.db.check_user(username)
      if user:
        print("User already exists. Please, try other login for registration.")
        await self.register()
    else:
      print("Login: " + username)
    password = getpass("Enter password: ")
    password2 = getpass("Confirm password: ")

    if password != password2:
      print("Passwords don't match")
      await self.register(username)

    user = await self.db.create_user(username, password)
    if not user:
      print("Something went wrong with login or password")
      await self.register(username)
    else:
      self.user = user
      await self.rooms()

  async def chat(self, room_id: int, rooms: dict):
    room_id = rooms[room_id]['id']
    room = await self.db.get_room(room_id)
    last_messages = []
    if not room:
      chat_name = input("Enter new room name (max length 150): ")
      room = await self.db.create_room(chat_name[:150], self.user.id)
    else:
      last_messages = [{"role": r['role'], "parts": [{'text': r['message']}]} for r in await self.db.last_messages(room_id, self.default_last_message)]
      reversed_messages = last_messages[::-1]
      print(f"Your chats last {self.default_last_message} messages:")
      for message in reversed_messages:
        print(f"{message['role']}: {message['parts'][0]['text']}")

    self.agent = Agent(last_messages)
    while True:
      text = input("User (q for quit): ")
      if text == "q":
        break
      insert_task = asyncio.create_task(self.db.insert_to_chat(room.id, text, 'user'))
      ask_agent = asyncio.create_task(self.agent.ask(text))
      res = await asyncio.gather(insert_task, ask_agent)
      print(f"Model: {res[1]}")
      await self.db.insert_to_chat(room.id, res[1], 'model')


  async def rooms(self):
    rooms = {i: r for i, r in enumerate(await self.db.get_users_chat_rooms(self.user.id), start=1)}
    for idx, room in rooms.items():
      print(f"{idx}. {room['name']}")
    print(f"{len(rooms) + 1}. New Chat")
    rooms[len(rooms) + 1] = {'id': 0}
    room_id = input("Please enter room id you want to join: ")
    if not re.match(r"^\d+$", room_id):
      print("You entered wrong id!\n")
      return await self.rooms()

    return await self.chat(int(room_id), rooms)

  async def run(self):
    while True:
      inp = input(f"{self.commands_str}\n>>> ")
      if inp == 'q':
        break
      if not re.match(r'^[1-9]+$', inp):
        print("Invalid input\n")
      command = self.commands[int(inp)]
      await command()