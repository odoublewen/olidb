from django.db import models
from django.contrib.auth import models as authmodels
from django.utils import timezone

from celery.result import AsyncResult
from celery.states import ALL_STATES, READY_STATES

