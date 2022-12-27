from asyncua import Client
import asyncio
from config import Config
from agent import Agent
from asyncua.ua.uaerrors import BadLicenseExpired

async def main():
  try:
    config = Config()
    url = config.put("url")

    devices = []

    async with Client(url=url) as client:
      root = client.get_objects_node()
      children = await root.get_children()

      for device in children:
        name = (await device.read_browse_name()).Name

        if (name != 'Server'):
          print(name)
          connection_string = config.put("connection_string", name)
          agent = Agent(device, connection_string)
          devices.append(agent)

      while True:
        for device in devices:
          tasks = await device.createTasks()
          await asyncio.gather(*tasks)
        await asyncio.sleep(5)


  except KeyboardInterrupt:
    print('KeyboardInterrupt')
  except Exception as e:
    if isinstance(e, BadLicenseExpired):
      print("License expired! ;)")
  

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())