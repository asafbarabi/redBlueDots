import logging


def get_logger(logger_name, log_to_console=True, log_file=None):
    # Create a logger with the given name
    logger = logging.getLogger(logger_name)

    # Set the logger's level to DEBUG
    logger.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a console handler if log_to_console is True
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Create a file handler if log_file is not None
    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger