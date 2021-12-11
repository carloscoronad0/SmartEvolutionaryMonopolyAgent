import logging
import os
formatter = logging.Formatter('%(message)s')

def setup_logger(name, path_to_log):
    load_directories(path_to_log)
    complete_name = f"{name}.log"
    complete_path = os.path.join(path_to_log, complete_name)
    handler = logging.FileHandler(complete_path)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

def load_directories(path_to_log):
    if not os.path.exists(path_to_log):
        os.mkdir(path_to_log)
        print(f"Directory {path_to_log} created")