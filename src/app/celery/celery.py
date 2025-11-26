from dotenv import load_dotenv

from . import make_celery

load_dotenv()

celery = make_celery()
