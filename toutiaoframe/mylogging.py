# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR: Yandi LI
# DATE:   2015-03-28
# TASK:  INITIALIZE A LOGGER FOR A CLASS 
##################################################
import logging
import logging.handlers
import sys, os
from cloghandler import ConcurrentRotatingFileHandler # pip install ConcurrentLogHandler
import subprocess

class LevelFilter(object):
  """
  This is a filter which keep only a specific level
  @http://stackoverflow.com/questions/8162419/python-logging-specific-level-only
  """
  def __init__(self, level):
    self.__level = level

  def filter(self, logRecord):
    return logRecord.levelno <= self.__level


class CustomAdapter(logging.LoggerAdapter):
  """
  This example adapter expects the passed in dict-like object to have a
  'context' key, whose value in brackets is prepended to the log message.
  @https://docs.python.org/2/howto/logging-cookbook.html#context-info
  """
  def process(self, msg, kwargs):
    return '[%s]\t%s' % (self.extra['context'], msg), kwargs


def getLogger(logname='root'):
    
  logger = logging.getLogger(logname)
  logger.setLevel(logging.DEBUG)
                            
  DIR = '../log/'
  if DIR: # not none
    subprocess.check_call(['mkdir', '-p', DIR])
  #================================
  # File Handler
  #================================
  LOG_FILENAME = os.path.abspath(DIR + logname + '.err')
  handler = ConcurrentRotatingFileHandler(LOG_FILENAME, "a", 200*1024*1024, 5)
  handler.setLevel(logging.WARN)
  formatter = logging.Formatter("%(asctime)s\t%(name)s-%(process)s-%(threadName)s\t%(levelname)s\t%(message)s")
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  
  #================================
  # Standard Output Handler: INFO ONLY
  #================================
  # handler = logging.StreamHandler(sys.stdout)
  LOG_FILENAME = os.path.abspath(DIR + logname + '.info')
  handler = ConcurrentRotatingFileHandler(LOG_FILENAME, "a", 200*1024*1024, 5)
  handler.setLevel(logging.DEBUG)
  formatter = logging.Formatter("%(asctime)s\t%(name)s-%(process)s-%(threadName)s\t%(message)s")
  handler.setFormatter(formatter)
  handler.addFilter(LevelFilter(logging.INFO))
  logger.addHandler(handler)
  return logger


