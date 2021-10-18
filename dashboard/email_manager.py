#!/usr/bin/env python
import math
import json
import boto3
from boto3.dynamodb.conditions import Key
import logging
import datetime as dt


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger()

currency_dict = {"AU": 'aud', "CA": 'cad', "GB": 'gbp', "US": 'usd', "NZ": 'nzd'}
currency_list = ['aud', 'cad', 'gbp', 'eur', 'usd', 'nzd']


def build_lead_db():
    pass


def lead_list(db):
    lead_types = {
        "New": [],
        "Quoted": [],
        "Design": [],
        "Invoice": [],
        "Production": [],
        "Other": [],
    }
    response = db.scan()
    response['LastEvaluatedKey'] = response.get('LastEvaluatedKey')
    while 'LastEvaluatedKey' in response:
        for lead in response.get('Items', []):
            lead_data = json.loads(lead["json"])
            lead_types[lead_data["type"]].append({"email": lead["email"], "leads": lead_data["leads"]})
        if response['LastEvaluatedKey']:
            response = db.query(ExclusiveStartKey=response['LastEvaluatedKey'])
        else:
            break
    return lead_types


def get_lead_data(lead_id, leads_table, lead_db):
    if lead_id.find('@') >= 0:
        leads = lead_db.get(lead_id, key_name="email", index_name="email-index")
        if len(leads):
            lead = leads[0]
            lead_id = int(lead["lead"])
        else:
            return {"email": lead_id}
    else:
        lead = lead_db.get(int(lead_id))
        lead_id = int(lead["lead"])
    lead_email = lead["email"]
    lead_entry = leads_table.query(KeyConditionExpression=Key('email').eq(lead_email)).get("Items", [None])[0]
    if lead_entry is None:
        lead_entry = {"emails": [{
            "date": str(dt.datetime.now()),
            "timestamp": dt.datetime.now().timestamp(),
            "to": '',
            "from": '',
            "subject": '',
            "body": "No unread email to display",
            "flags": "SEEN",
        }], "total": "error"}
    else:
        lead_entry = json.loads(lead_entry['json'])
    lead_map = lead["status"]["mapName"]
    lead_hash = lead["status"]["id"]
    lead_state = int(lead.get("state", 9999))
    lead_name = lead["status"]["firstName"]
    map_mark = lead["status"].get("poi", {'lat': 0.0, 'lng': 0.0})
    map_center = {'lng': (lead["status"]["topLeft"]["lng"] + lead["status"]["bottomRight"]["lng"]) / 2,
                  'lat': (lead["status"]["topLeft"]["lat"] + lead["status"]["bottomRight"]["lat"]) / 2}
    map_zoom = lead["status"]["mapZoom"]
    map_zoom = math.log2(2 ** map_zoom * 350 / 400)
    map_size = lead["status"].get('size', "1")
    if len(map_size) != 1:
        map_size = {'430x430': '0', '600x600': '1', '830x830': '2', '17.5x17.5': '0', '24x24': '1', '32x32': '2'}.get(
            map_size, '1')
    map_invoice = int(lead.get("invoice", 0))
    map_units = lead["status"].get('units', False)
    unit = 'mm'
    if not map_units:
        map_units = "metric"
        unit = 'mm'
        if lead["status"].get("ipCountry") == "US":
            map_units = 'imperial'
            unit = '"'
    size_dict = {'mm': ['430x430', '600x600', '830x830'], '"': ['17.5x17.5', '24x24', '32x32']}
    map_description = lead["status"].get("description",
                                         f"Map Size: {size_dict[unit][int(map_size)]}{unit} + FREE Wooden Gift Box")
    if map_description.find('Size') < 0:
        map_description = f"Map Size: {size_dict[unit][int(map_size)]}{unit} + FREE Wooden Gift Box"
    map_price = lead["status"].get('price', 9999)
    map_phonenumber = lead["status"].get('phonenumber', 0)
    map_production = lead["status"].get('production', False)
    if not map_production:
        map_production = "Australia"
        if lead["status"].get("ipCountry") == "CA":
            map_production = 'Canada'
    lead_currency = lead["status"].get("currency", False)
    if not lead_currency:
        lead_currency = currency_dict.get(lead["status"].get("ipCountry"), 'usd')
    if type(lead_currency) == int or len(lead_currency) == 1:
        lead_currency = currency_list[int(lead_currency)]
    map_address = lead["status"].get('address', {})
    render = lead["status"].get("render", "https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/Pangea.png")
    lead = {"id": lead_id, "map": lead_map, "hash": lead_hash, "state": lead_state, "name": lead_name,
            "email": lead_email, "center": map_center, "zoom": map_zoom, "mark": map_mark, "address": map_address,
            "size": map_size, "units": map_units, "production": map_production, "price": map_price,
            "description": map_description, "currency": lead_currency, "invoice": map_invoice,
            "emails": lead_entry["emails"][0], "render": render, "total": lead_entry["total"],
            "phonenumber":map_phonenumber}
    return lead


def get_emails(customer, db):
    response = db.query(KeyConditionExpression=Key('email').eq(customer))
    lead = response["Items"][0]
    lead_data = json.loads(lead["json"])
    for message in lead_data['emails']:
        yield message


def read_emails(email_address, seen_queue=None):
    if seen_queue:
        email_to_read = {"email_address": email_address}
        sqs = boto3.client("sqs", region_name="ap-southeast-2")
        response = sqs.get_queue_url(QueueName=seen_queue)
        seen_queue = response['QueueUrl']
        sqs.send_message(QueueUrl=seen_queue, MessageBody=json.dumps(email_to_read))


def send_mail(text_message, toaddrs, images=None, html_message=None, mail_queue=None):
    if mail_queue:
        email_content = {"text": text_message, "to": toaddrs}
        if images:
            email_content['images'] = images
        if html_message:
            email_content['html'] = html_message
        sqs = boto3.client("sqs", region_name="ap-southeast-2")
        response = sqs.get_queue_url(QueueName=mail_queue)
        sent_email_url = response['QueueUrl']
        sqs.send_message(QueueUrl=sent_email_url, MessageBody=json.dumps(email_content))
