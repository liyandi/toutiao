# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-09-15
# LAST_MODIFIED : 2015年11月14日 星期六 16时46分14秒
# USAGE : python core.py
# PURPOSE : TODO
##################################################
import mylogging
import threading
import multiprocessing
import multiprocessing.queues as Queue
import os, time
import requests, json


logging = mylogging.getLogger('Core')


class FileIO(threading.Thread):
  """
  Class that interacts with files.
  When initiated with read method, reads lines from a file with
  a given filename and inserts into its queue;
  When initiated with write method, read from its own queue 
  and write to a file in system
  """
  def __init__(self, filename, file_method='r', IOQueue=None,
              daemon=False, encode='utf-8', append_newline=True):
    """
    @Parameters
    --------------------------
    | filename: str
    | file_method: 'r', 'w', 'a'
    | IOQueue: queue for data exchange, 
    |          to_queue if method is 'r', from_queue if method is 'w', 'a'
    | daemon: wheher run as daemon
    | encode: 
    |        'utf-8': encode each line by utf-8 for writing
    |        'json': encode dict by json
    |        list: convert a dict to a tsv based on a list of keys,
    |              e.g., if {"object_id":1, "article_id":2} => '1\t2' if provided list=['object_id', 'article_id'] 
    |              only use in the 'w', 'a' modes
    |        None: encode each line by str()
    | append_newline: append a '\n' to each line for writing
    """
    super(self.__class__, self).__init__()
    self.file_method = file_method
    self.filename = filename
    self.daemon = daemon
    self.IOQueue = IOQueue if IOQueue else Queue.Queue()
    self._format = self._build_formatter(self.file_method, encode, append_newline) 


  @property
  def IOQueue(self):
    """
    An iterable element/pointer.      
    If init method is set to read, the object read from a file into this queue.
    If init method is set to write, the object read from this queue and write to a file.
    """
    return self._queue


  @IOQueue.setter
  def IOQueue(self, q):
    if isinstance(q, Queue.Queue):
      self._queue = q
    else:
      logging.error('DENIED: Please use multiprocessing.queues.Queue for save IO.')


  @property
  def formatter(self):
    """ Defines how a line is encoded to write 
    """
    return self._format


  @formatter.setter
  def formatter(self, formatter):
    if formatter and hasattr(formatter, '__call__'):
      self._format = formatter


  @staticmethod
  def _build_formatter(file_method, encode='utf-8', append_newline=True):
    """ Defines how a line is encoded to write 
    """
    assert file_method in ['r', 'w', 'a']
    if file_method in ['w', 'a']:
      nstr = '\n' if append_newline else ''
      if encode == 'utf-8':
        formatter = lambda x: (('{0}' + nstr).format(x)).encode('utf-8')
      elif encode == 'json':
        formatter = lambda x: ('{0}' + nstr).format(json.dumps(x))
      elif isinstance(encode, list):
        def dict2csv(di, keys):
          res = '\t'.join([di.get(k, '') for k in keys]) 
          if isinstance(res, unicode):
            return res.decode('utf-8') + nstr
          else:
            return res + nstr
        formatter = lambda x: dict2csv(x, encode)
      else:
        formatter = lambda x: ('{0}' + nstr).format(x)
      return formatter

    elif file_method in ['r']:
      if encode == 'utf-8' and append_newline:
        formatter = lambda x: x.decode('utf-8').rstrip('\r\n')
      elif encode == 'utf-8' and not append_newline:
        formatter = lambda x: x.decode('utf-8')
      else:
        formatter = lambda x: x
      return formatter
   

  def run(self):
    """
    Main function, called when start() is called. 
    Call the queue IO and get things done.
    """
    self._irun()


  def end(self):             
    """
    Interface function, used to end the daemon and kill the wait.
    End of start()
    """
    if self.file_method in ['w', 'a']:
      self.en_from_queue(None) # send terminate signal to workers
    self.join() # stop the thread itself


  def en_from_queue(self, line):
    """
    Interface function, add data to the waiting list queue to triger our workers
    """
    self._queue.put(line)
    

  def _irun(self):
    """
    Main IO between the queue and the file
    """
    f = open(self.filename, self.file_method)
    if self.file_method == 'r':
      logging.debug("STARTING WORKERS: %s", 'reader')
      for line in f:
        try:
          self._queue.put(line)
        except:
          logging.exception(line)
      logging.debug("WORKER SESSION ENDED: %s", 'reader')
    elif self.file_method in ['w', 'a']:
      logging.info("STARTING WORKERS: %s", 'writer')
      while True:
        try:
          line = self._queue.get()
          if line is not None:
            f.write(self._format(line))
            logging.debug("Processed: %s", line)
          else:
            logging.info("WORKER SESSION ENDED: %s", 'writer')
            ## CLEANUP THE REST OF THE QUEUE
            while True:
              try:
                line = self._queue.get_nowait()
                if not line: continue
                f.write(self._format(line))
                logging.info("MORE LINE AFTER TERM_SIG: %s", line)
              except Queue.Empty:
                break
            ## END THE JOB
            break
        except:
          logging.exception(line)



class UpdateSubsciber(threading.Thread):
  """
  Class that records the configuration files that some class/function depends.
  When an object registers to this thread, it routinely checks the last modified time of config files,
  and once any change is detected, the thread calls back registered function, 
  e.g., so the class variables will be updated.
  """

  def __init__(self, WATCH_CYCLE=300, daemon=True):
    """
    @Parameters
    -------------------------
    | WATCH_CYCLE: number of seconds for a watch-cycle
    """
    super(self.__class__, self).__init__()
    self.daemon = daemon
    self.registerTable = {}
    self.WATCH_CYCLE = WATCH_CYCLE
    self._keep_alive = True


  @property
  def registerTable(self):
    """ A dict that records the following,
    ---------------------------
    objectCallBack : {
       'configFiles': {'filename1': last_modified,
                       'filename2': last_modified
                      } 
    }
    """
    return self._registerTable


  @registerTable.setter
  def registerTable(self, table):
    self._registerTable = table


  def register(self, objectCallBack, configFiles,):
    """ Register the config files of a class and a call back to its _config()
    @Parameters
    -------------------------------
    | objectCallBack: subcriber's callback function e.g, reload class_variables, 
    |                 when some files are updated. 
    |                 subcriber can be an object, a class name, or any functions
    | configFiles: list of file names
    """
    self._registerTable[objectCallBack] = {'configFiles': {}}
    for fname in configFiles:
      self._registerTable[objectCallBack]['configFiles'][fname] = os.stat(fname).st_mtime
      logging.debug("FILE REGISTERED: calls %s when %s changes", objectCallBack, fname)


  def run(self):
    """ Main interface function, called when start() is called. 
    """
    self._irun()


  def end(self):             
    """
    Interface function, used to end the daemon and kill the wait.
    End of start()
    """
    self._keep_alive = False
    self.join() # stop the thread itself

  
  def testfunc(self):
    logging.info("TEST FUNCTION CALLED, registerTable %s", self.registerTable)


  def _irun(self):
    """ Main, check the register table regularily. Update if neccessary.
    """
    logging.info('STARTING WORKER: %s', self)
    while self._keep_alive:
      for objectCallBack in self._registerTable:
        is_modified = False
        configFiles = self._registerTable[objectCallBack]['configFiles']

        for fname, mtime in configFiles.iteritems():
          ntime = os.stat(fname).st_mtime
          if ntime != mtime:
            is_modified = True
            logging.info("CONFIG FILE MODIFIED: %s AT %s", fname, ntime)
            break

        if is_modified:
          for fname in configFiles:
            self._registerTable[objectCallBack]['configFiles'][fname] = os.stat(fname).st_mtime
          ## call the subscriber's call backs
          objectCallBack()
          logging.info("CALLS BACK DONE: %s", objectCallBack.func_name)

      if self._keep_alive:
        time.sleep(self.WATCH_CYCLE)
    logging.info('WORKER SESSION ENDED: %s', self)



class Core(multiprocessing.Process):
  """
  Central Processing Unit
  Defines a pure virtual class with a bunch of handy properties:
  * Can run as a standalone process, harnessing the multi-core capability.
  * Communiate with other process through queues, 
    + Get the input from producer line,
    + Push the output to the consumer line,
    + Multiple tasks can be connected in a flexiable way, by the queues. 
  * A job will flow from one worker to the next as soon as it's done by the first, 
    as opposed to wait till the last job leaves the hand of the first worker.
  * Try to support both ways of processing, 
    + either as streaming (as iterable),  
    + or wait until a batch of lines is collected
  Features:
  * basic from_queue and to_queue structure
  * automatic updates of configuration files
  """
  def __init__(self,
                from_queue=None,
                to_queue=None,
                daemon=False):
    """
    @Parameter
    --------------------------
    | from_queue: where the workers get input from
    | to_queue: where the workers put the results
    | daemon: if runs as daemon process
    """
    super(Core, self).__init__()
    self.daemon = daemon
    self.from_queue = from_queue if from_queue else Queue.Queue()
    self.to_queue = to_queue if to_queue else Queue.Queue()


  @property
  def from_queue(self):
    """
    An iterable element/pointer.      
    The object reads from this queue.
    """
    return self._from_queue


  @from_queue.setter
  def from_queue(self, q):
    if isinstance(q, Queue.Queue):
      self._from_queue = q
    else:
      logging.error('DENIED: Please use multiprocessing.queues.Queue for save IO.')


  @property
  def to_queue(self):
    """
    An iterable element/pointer.      
    The object writes results to this queue.
    """
    return self._to_queue


  @to_queue.setter
  def to_queue(self, q):
    if isinstance(q, Queue.Queue):
      self._to_queue = q
    else:
      logging.error('DENIED: Please use multiprocessing.queues.Queue for save IO.')


  def en_from_queue(self, line):
    """
    Interface function, add data to the waiting list queue to triger our workers
    """
    self.from_queue.put(line)


  @staticmethod
  def tee(cins, to_queues):
    """
    Put an identical copy of a stream into a set of queues
    Useful in case for example if you want to write a stream to a file and an API in parallel
    @Parameters
    -----------------------------------
    | cins: iterable
    | to_queues: a set/list of queue objects
    """
    for cin in cins:
      for to_queue in to_queues:
        to_queue.put(cin)



class RestfulIO(Core):
  """  
  Have to be initialized with config(), setting basic params of the Restful query.
  """
  def config(self, 
              REST_METHOD= 'insert', 
              TABLE_NAME='', 
              APPSOURCE=2936099636, APPKEY=1428722706):
    """ Set model parameters
    @Parameters
    -----------------------------
    | REST_METHOD: one of 'insert', 'delete', 'show', 'test'. 
                An isinstance can perform only one kind of the operations.
    | TABLE_NAME: table name of the restful service, REQUIRED
    | SCHEMA: list, column names of the target table, REQUIRED,
              e.g., ["object_id", "article_id"] in order
    | APPSOURCE: source of the restful service, defaulted
    | APPKEY: appkey of the restful, defaulted
    """
    assert REST_METHOD in ["insert", "delete", "show", "test"]
    self.REST_METHOD = REST_METHOD # defines what moves will the workers takes
    self.TABLE_NAME = TABLE_NAME
    self.APPSOURCE = APPSOURCE
    self.APPKEY = APPKEY
    return self


  @staticmethod
  def postDataArgs(data, TABLE_NAME, APPSOURCE, APPKEY):
    urlargs = {'source': APPSOURCE,
                'data': json.dumps({
                      'appkey': APPKEY,
                      'table': TABLE_NAME,
                      'columns': data
                      })
              }
    return urlargs


  @staticmethod
  def getDataArgs(key, TABLE_NAME, APPSOURCE, APPKEY):
    urlargs = {'source': APPSOURCE,
               'appkey': APPKEY,
               'table': TABLE_NAME,
               "cache": False,
               'key': key
              }
    return urlargs


  def request(self, url, params, method='get', TRYOUT=3, TIMEOUT=5):
    """
    >>> a.request('http://i2.api.weibo.com/2/statuses/querymid.json', {'source':'445670032', 'type':1, 'id': 3512191498379699})
    {u'mid': u'z579Hz9Wr'}
    """
    for i in xrange(TRYOUT):
      try:
        if method == 'get':
          urlargs = self.getDataArgs(params, self.TABLE_NAME, self.APPSOURCE, self.APPKEY)
          req = requests.get(url, params=urlargs, timeout=TIMEOUT)
        else: # method == 'post':
          urlargs = self.postDataArgs(params, self.TABLE_NAME, self.APPSOURCE, self.APPKEY)
          req = requests.post(url, data=urlargs, timeout=TIMEOUT)
        if req:
          res = req.json()
          return res
      except requests.RequestException:
        continue
    else:
      logging.warning('TRYOUT\t%s\t%s\t%s', url, urlargs, req.text) 
      return {}


  def insertIntoDB(self, data):
    """
    @Parameters
    ---------------------------
    | data: single line of data as dict 
    |       e.g. {"object_id": object_id, "article_id": article_id} 
    @Returns
    ---------------------------
    | json result, e.g., {"result": True} 
    """
    try:    
      url = 'http://i2.api.weibo.com/2/darwin/table/put.json'
      res = self.request(url, data, 'post')
      if not res or 'error' in res:
        logging.error('PUT ERROR\t%s', data)
        return {}
      if 'result' not in res:
        logging.warning('PUT FAIL'+'\t%s', data)
        return {}
      else:
        logging.info('PUT SUCCESS'+'\t%s'*2, data, res)
        return res
    except:
      logging.exception('PUT UNKNOWN ERROR'+'\t%s'*2, data, self.TABLE_NAME)
      return {}


  def deleteFromDB(self, data):
    """
    @Parameters
    ---------------------------
    | data: single line of data as dict, 
    |       e.g.,{"object_id": object_id, "article_id": article_id} 
    |       or just the a primary key, {"object_id", object_id}
    @Returns
    ---------------------------
    | json result, e.g., {"result": True} 

    """
    try:
      url = 'http://i2.api.weibo.com/2/darwin/table/delete.json?'
      res = self.request(url, data, 'post')
      if not res or 'error' in res:
        logging.error('DELETE ERROR\t%s', data)
        return {}
      if 'result' not in res:
        logging.warning('DELETE FAIL'+'\t%s', data)
        return {}
      else:
        logging.info('DELETE SUCCESS'+'\t%s'*2, data, res)
        return res
    except:
      logging.exception('DELETE UNKNOWN ERROR'+'\t%s'*2, data, self.TABLE_NAME)
      return {}


  def showDB(self, key):
    """
    @Parameters
    ---------------------------
    | key: a line of the a primary key of the table, e.g. object_id
    @Returns
    ---------------------------
    | json result, e.g., {"article_id":" 1022:2222", "object_id": "321232:12213"} 

    """
    try:
      url = 'http://i2.api.weibo.com/2/darwin/table/show.json?'
      res = self.request(url, key, 'get')
      if not res or 'error' in res:
        logging.error('SHOW ERROR\t%s', key)
        return {}
      if 'columns' not in res:
        logging.warning('SHOW FAIL'+'\t%s', key)
        return {}
      else:
        res = res['columns']
        logging.info('SHOW SUCCESS'+'\t%s'*2, key, res)
        self.to_queue.put(res) # en_to_queue
        return res
    except:
      logging.exception('SHOW WITH UNKNOWN ERROR'+'\t%s'*2, key, self.TABLE_NAME)
      return {}


  def testfunc(self, line):
    """
    Dummy for test purpose
    """
    logging.info("Processed: %s", line)
    self.to_queue.put(line+'\n') # en_to_queue
    logging.info("Length of to_queue: %d", self._to_queue.qsize())


  def end(self, TIMEOUT=None):             
    """
    Interface function, used to end the daemon and kill the wait.
    End of start()
    """
    self.en_from_queue(None) # send terminate signal to workers
    # self.queue.join() # wait until the waiting list is empty
    self.join(timeout=TIMEOUT) # stop the thead itself


  def run(self):
    """
    Main function, called when start() is called. 
    Call the queue consumer and get things done.
    """
    if self.REST_METHOD == 'insert':
      self._irun(self.insertIntoDB)
    elif self.REST_METHOD == 'delete':
      self._irun(self.deleteFromDB)
    elif self.REST_METHOD == 'show':
      self._irun(self.showDB)
    elif self.REST_METHOD == 'test':
      self._irun(self.testfunc)


  def _irun(self, func, NUM_THREAD=1000):
    """ Read from from_queue and send lines to database via Restful.
    Ends when a None/empty string is put in the from_queue
    @Parameters
    ---------------------------
    | func: one of the callback functions, insertIntoDB, deleteFromDB, showDB, 
    |         who works on a single line of data
    | KEEP_RETURNS: True if we want to keep the result in the to_queue, False if we 
    |               want to discard the result
    | NUM_THREAD: number of threads for calling the Restful service
    @Returns
    ---------------------------
    | to_queue is filled with results
    """
    workers = []; count = 0
    logging.info("STARTING WORKERS: %s", func.func_name)
    while True:
      try:
        line = self._from_queue.get()
        logging.debug("Got from queue: %s", line)
        if line is not None:
          worker = threading.Thread(target=func, args=(line, ))
          workers.append(worker)
          worker.start(); count += 1
          if count % NUM_THREAD == 0:
            for worker in workers:
              worker.join(timeout=10)
            workers = []; count = 0
        else:
          ## if an end is signaled, clear the remaining queue, w/o waiting
          while True:
            try:
              line = self._from_queue.get_nowait()
              if not line: # skip any empty lines after the terminate signal
                continue
              worker = threading.Thread(target=func, args=(line, ))
              workers.append(worker)
              worker.start(); count += 1
              if count % NUM_THREAD == 0:
                for worker in workers:
                  worker.join(timeout=10)
                workers = []; count = 0
              logging.info("MORE LINE AFTER TERM_SIG: %s", line)
            except Queue.Empty:
              break
            except:
              logging.exception('UNKNOWN ERROR IN LINE\t%s', line.strip())
              continue
          if len(workers) > 0:
            for worker in workers:
              worker.join(timeout=10)
          logging.info('WORKER SESSION ENDED: %s', func.func_name)
          break
      except Queue.Empty:
          if len(workers) > 0:
            for worker in workers:
              worker.join(timeout=10)
          logging.info('NO MORE INPUT/END_OF_FILE AFTER TIMEOUT, WORKER SESSION ENDED')
          break
      except:
        logging.exception('UNKNOWN ERROR IN LINE\t%s', line.strip())
        continue
        


if __name__ == "__main__":
  pass

