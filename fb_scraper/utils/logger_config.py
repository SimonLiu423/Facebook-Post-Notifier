import logging


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(asctime)s %(name)s %(levelname)-8s] %(message)s", '%Y%m%d %H:%M:%S')

    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
