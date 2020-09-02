import logging
import json
import os

class StackdriverFormatter(logging.Formatter):

	def __init__(self, *args, **kwargs):
		super(StackdriverFormatter, self).__init__(*args, **kwargs)

	def format(self, record):
		return json.dumps({
			'severity': record.levelname,
			'message': record.getMessage(),
			'name': record.name
		})

def info(module, msg):
	log.info("{}.INFO:[{}] Msg : {}".format(os.environ['DEPLOY_ENV'], module, msg))

def critical(module, msg):
	log.critical("{}.CRITICAL:[{}] Msg : {}".format(os.environ['DEPLOY_ENV'], module, msg))

def error(module, msg):
	log.error("{}.ERROR:[{}] Msg : {}".format(os.environ['DEPLOY_ENV'], module, msg))

def warning(module, msg):
	log.warning("{}.WARNING:[{}] Msg : {}".format(os.environ['DEPLOY_ENV'], module, msg))

def debug(module, msg):
	log.debug("{}.DEBUG:[{}] Msg : {}".format(os.environ['DEPLOY_ENV'], module, msg))

log = logging.getLogger(os.environ['DEPLOY_ENV'])
handler = logging.StreamHandler()
format = StackdriverFormatter()
handler.setFormatter(format)

log.addHandler(handler)
log.setLevel(logging.DEBUG)