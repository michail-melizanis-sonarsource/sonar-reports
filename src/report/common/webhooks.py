from collections import defaultdict

from report.utils import generate_section
from utils import multi_extract_object_reader
from datetime import datetime, UTC, timedelta


def process_webhook(webhooks, webhook, server_id):
    webhooks[server_id][webhook['name']] = dict(
        server_id=server_id,
        key=webhook['key'],
        name=webhook['name'],
        url=webhook['url'],
        project=webhook.get('projectKey', ''),
        has_secret=webhook['hasSecret'],
        deliveries=0,
        successes=0,
        failures=0,
        last_success_date=None,
        last_success=None,
        last_error_date=None,
        last_error=None,
    )
    return webhooks


def process_delivery(webhooks, server_id, delivery):
    name = delivery['name']
    webhook = webhooks[server_id][name]
    webhook['deliveries'] += 1
    delivery_date = datetime.strptime(delivery['at'], '%Y-%m-%dT%H:%M:%S%z')

    if delivery['success']:
        webhook['successes'] += 1
        webhook['last_success_date'] = max(webhook[server_id]['last_success_date'], delivery_date)
        webhook['last_success'] = webhook['last_success_date'].strftime("%Y-%m-%d")
    else:
        webhook['failures'] += 1
        webhook['last_error_date'] = max(webhook['last_error_date'], delivery_date)
        webhook['last_error'] = webhook['last_error_date'].strftime("%Y-%m-%d")
    return webhooks


def process_webhooks(directory, extract_mapping, server_id_mapping):
    webhooks = defaultdict(dict)
    for url, webhook in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getWebhooks'):
        server_id = server_id_mapping[url]
        webhooks = process_webhook(webhooks=webhooks, webhook=webhook, server_id=server_id)
    for url, webhook in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getProjectWebhooks'):
        server_id = server_id_mapping[url]
        webhooks = process_webhook(webhooks=webhooks, webhook=webhook, server_id=server_id)
    for url, delivery in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getWebhookDeliveries'):
        server_id = server_id_mapping[url]
        webhooks = process_webhook(webhooks=webhooks, webhook=delivery, server_id=server_id)
    for url, delivery in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getProjectWebhookDeliveries'):
        server_id = server_id_mapping[url]
        webhooks = process_webhook(webhooks=webhooks, webhook=delivery, server_id=server_id)
    return webhooks

def generate_webhook_markdown(directory, extract_mapping, server_id_mapping):
    webhooks = process_webhooks(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    return generate_section(
        title='Webhooks',
        headers_mapping={
            "Server ID": "server_id",
            "Webhook Name": "name",
            "URL": "url",
            "Project": "project",
            "Deliveries": "deliveries",
            "Successful Deliveries": "successes",
            "Failed Deliveries": "failures",
            "Last Successful Delivery": "last_success",
            "Last Failed Delivery": "last_error",
        },
        rows=[webhook for server_webhooks in webhooks.values() for webhook in server_webhooks.values()],
    )