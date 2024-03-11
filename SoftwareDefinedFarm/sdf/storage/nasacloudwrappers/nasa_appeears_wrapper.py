# System imports
from pathlib import Path
from typing import Any, Dict, List


# Local packages
from sdf.storage.nasacloudwrappers.data_pull_typedefs import (TaskTypes, OutputTypes,
                                              SpatialProjections as Projections)
from sdf.storage.base_storage import StorageModule 
                                                         


# Third party packages
from requests import get, post 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A Wrapper class for calling NASA Earth Data Cloud.
class NASAppeearsService(StorageModule):

    def __init__(self,
                 config: Any,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config
        self.active_token = None
        self.general_api = 'https://appeears.earthdatacloud.nasa.gov/api/'


    def get_new_token(self):
        """
           Get a new token from EarthData (if previous one expired).
        """

        # Wait on JSONifying until the response is guaranteed to not error.
        login_endpt = self.general_api + 'login'
        response = post(login_endpt, auth=(self.config['username'],
                                           self.config['password'])
                       )
        token = response.json()
        self.log("Token response %s" % token)
        return token


    def get_product_list(self):
        """
           Get the list of all available products.
           The API call does not require authentication.
        """

        # Wait on JSONifying until the response is guaranteed to not error.
        product_endpt = self.general_api + 'product'
        response = get(product_endpt)
        product_response = response.json()
        all_products = { p['ProductAndVersion']: p for p in product_response }
        return all_products


    def list_product_layers(self, product_id: Dict):
        """
           List all the layers available for a given product.
           The API call does not require authentication.
           :param product_id: The product and version used for identication.
        """

        layers_endpt = self.general_api + 'product/' + product_id['FullVersion']
        layer_response = get(layers_endpt)
        return layer_response.json()


    def get_projection_types(self):
        """
           Retrieve list of supported projections.
           The API call does not require authentication.
        """
        projections_endpt = self.general_api + 'spatial/proj'
        projections_response = get(projections_endpt)
        return projections_endpt.json()


    def fill_point_request(self,
                           task_obj: Dict,
                           coordinates: List[Dict],
                           output_type: OutputTypes = OutputTypes.GEOTIFF):
        """
           Fill the rest of the parameters for a point request.
           :param task_obj: A generic task object dictionary.
           :param coordinates: A list of (optionally ID'd and categorized)
                               coordinates.
           :param output_type: The format to use for the file output.
        """
        params = task_obj['params']

        # The default output format is GEOTIFF unless specified otherwise.
        params['output'] = {
                            "format": {
                              "type": output_type.value
                            }
                           }
        params['coordinates'] = coordinates 
        return task_obj

        
    def fill_area_request(self,
                          task_obj: Dict,
                          area_of_interest: Dict,
                          output_type: OutputTypes,
                          projection_name: Projections):
        """
            Fill in the rest of the parameters for an area request.
            :param task_obj: A generic task object dictionary.
            :param area_of_interest: A polygon definition for a geographic area.
            :param output_type: The format to use for the file output.
            :param projection_name: The type of project to use. The projections
                        are defined at
            https://appeears.earthdatacloud.nasa.gov/api/?python#list-projections
        """
        params = task_obj['params']
        params['geo'] = area_of_interest
        params['output'] = { "format":
                                    { "type": output_type.value },
                                      "projection": projection_name.value
                           }
        return task_obj


    def create_task(self,
                    task_type: TaskTypes,
                    dates: List[Dict],
                    layers: List[Dict],
                    task_name: str = None,
                    coordinates: List[Dict] = None,
                    area_of_interest: Dict = None,
                    output_type: OutputTypes = OutputTypes.GEOTIFF,
                    projection_name: Projections = Projections.GEOGRAPHIC):
       """
          Create a task object to be submitted to NASA EarthCloud.
          :param task_type: The type of task, either area or point.
          :param dates: A list of (optionally recurring) date ranges.
          :param product_id: Product and version identifier.
          :param layers: The layer to pull for each product.
          :param task_name: Optional name specified by the user.
          :param coordinates: A list of (optionally ID'd and categorized)
                               coordinates. Must not be None for point requests.
          :param area_of_interest: A polygon definition for a geographic area.
                                   Must not be None for area requests.
          :param output_type: The format to use for the file output.
          :param projection_name: The type of project to use. The projections
                        are defined at
          https://appeears.earthdatacloud.nasa.gov/api/?python#list-projections
       """
       task_obj = {}

       # Fill in the different parameters
       task_obj['params'] = {
                             "dates": dates,
                             "layers": layers
                            }

       # Check if the user specified a name
       if task_name != None:
           task_obj['task_name'] = task_name
       else: # Create a stub name from product id and dates
           start_date = dates[0]['startDate']
           end_date = dates[0]['endDate']
           task_obj['task_name'] = layers[0]['layer'] + '-' + start_date
           task_obj['task_name'] += '-' + end_date 

       task_obj['task_type'] = task_type.value

       if task_type == TaskTypes.POINT:
           task_obj = self.fill_point_request(task_obj, coordinates)
       else:
           task_obj = self.fill_area_request(task_obj, area_of_interest,
                                             output_type, projection_name)

       return task_obj


    def write(self, task_obj: Dict):
        """
           Submit a task for processing to the EarthData cloud.
           This is akin to "writing" a task to the cloud.
           The call requires authentication.
           :param task_obj: A parameterized task.
        """
        # Check if there is an active token
        if self.active_token == None:
            self.active_token = self.get_new_token()

        # Get the layers related to the product
        token = self.active_token['token']

        response = post(self.general_api + 'task', json=task_obj,
                        headers={'Authorization': 'Bearer ' + token})
        response_code = response.status_code
        task_response = response.json()
        return response_code, task_response 


    def list_all_tasks(self):
        """
           List all requests associated with a user account.
           This call requires authentication with EarthCloud.
        """
        # Check if there is an active token
        if self.active_token == None:
            self.active_token = self.get_new_token()

        # Get the layers related to the product
        token = self.active_token['token']

        response = get(self.general_api + 'task',
                       headers={'Authorization': 'Bearer ' + token})

        return response.json()


    def retrieve_task(self, task_id: str):
        """
           Retrieve a particular task given an existing ID.
           :param task_id: The unique task identifier.
           This call requires authentication with EarthCloud.
        """
        # Check if there is an active token
        if self.active_token == None:
            self.active_token = self.get_new_token()

        # Get the layers related to the product
        token = self.active_token['token']

        response = get(self.general_api + 'task/' + task_id,
                       headers={'Authorization': 'Bearer ' + token})

        return response.json()


    def delete_task(self, task_id: str):
        """
           Delete a particular task given an existing ID.
           :param task_id: The unique task identifier.
           This call requires authentication with EarthCloud.
        """
        # Check if there is an active token
        if self.active_token == None:
            self.active_token = self.get_new_token()

        token = self.active_token['token']

        response = delete(self.general_api + 'task/' + task_id,
                          headers={'Authorization': 'Bearer ' + token})

        # 204 is considered to have been successful.
        return response.status_code


    def get_task_bundle(self, task_id: str):
        """
           List all files available for download in a task bundle.
           :param task_id: The unique task identifier.
           This call requires authentication with EarthCloud.
        """
        # Check if there is an active token
        if self.active_token == None:
            self.active_token = self.get_new_token()

        # Get the files associated with the bundle. 
        token = self.active_token['token']

        response = get(self.general_api + 'bundle/' + task_id,
                       headers={'Authorization': 'Bearer ' + token})

        return response.json()


    def read(self,
             task_id: str,
             file_id: str):
        """
           Download a file from a completed task bundle.
           This is akin to "reading" from the cloud once it generates readables.
           :param task_id: The unique task identifier.
           :param file_id: The unique identifier for the file.
        """
        # Check if there is an active token
        if self.active_token == None:
            self.active_token = self.get_new_token()

        token = self.active_token['token']
        target_url = self.general_api + 'bundle/' + task_id
        target_url += '/' + file_id
        response = get(target_url,
                       headers={'Authorization': 'Bearer ' + token},
                       allow_redirects=True,
                       stream=True)

        # Create a directory where to store the file, only if one
        # does not already exist for the given task ID
        dir_path = Path(task_id).mkdir(exist_ok=True)
        file_path = Path(task_id).joinpath(file_id)

        with open(file_path, 'wb') as fd:
            for data in response.iter_content(chunk_size=8192):
                fd.write(data)
