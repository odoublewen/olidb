from oliapp import celeryapp
from scripts.run_primer3 import make_5primer_set


@celeryapp.task()
def enqueue_5primer_set(*args):
    return make_5primer_set(*args)
