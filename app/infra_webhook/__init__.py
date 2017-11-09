from flask import Blueprint
infra_webhook = Blueprint('infra_webhook', __name__)
from . import views
