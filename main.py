from asyncua import Client
import asyncio
from config import Config

async def main():
  config = Config()
  url = config.put("url")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())