import logging
import os
from datetime import datetime

def initialize_logging():
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{log_directory}/debug_{current_time}.log"
    
    logging.basicConfig(
        filename=log_filename,
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )
    
    # Adding console handler to also print the logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler)

    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    # logging.getLogger('openai._base_client').setLevel(logging.WARNING)

    logging.info("Logging initialized successfully.")



