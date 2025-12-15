import json
from dotenv import load_dotenv
load_dotenv('../.env')

from google import genai

try:
  with open("chats.json", 'r') as f:
    chats = json.load(f)
except FileNotFoundError:
  chats = []
except Exception as e:
  print(e)

client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash", history=chats)

while True:
  req = input("User: ")
  if req in ['q', 'quit']:
      break
  response = chat.send_message(req)
  print("Model: " + response.text)

with open("chats.json", 'w') as f:
  chats = []
  for msg in chat.get_history():
    chats.append({
      'role': msg.role,
      'parts': [{'text': msg.parts[0].text}],
    })
  json.dump(chats, f)