import logging

# Nothing else i tried would suppress all the damn warnings
logging.captureWarnings(True)
logging.getLogger("py.warnings").setLevel(logging.ERROR)

