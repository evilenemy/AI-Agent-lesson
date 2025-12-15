from google.genai import Client
from typing import AnyStr
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

class Agent:
  def __init__(self, last_messages: list):
    self.client = Client()
    self.chat = self.client.chats.create(model='gemini-2.5-flash-lite', history=last_messages)

  async def ask(self, text: str) -> AnyStr:
    return self.chat.send_message(text).parts[0].text
