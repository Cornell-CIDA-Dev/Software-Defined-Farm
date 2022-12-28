# System packages
from argparse import ArgumentParser
from typing import Optional, List


def prompt_infinitely(prompt: str,
                      valid: Optional[List] = None
                     ):
    """
       Prompt the user forever until they enter something valid.
       :param prompt: The prompt to give the user.
       :param valid: The list of valid requests.
       :rtype: str.
    """
    user_input = None
    if valid:
        while user_input not in valid:
            user_input = input(prompt)
    else:
        user_input = input(prompt)
    return user_input


def create_request():
    """
       Wait for a request from the user.
    """
    valid_requests = ["e"]
    r_prompt = "Request? [e = exit] : \n"
    r_type = input(r_prompt)
    if r_type not in valid_requests:
        r_type = prompt_infinitely(r_prompt, valid=valid_requests)
    if r_type == "e":
        return "exit", None


def parse_main_args():
    """ Parse the arguments passed by the user. """

    port_message = ("The port on which to start the server")
    snap_message = ("The path to a starting snapshot file")
    config_message = ("The path to a config file")

    parser = ArgumentParser(description='Retrieve arguments for a module run')

    # We may eventually want to get rid of the port and snapshot args
    parser.add_argument('-p', '--port', type=int,
                        help=port_message)
    parser.add_argument('-s', '--snapshotfile', type=str,
                        help=snap_message)
    parser.add_argument('-c', '--configfile', type=str,
                        help=config_message, required=True)

    args = parser.parse_args()

    port = args.port
    snapshot = args.snapshotfile
    config_file = args.configfile

    args = {'port': port, 'snapshot': snapshot,
            'config_file': config_file}
    return args
