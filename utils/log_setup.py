import logging
def setup_logger(name, filename, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    fmt = logging.Formatter("[%(asctime)s][DAY %(day)d] %(message)s", "%H:%M:%S")

    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(filename, mode='w')
    ]

    for h in handlers:
        h.setFormatter(fmt)
        logger.addHandler(h)

    return logger