import asyncio
from dotenv import load_dotenv, find_dotenv
from db.models import async_main, async_session
from app.db import DB
from app.application import App

load_dotenv(find_dotenv(), override=True)

async def main():
  await async_main()

  db = DB(async_session)
  app = App(db)
  await app.run()

if __name__ == '__main__':
  asyncio.run(main())