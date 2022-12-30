from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
import json
import asyncio
from asyncua import ua
import datetime
class Agent:
  def __init__(self, device, connection_string):
    self.device = device
    self.connection_string = connection_string
    self.client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)
    self.client.connect()
    self.client.on_twin_desired_properties_patch_received = self.patchProductionRate
    self.client.on_method_request_received = self.receiveMethod
    
    self.tasks = []

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


  async def patchTwinReportedProps(self):
    self.client.patch_twin_reported_properties({'WorkorderId': await (await self.device.get_child('WorkorderId')).read_value()})
    self.client.patch_twin_reported_properties({'DeviceError': await (await self.device.get_child('DeviceError')).read_value()})
  
  async def createTasks(self):
    tasks = [asyncio.create_task(task) for task in self.tasks]
    tasks.append(asyncio.create_task(self.patchTwinReportedProps()))
    tasks.append(asyncio.create_task(self.send()))
    self.tasks = []
    return tasks

  def patchProductionRate(self, patch):
    if "ProductionRate" in patch:
      print("Patched ProductionRate to: " + str(patch['ProductionRate']))
      self.tasks.append(
        self.setProps(ua.Variant(patch['ProductionRate'], ua.VariantType.Int32))
      )

  async def setProps(self, value):
    await (await self.device.get_child('ProductionRate')).write_value(value)

  def receiveMethod(self, method_request):

    if method_request.name == "MaintenanceDone":
      print("Adding MaintenanceDoneDate to twin reported properties")
      self.client.patch_twin_reported_properties({'MaintenanceDoneDate': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

    if method_request.name == "Reset":
      print("Resetting device")
      self.tasks.append(
        self.device.call_method("ResetErrorStatus")
      )

    if method_request.name == "Stop":
      print("Stopping device")
      self.tasks.append(
        self.device.call_method("EmergencyStop")
      )

    self.client.send_method_response(MethodResponse(method_request.request_id, 0))