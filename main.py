import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from mcp.server.fastmcp import FastMCP
load_dotenv(find_dotenv(), override=True)

mcp = FastMCP('demo')
engine = create_async_engine(f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

@mcp.tool()
async def command_query(command: str) -> list:
  """
  Executes SQL commands in local postgresql server and returns result.
  """
  async with async_session() as session:
    res = (await session.execute(text(command))).mappings().fetchall()
    await session.commit()
    return res

if __name__ == '__main__':
  mcp.run(transport='stdio')