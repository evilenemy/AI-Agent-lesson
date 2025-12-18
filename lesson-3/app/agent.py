import os
import httpx

from google.genai import Client, types
from typing import AnyStr
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

def get_weather(city: str) -> dict[str, AnyStr]:
  """Get current weather of given city."""
  api_key = os.getenv("OPENWEATHER_API_KEY")

  return httpx.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric").json()

config = types.GenerateContentConfig(tools=[get_weather], system_instruction="Always answer with human readable format after whenever tool calling.")

class Agent:
  def __init__(self, last_messages: list):
    self.client = Client()
    self.chat = self.client.chats.create(model='gemini-2.5-flash-lite', history=last_messages, config=config)

  async def ask(self, text: str) -> AnyStr:
    return self.chat.send_message(text).parts[0].text