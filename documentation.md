# WIKTOR MITERA

## IoT Project

### Connection with OPC UA

To connect with OPC UA i am using asyncua library. You need to install it first. Application creates instance of Client class and connects to server. Configuration of connection is stored in
config.ini file.

It looks something like this:

```
[MAIN]
url = opc.tcp://localhost:4840/
```

When connection is established, we create Agent class instance and start it. Agent class is responsible for handling data from OPC UA server. It is also responsible for sending data.

### Agent Configuration

To start Agent we need to provide connection_string. It is a string that contains information about connection to Azure IoT Hub. It looks something like this:

```
[Device 1]
connection_string = connectionString
```

### Agent Creation

```
agent = Agent(device, connection_string)
```

### Telemetry

Agent is responsible for sending telemetry to Azure IoT Hub. It is done by calling send method. It takes no arguments.

```
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

```

### Device twin

```
  async def patchTwinReportedProps(self):
    self.client.patch_twin_reported_properties({'WorkorderId': await (await self.device.get_child('WorkorderId')).read_value()})
    self.client.patch_twin_reported_properties({'DeviceError': await (await self.device.get_child('DeviceError')).read_value()})

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

```

We can patch twin reported properties by calling patchTwinReportedProps method. It will send WorkorderId and DeviceError to Azure IoT Hub and save them in twin reported properties.

By calling client.on_twin_desired_properties_patch_received = self.patchProductionRate we can patch ProductionRate on our device. After we add new value to ProductionRate we call setProps method. It
will write new value to ProductionRate node on our device.

We can also call methods on our device. We can call Reset, Stop and MaintenanceDone methods. To do that we need to call client.send_method_response. It takes MethodResponse as an argument.

Reset method will reset DeviceError node on our device. (all errors will be set to false)

Stop method will set EmergencyStop node on our device to true.

MaintenanceDone method will set MaintenanceDoneDate node on our device to current date.

### Buisness Logic

Buissness Logic is made by queries and functions that are stored in asa and functions folder. Queries are stored in asa folder and functions are stored in functions folder.
