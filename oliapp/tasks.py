from lib.run_primer3 import make_5primer_set
from oliapp import celeryapp

@celeryapp.task()
def enqueue_5primer_set(*args):
    return make_5primer_set(*args)
