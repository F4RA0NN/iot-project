from azure.iot.device import IoTHubDeviceClient, Message
import json

class Agent:
  def __init__(self, device, connection_string):
    self.device = device
    self.connection_string = connection_string
    self.client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)
    self.client.connect()

  async def send(self):
    telemetry = {
        "WorkorderId": await (await self.device.get_child('WorkorderId')).read_value(),
        "ProductionStatus": await (await self.device.get_child('ProductionStatus')).read_value(),
        "GoodCount": await (await self.device.get_child('GoodCount')).read_value(),
        "BadCount": await (await self.device.get_child('BadCount')).read_value(),
        "Temperature": await (await self.device.get_child('Temperature')).read_value(),
    }

    print(telemetry)

    message = Message(json.dumps(telemetry), 'UTF-8',"JSON")

    self.client.send_message(message)

