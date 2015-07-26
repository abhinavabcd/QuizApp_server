'''
Created on Jul 25, 2015

@author: abhinav
'''
import logging
from logging.handlers import TimedRotatingFileHandler
from server import configuration


# log start
def create_timed_rotating_log(path):
    """"""
    logger = logging.getLogger("Quizapp time log")
    logger.setLevel(logging.INFO)
 
    handler = TimedRotatingFileHandler(path,
                                       when="H",
                                       interval=1,
                                       backupCount=240)
    logger.addHandler(handler)
    return logger



logger = create_timed_rotating_log('quizapp_logs/quizapp'+"_"+ configuration.serverId +'.log')