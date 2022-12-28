# System imports
from typing import Any
from uuid import uuid4


# Local packages
from sdf.farmbios.base_handler import BaseRPCHandler
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.storage_pb2 import StorageRPC 
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The dispatch of FarmBIOS sensor RPC messages.
class StorageRPCHandler(BaseRPCHandler):

    def __init__(self, module):
        super().__init__()
        self.module = module 


    def handle_message(self,
                       message: FarmBIOSMessage,
                       observer: Any = None,
                       is_callback: bool = False):
        """
           Process Storage RPC calls.
           :param message: The message pulled from the wire.
           :param observer: The local observer making the call.
           :param is_callback: Determines the type of handling.
        """
        # Retrieve the call specs.
        rpc_info = message.storage
        metadata = rpc_info.procedure

        # Discern the call type
        proc_type = metadata.WhichOneof("procedure_types")

        if proc_type == "call":
            if metadata.call == CallType.WRITE:
                self.log("STORE: Call: WRITE\n")
                return self.module.write(message)
            elif metadata.call == CallType.READ:
                self.log("STORE: Call: READ\n")
                return self.module.read(message)
        elif proc_type == "response":
            if metadata.response == ResponseType.REQUESTED_DATA:
                self.log("STORE: Response: REQUESTED_DATA")
                # Process the received data 
                pass
            else:
                self.log("Unknown response: %s\n" % metadata.response)
        else:
            self.log("Unknown procedure type, ignoring")

        # Change Feed messages

        #if proc_type == "call":
        #    if metadata.call == CallType.GET_CHANGE_FEED:
        #        self.log("STORE: Call: GET_CHANGE_FEED")
        #        self.log("Feed query on %s\n" % rpc_info.medium.sdf_feed.iterator)
        #        resp_meta = StorageRPC()
        #        resp_meta.procedure.response = ResponseType.FEED_ITERATOR
        #        resp_meta.medium.sdf_feed.iterator = str(uuid4())
        #        resp_message = self.get_farmbios_message("storage",
        #                                                 resp_meta)
        #        return [resp_message]
        #    elif metadata.call == CallType.GET_NEXT:
        #        self.log("STORE: Call: GET_NEXT")
        #        self.log("Next query on %s\n" % rpc_info.medium.sdf_feed.iterator)
        #        resp_meta = StorageRPC()
        #        resp_meta.procedure.response = ResponseType.NEXT_ITEM
        #        resp_meta.medium.sdf_feed.iterator = rpc_info.medium.sdf_feed.iterator
        #        resp_message = self.get_farmbios_message("storage",
        #                                                 resp_meta)
        #        return [resp_message]
        #elif proc_type == "response":
        #    if metadata.response == ResponseType.FEED_ITERATOR:
        #        self.log("STORE: Response: FEED_ITERATOR\n")
        #        # Store the feed pointer 
        #        self.log("Recvd iterator %s" % rpc_info.medium.sdf_feed.iterator)
        #        return None 
        #    elif metadata.response == ResponseType.NEXT_ITEM:
        #        self.log("STORE: Response: NEXT_ITEM")
        #        # Process the next item in the feed 
        #        self.log("Next from %s\n" % rpc_info.medium.sdf_feed.iterator)
        #        return None 
        #    else:
        #        self.log("Unknown response: %s\n" % metadata.response)
        #else:
        #    self.log("Unknown procedure type, ignoring")

        ## Pub/Sub messages

        #if proc_type == "call":
        #    if metadata.call == CallType.SUBSCRIBE:
        #        self.log("STORE: Call: SUBSCRIBE")
        #        self.log("Topics %s\n" % rpc_info.medium.sdf_pub_sub.topics)
        #        resp_meta = StorageRPC()
        #        resp_meta.procedure.response = ResponseType.SUBSCRIBE_SUCCESS
        #        # Return the topics that were successfully subscribed to.
        #        subscription_topics = rpc_info.medium.sdf_pub_sub.topics
        #        resp_meta.medium.sdf_pub_sub.topics.extend(subscription_topics)
        #        resp_message = self.get_farmbios_message("storage",
        #                                                 resp_meta)
        #        return [resp_message]
        #    elif metadata.call == CallType.PUSH:
        #        self.log("STORE: Call: PUSH")
        #        self.log("Topic update %s\n" % rpc_info.medium.sdf_pub_sub.topics)
        #        resp_meta = StorageRPC()
        #        resp_meta.procedure.response = ResponseType.PUSH_SUCCESS
        #        # Return the topic that was successfully pushed.
        #        pushed_topics = rpc_info.medium.sdf_pub_sub.topics
        #        resp_meta.medium.sdf_pub_sub.topics.extend(pushed_topics) 
        #        resp_message = self.get_farmbios_message("storage",
        #                                                 resp_meta)
        #        return [resp_message]
        #    elif metadata.call == CallType.NOTIFY:
        #        self.log("STORE: Call: NOTIFY")
        #        self.log("Notifying on topic(s): %s\n" % \
        #                 rpc_info.medium.sdf_pub_sub.topics)
        #        return None 
        #    elif metadata.call == CallType.PULL:
        #        self.log("STORE: Call: PULL")
        #        self.log("Pull query on %s\n" % rpc_info.medium.sdf_pub_sub.topics)
        #        resp_meta = StorageRPC()

        #            # TODO Fill the topic updates if there are any
        #            are_there_updates = randint(0,1)
        #            if are_there_updates == 0:
        #                resp_meta.procedure.response = ResponseType.NO_DATA
        #            else:
        #                resp_meta.procedure.response = ResponseType.TOPIC_UPDATES

        #            # Return the topic that was pulled.
        #            pulled_topics = rpc_info.medium.sdf_pub_sub.topics
        #            resp_meta.medium.sdf_pub_sub.topics.extend(pulled_topics)

        #            resp_message = self.get_farmbios_message("storage",
        #                                                     resp_meta) 
        #            return [resp_message]
        #elif proc_type == "response":
        #    if metadata.response == ResponseType.SUBSCRIBE_SUCCESS:
        #        self.log("STORE: Response: SUBSCRIBE SUCCESS")
        #        self.log("Successfully subscribed to %s\n" % \
        #                 rpc_info.medium.sdf_pub_sub.topics)
        #        return None 
        #    elif metadata.response == ResponseType.PUSH_SUCCESS:
        #        self.log("STORE: Response: PUSH SUCCESS")
        #        self.log("Successfully pushed to %s\n" % \
        #                 rpc_info.medium.sdf_pub_sub.topics)
        #        # Process a successful push notification 
        #        return None 
        #    elif metadata.response == ResponseType.NO_DATA:
        #        # Process an empty data pull 
        #        self.log("STORE: Response: NO DATA")
        #        self.log("No updates for %s\n" % rpc_info.medium.sdf_pub_sub.topics)
        #        return None 
        #    elif metadata.response == ResponseType.TOPIC_UPDATES:
        #        self.log("STORE: Response: TOPIC UPDATES")
        #        self.log("Rcvd updates for %s\n" % rpc_info.medium.sdf_pub_sub.topics)
        #        # TODO: Process the pull updates
        #        return None 
        #    else:
        #        self.log("Unknown response: %s\n" % metadata.response)
        #else:
        #    self.log("Unknown procedure type, ignoring")
