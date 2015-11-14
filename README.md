Toutiao Framework
=================
This work is done primarily for creating a universal framework for my recent project, 
called [Weibo Toutiao](https://play.google.com/store/apps/details?id=com.sina.app.weiboheadline), 
a news provider that collects data shared by users on weibo.com. 

Beyond its original application, I find this general design of *work flows* useful in many senarios.  
By inheriting the base class in this project, an object acquires the following,

Properties:

  * **Better parallelization**. Can run as a standalone process, harnessing the multi-core capability.
  * **Communiate** with other process through queues, 
    + Get the input from producer line,
    + Push the output to the consumer line,
    + Multiple tasks can be connected in a flexiable way, namely by the queues. 
  * **Better serialization**. A job will flow from one worker to the next 
    as soon as it's done by the first, 
    as opposed to wait till all jobs are done by the first.
  * **Flexible modes**. Try to support both ways of processing, 
    + either as **streaming** (as iterables),  
    + or as **batches** (wait until a batch of lines is collected).
  * **Automatic reloading** on updates of configuration files

---
To install, simply do `python setup.py install --user`
    
Then to use the module:

    >>> import toutiao.core as T
    >>> a = T.Core()

#### 1. Basic Usage of IO Units
We have provided the following modules to facilitate parallel IO.

* `FileIO`
* `RestfulIO`

They can be used independently to perform IO jobs, but also serve as the 
building blocks of the Toutiao Framework.

We use some examples to demonstrate the basic use of these units.

1. To write lines to a file:

        import time, random
        # register
        a = T.FileIO('newfile', 'w', append_newline=True)
        a.start()
        
        # do the job
        for i in range(10):
          time.sleep(random.uniform(0,2))
          a.en_from_queue(i)

        # signal ending
        a.end()
    The most simple test of the `FileIO` module.
    Note that by setting `append_newline=True`, the object added an newline char 
    for us before writing to a file, and
    make an internal operation to convert integers to strings.

2. To read and write using `FileIO`

        a = T.FileIO('mylogging.py', 'r', encode=None, ) # READ FROM THIS FILE                     
        b = T.FileIO('newfile', 'w', from_queue=a.IOQueue, encode=None ) # WRITE TO THIS FILE
        for p in [a, b]:
          p.start()
        for p in [a, b]:
          p.end()
    In this simple use, the first object `a` read lines and put them in its IOQueue, 
    the second object `b` fetch the content from that queue and writes to a file.
    Note that, if we set `encode=None`, no encoding convertion will be made.

3. Serial streaming of a dummy `RESTfulIO` query and a `FileIO`

        ## register work flow
        a = T.RestfulIO().config(REST_METHOD='test')
        b = T.FileIO('newfile', 'a') 
        b.IOQueue = a.to_queue
        for p in [a, b]:
          p.start()

        ## do the job
        for i in xrange(10):
          a.en_from_queue(str(i))

        ## signal ending
        for p in [a, b]:
          p.end()
    We hand in some integers to the `from_queue` of the `RESTfulIO`, 
    wait for them to flow to the `IOQueue` of `FileIO` 
    and finally got written to the target file. 
                                               
4. Perform multi-threaded RESTful queries, while writing the result to a file
    
        # register work flows
        pput = T.RestfulIO().config(REST_METHOD='insert', TABLE_NAME='article_duplicate')
        pshow = T.RestfulIO().config(REST_METHOD='show', TABLE_NAME='article_duplicate')
        pdel = T.RestfulIO().config(REST_METHOD='delete', TABLE_NAME='article_duplicate')
        pf = T.FileIO('newfile', 'a', encode='json', append_newline=True) 
        pf.IOQueue = pshow.to_queue  # THIS QUEUE HOLDS THE RESULT OF THE QUERY
        for p in [pput, pshow, pdel, pf]:
          p.start()

        ## table/show, get empty result
        for i,j in zip(['1', '2'], ['1', '1'], ):
          pshow.en_from_queue(i)

        ## table/insert,
        for i,j in zip(['1', '2'], ['1', '1'], ):
          data = {"object_id": i, "article_id": j}  
          pput.en_from_queue(data)

        time.sleep(2) # wait for insertion to finish

        ## table/show, get what we've just inserted
        for i,j in zip(['1', '2'], ['1', '1'], ):
          pshow.en_from_queue(i)

        ## table/delete, clear
        for i,j in zip(['1', '2'], ['1', '1'], ):
          data = {"object_id": i}  
          pdel.en_from_queue(data)

        time.sleep(2) # wait for deletion to finish

        ## table/show, get empty result again
        for i,j in zip(['1', '2'], ['1', '1'], ):
          pshow.en_from_queue(i)

        ## send terminate signals
        for p in [pput, pshow, pdel, pf]:
          p.end()
    During the show operation, the file handler writes the result to a file that contains,
        
        {}
        {}
        {"article_id": "1", "object_id": "1"}
        {"article_id": "1", "object_id": "2"}
        {}
        {}
    Note that we get the json format by setting `FileIO.encode` to `'json'`;
    otherwise,  if `FileIO.encode` is set to the default value `None`,
    we will get the plain string instead,

        {}
        {}
        {u'article_id': u'1', u'object_id': u'2'}
        {u'article_id': u'1', u'object_id': u'1'}
        {}
        {}
                                                                             
    Sometimes, we might prefer a Tab-seperated file than the json format.
    We make it possible, when `FileIO.encode` is set to the name of
    the keys you want to extract from the json.
    For instance, if we set `encode=['object_id', 'article_id']`, we get,
      
        ^I$
        ^I$
        1^I1$
        2^I1$
        ^I$
        ^I$
   where `^I` stands for `TAB`, `$` stands for `NEWLINE`.

#### 2. Basic Usage of Auxilary Units

* `UpdateSubsciber`

1. UpdateSubsciber

        pus = T.UpdateSubsciber(WATCH_CYCLE=20)
        pus.start()
        pus.register(pus.testfunc, ['newfile'])
        time.sleep(5)
        subprocess.check_call(["touch", "newfile"])
        time.sleep(30)
        pus.end()

#### 3. The Core Classes

* `Core`
* `Daemon`

To be continued...

