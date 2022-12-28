# System imports
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict 


# Local packages
from sdf.actuation.base_actuation import ActuationModule
from sdf.farmbios.base_handler import BaseRPCHandler
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.utils.user_input import create_request
from sdf.waterguard.proto.waterguard_pb2 import TwilioMessage


# Third party packages
from twilio.rest import Client

__author__ = "Shiang Chin, Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class WaterGuardActuation(ActuationModule):

    def __init__(self, config: Any):
        self.config = config
        self.account_sid = self.config.account_sid
        self.auth_token = self.config.auth_token
        self.twilio_num = self.config.twilio_num
        self.operator_num = self.config.operator_num
        self.twilio_client = Client(self.account_sid, self.auth_token)


    def activate(self,
                 message: FarmBIOSMessage):
        """
           Send a text message to the equipment operators.
           :param message: The message from the wire.
        """
        twilio_msg = TwilioMessage()
        twilio_msg.ParseFromString(message.actuation.proc_commands)
        body = twilio_msg.body

        self.log("Message body %s\n" % body)
        self.log("Message destination %s\n" % self.operator_num)

        message = self.twilio_client.messages \
                                    .create(
                                            body=body,
                                            from_=self.twilio_num,
                                            to=self.operator_num
                                            )

        self.log("Message ID: %s\n" % message.sid)
        return None, None


    def run(self,
            dispatcher: Any):
        """
           Start the threads for the different functions.
           Note that we're passing the dispatcher for now, but it may not
           be useful in the future.
           :param dispatcher: The dispatcher for incoming/outgoing messages.
        """
        # Get a pointer to the network controller
        net_ctrl = self.config.net_ctrl

        # A pool of threads to be used for file and message checks. 
        pool = ThreadPoolExecutor(3)

        # A lit of all threads that will need to register the exit signal
        exitable_module_threads = []

        # Run a thread whose job is to check for new messages.
        spin_thread_future = pool.submit(net_ctrl.spin_server_forever)
        spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
        # Note: The WaterGuard actuation module currently has no
        # threads, so the only exitable thread is the networking thread
        exitable_module_threads.append(net_ctrl)

        # Await user exit request.
        while True:
            request = create_request()
            print("Received a signal to exit, releasing resources\n")
            for running_module in exitable_module_threads:
                running_module.exit_signal = True
            break 

        # Wait on all the threads to exit
        pool.shutdown(wait=True)
