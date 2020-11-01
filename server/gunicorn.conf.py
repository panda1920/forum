# -*- coding: utf-8 -*-
"""
This file houses configurations for gunicorn
"""
import multiprocessing

workers = 2
worker_class = 'sync'
bind = f'0.0.0.0:8000'
accesslog = '-'
loglevel = 'info'
print_config = True
