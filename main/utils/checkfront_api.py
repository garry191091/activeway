import requests
from django.conf import settings
from main.models import CheckfrontStatus
from requests.auth import HTTPBasicAuth

# Session setup
session = requests.Session()
session.auth = HTTPBasicAuth(
    settings.CHECKFRONT_API_KEY, settings.CHECKFRONT_API_SECRET
)

# Statuses configuration
CHECKFRONT_STATUSES = {
    status.status_id: status.label for status in CheckfrontStatus.objects.all()
}


def check_item_name(item_id):
    response = session.get(f"{settings.CHECKFRONT_API_BASE_URL}/item/{item_id}").json()
    return response["item"]["name"]
