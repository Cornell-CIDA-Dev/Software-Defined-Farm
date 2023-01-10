# System imports
from typing import Any


# Local packages
from sdf.compute.base_compute import ComputeModule
from sdf.dairymgr.callback_enum_defs import DairyMgrComputeCallBacks as dmgr_co_cb
from sdf.dairymgr.dairymgr_config import DairyManagerComputeConfig
from sdf.dairymgr.proto.generated.update_pb2 import DairyMgrSensorUpdate
from sdf.dairymgr.proto.dairymgr_pb2 import FarmPCMessage 
from sdf.dairymgr.utils.helpers import deliver
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.sensor_pb2 import SensorRPC 
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.helper_typedefs import Modules as mod


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for Dairy Manager aggregation function.
class DairyManagerCompute(ComputeModule):

    def __init__(self,
                 config: DairyManagerComputeConfig,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher


    def handle_callback(self,
                        message: FarmBIOSMessage,
                        callback_func: dmgr_co_cb,
                        **kwargs):
       """
           Call the appropriate handler for compute module call backs.
           :param message: The message with the response for the call back.
           :param callback_func: The local function to pass the message to.
       """
       self.log("HANDLING CALL BACK FOR: %s\n" % callback_func.name)
       if callback_func == dmgr_co_cb.CONFIRM_REGISTRATION:
           return self.confirm_registration(message)
       elif callback_func == dmgr_co_cb.PROCESS_READ_DATA:
           return self.process_read_data(message)
       else:
           self.log("Unknown call back %s\n" % callback_func.name)
           return None, None


    def start_registration(self, sensor_name: str):
        """
           Register with the sensor module.
           :param sensor_name: The sensor module to contact for registration.
        """
        # Create sensor update and specify the sensor of interest.
        sensor_msg = SensorRPC()
        sensor_msg.procedure.call = CallType.REGISTER 
        update = DairyMgrSensorUpdate(sensorName=sensor_name)
        sensor_msg.update = update.SerializeToString()

        # Register a call back to finish the registration and configuration
        outgoing_msg = self.dispatcher.compose_outbound(sensor_msg,
                                                        mod.COMPUTE,
                                                        mod.SENSOR,
                                             dmgr_co_cb.CONFIRM_REGISTRATION)
        self.dispatcher.dispatch_message(outgoing_msg)


    def confirm_registration(self, message: FarmBIOSMessage):
        """
           Process a registration confirmation message from the sensor module.
           Set the configuration passed by the sensor module.
        """
        status = message.sensor.procedure.response
        if status == ResponseType.REGISTER_SUCCESS:
            self.log("REGISTRATION WITH SENSOR MODULE WAS SUCCESSFUL")
        else:
            self.log("SENSOR REGISTRATION WITH SENSOR MODULE FAILED")
        # No responses to send or callbacks to register
        return None, None


    def rcv_sensor_notification(self, message: FarmBIOSMessage):
        """
           A method for local calls to receive sensor notifications.
           :param message: The message from the wire.
        """
        update = DairyMgrSensorUpdate()
        update.ParseFromString(message.compute.update)
        update_str = "\n Update Received \n"
        update_str += "Sensor :%s\n" % update.sensorName
        update_str += "File Path: %s\n" % update.updatePath
        update_str += "Timestamp: %s\n" % update.updateTimestamp
        self.log(update_str)

        # Create a read request for the update
        sensor_msg = SensorRPC()
        sensor_msg.procedure.call = CallType.READ

        # Future possibility is to add some filtering conditions on the update.
       
        # Copy the update to be sent back to the sensor
        sensor_msg.update = message.compute.update 

        # Create an outgoing message requesting a read for the update
        outgoing_msg = self.dispatcher.compose_outbound(sensor_msg,
                                                        mod.COMPUTE,
                                                        mod.SENSOR,
                                             dmgr_co_cb.PROCESS_READ_DATA)

        return outgoing_msg.message_list, outgoing_msg.callback_record


    def process_read_data(self, message: FarmBIOSMessage):
        """
           Echo the file name for the received message.
           :param message: The message from the wire.
        """
        farmpc_message = FarmPCMessage()
        farmpc_message.ParseFromString(message.data)

        # Channel the message to the right handler.
        message_type = farmpc_message.WhichOneof("farmpc_types")
        if message_type == "vendorTwo":
            filename = farmpc_message.vendorTwo.filename
            print("Vendor Two Message, filename: %s\n" % filename)
        elif message_type == "vendorOne":
            filename = farmpc_message.vendorOne.filename
            print("Vendor One Message, filename: %s\n" % filename)
        elif message_type == "vendorThree":
            filename = farmpc_message.vendorThree.filename
            print("Vendor Three Message, filename: %s\n" % filename)

        # Send message to the cloud storage module.
        deliver(farmpc_message, self.config)

        return None, None


    def analytics(self, message: FarmBIOSMessage):
        """
           Run the dairy manager business logic.
           :param message: The message from the wire.
        """
        pass


    def run(self, arg: bytes):
        """
           A method for running any experiments requested by the peer.
           :param arg: The context for querying data.
        """
        pass
