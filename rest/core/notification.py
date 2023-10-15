import os
from typing import List
import requests
from core.logger import log

NOTIFICATION_PROVIDER = os.environ.get('NOTIFICATION_PROVIDER', "0f8c65d3-e4c4-4a89-b638-c31a8262e0fb")
ZENOTIFY_BASE_URL = os.environ.get('ZENOTIFY_BASE_URL', "http://zenotify.zekoder.zestudio.zekoder.zekoder.net")
ZENOTIFY_SERVICE_BASE_URL = os.environ.get('ZENOTIFY_SERVICE_BASE_URL',
                                           "http://zenotify-service.zekoder.zestudio.zekoder.zekoder.net")


def create_notification(recipients: List[str], template: str, data: dict):
    target = "email"
    try:
        json_data = {
            "recipients": recipients,
            "push_subscriptions": {},
            "provider": NOTIFICATION_PROVIDER,
            "template": template,
            "params": {"list": [data]},
            "target": [f"{target}"],
            "status": "",
            "last_error": ""
        }
        resp = requests.post(f"{ZENOTIFY_BASE_URL}/notifications/", json=json_data)
        response = resp.json()
        log.debug(f'Notification created success <{response["id"]}>')
        return response
    except Exception as e:
        log.debug(e)
        log.error("Can not create notification!")


def send_notification(notification_id: str = None):
    headers = {
        'Content-Type': 'application/json',
    }
    json_data = {"notificationId": notification_id}
    response = requests.post(f"{ZENOTIFY_SERVICE_BASE_URL}/send/email", json=json_data, headers=headers)
    log.info(response)
    if response.status_code in [200, 201]:
        log.debug(f'Notification sent!')
    else:
        log.error(response.json())
