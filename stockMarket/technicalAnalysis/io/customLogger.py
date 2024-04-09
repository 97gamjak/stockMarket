import logging
import logging.config

from pathlib import Path

config_file = str(Path(__file__).parent / Path("log.conf"))

logging.config.fileConfig(config_file)

time_logger = logging.getLogger('timeit')

time_logger.setLevel(logging.WARNING)
