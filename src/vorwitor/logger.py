import logging
import sys

from vorwitor import CONFIG_DIR


logger = logging.getLogger('Vorwitor')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(filename=CONFIG_DIR + '/debug.log', mode='w')
fh.setLevel(logging.DEBUG)
# TODO if DEBUG is off
#fh = logging.FileHandler(filename=CONFIG_DIR + '/debug.log', filemode='w', level=logging.ERROR)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s:%(funcName)s:%(lineno)s %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
