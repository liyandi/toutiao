# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-11-13
# LAST_MODIFIED : 2015年11月14日 星期六 12时25分35秒
# USAGE : python setup.py
# PURPOSE : TODO
##################################################
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='toutiaoframe',
      version='0.1',
      description='A framework for processsing Weibo-Toutiao feed',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='multiprocessinng RESTful weibo toutiao feed',
      url='',
      author='Yandi LI',
      author_email='yandi@staff.weibo.com',
      license='MIT',
      packages=['toutiaoframe'],
      install_requires=[
          'ConcurrentLogHandler',
      ],
      include_package_data=True,
      zip_safe=False)


