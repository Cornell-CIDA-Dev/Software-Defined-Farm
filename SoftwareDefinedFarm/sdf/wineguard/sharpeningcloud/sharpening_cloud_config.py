# System imports
from json import loads, dumps
from os import environ
from typing import Any, Dict


# Local imports
from sdf.config.base_config import BaseConfig
from sdf.wineguard.proto.wineguard_pb2 import (EarthCloudCredentials,
                                               EarthCloudConfig,
                                               EarthCloudProduct,
                                               EarthClouResult,
                                               Layer)


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# An abstract class for configuring request module runs.
class SharpeningRequestConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified config including settings like
                          the EarthCloud preferences, credentials, etc.
        """
        # Override the the address for the sharpening module with environment
        # variables before passing to the base config.
        config['computeHost'] = environ['SHARPENING_MODULE_ADDRESS']
        config['computePort'] = environ['SHARPENING_MODULE_PORT']

        super().__init__(config)

        products = []
        for product in config['products']:
            new_prod = EarthCloudProduct(fullVersion=product['FullVersion'],
                                         description=product['Description'])
            layers = []
            for layer in product['Layers']:
                new_layer = Layer(name=layer)
            new_prod.layers.extend(layers)
            new_prod.projection = product['Projection']

            products.append(new_prod)

        self.earth_cloud = EarthCloudConfig()
        self.earth_cloud.products.extend(products)
        # Load the request if one is specified
        if 'requestFile' in config:
           try:
               req_file_path = config['requestFile']
               with open(req_file_path, 'r') as fd:
                   request_json = loads(fd.read()) 
                   self.earth_cloud.request.specs = dumps(request_json)
           except FileNotFoundError as fnf:
               self.log("Request file %s not found..." % req_file_path)
               self.earth_cloud.request = None


        # Configure the address tuple to be used by the request module
        self.requester_address = tuple([config['requesterHost'],
                                        int(config['requesterPort'])
                                       ])


# An abstract class for configuring request module runs.
class SharpeningCloudConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified config including settings like
                          the EarthCloud preferences, credentials, etc.
        """
        super().__init__(config)

        products = []
        for product in config['products']:
            new_prod = EarthCloudProduct(fullVersion=product['FullVersion'],
                                         description=product['Description'])
            layers = []
            for layer in product['Layers']:
                new_layer = Layer(name=layer)
            new_prod.layers.extend(layers)
            new_prod.projection = product['Projection']

            products.append(new_prod)

        self.earth_cloud = EarthCloudConfig()
        self.earth_cloud.products.extend(products)
        self.earth_cloud.access.username = config['username']
        self.earth_cloud.access.password = config['password']
        self.log("EarthCloud config given %s\n" % self.earth_cloud)

        # Configure the address tuple to be used by the request module
        self.requester_address = tuple([config['computeHost'],
                                        int(config['computePort'])
                                       ])
