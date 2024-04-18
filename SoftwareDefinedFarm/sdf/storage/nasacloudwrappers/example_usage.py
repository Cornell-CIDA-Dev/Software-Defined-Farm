# Main method
if __name__ == "__main__":
    
    args =  parse_main_args()
    config_file_path = args['config_file']

    # Read the application config and create the module config object
    config = None
    try:
        with open(config_file_path, 'r') as fd:
            config = loads(fd.read())
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)

    wrapper = AppeearsWrapper(config)

    #Get the list of available products
    products = wrapper.get_product_list()
    for product_id, info in products.items():
        print("Product ID: %s, Platform: %s, Description: %s\n\n" % \
                     (product_id, info['Platform'], info['Description']))

    for product in config['products']:

        product_layers = wrapper.list_product_layers(product)
        print("Product Desc: %s, \n" % product['Description'])

        for layer, details in product_layers.items():
           print("Layer %s: \n Details: %s\n\n" % (layer, details))

     #Load stub point request
    stub_point_json_path = config['stubPointRequestFile']
    try:
        with open(stub_point_json_path, 'r') as fd:
            pt_request_json = loads(fd.read())
    except FileNotFoundError as fnf:
        print("Stub point request file %s not found... exiting" % pt_request_json)
        exit(1)

    # Init parameters for the task object from the loaded JSON
    task_type = TaskTypes.POINT
    task_name = pt_request_json['taskName']
    dates = pt_request_json['dates']
    layers = pt_request_json['layers']
    coordinates = pt_request_json['coordinates']
    output_format = OutputTypes.GEOTIFF

    task_obj = wrapper.create_task(task_type, dates, layers,
                                   task_name=task_name,
                                   coordinates=coordinates,
                                   output_type=output_format)

    for key, value in task_obj.items():
        print("%s: %s\n" % (key, value))

    # Submit task for testing
    response_code, task_response = wrapper.submit_task(task_obj)
    print("Response code %s\n Response: %s\n" % (response_code, task_response))

    # Test checking and downloading bundles for an existing task
    task_id = pt_request_json['nov3TaskId'] 
    task_bundles = wrapper.get_task_bundle(task_id)
    for file_dets in task_bundles['files']:
        print("%s:\n" % file_dets)
        # Download the file
        wrapper.download_bundle_file(task_id, file_dets['file_id'])
