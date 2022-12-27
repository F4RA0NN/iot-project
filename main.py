from asyncua import Client
import asyncio
from config import Config
from agent import Agent

async def main():
  config = Config()
  url = config.put("url")

  async with Client(url=url) as client:
    root = client.get_objects_node()
    children = await root.get_children()

    for device in children:
      name = (await device.read_browse_name()).Name

      if (name != 'Server'):
        print(name)
        connection_string = config.put("connection_string", name)
        agent = Agent(device, connection_string)

        while True:
          await agent.send()
          await asyncio.sleep(3)
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())