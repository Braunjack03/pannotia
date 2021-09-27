import json
import pickle
import base64
import boto3
import uuid
import re
import datetime as dt
from decimal import Decimal
from multiprocessing import Process
import requests
import urllib.parse

from flask import Blueprint, render_template, request, Response, current_app, redirect
from flask_login import current_user

from .models import Dynamo
from .email_manager import read_emails, send_mail, build_lead_db, get_emails, lead_list, get_lead_data
from .tms import deg_to_num, num_to_deg


main = Blueprint('main', __name__, template_folder='templates', static_url_path='', static_folder='static')

bucket_name = "temp.pangeamaps.com"
master_file = "static/master_list_center.dat"
delete_list = "static/delete_list.json"
dynamo_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')
dynamodb_client = boto3.client('dynamodb', region_name='ap-southeast-2')
s3_client = boto3.client('s3')
sqs = boto3.client("sqs", region_name="ap-southeast-2")

currency_dict = {"AU": 'aud', "CA": 'cad', "GB": 'gbp', "US": 'usd', "NZ": 'nzd'}
currency_reverse_dict = {'aud': "AU", 'cad': "CA", 'gbp': "GB", 'usd': "US", 'nzd': "NZ"}
currency_list = ['aud', 'cad', 'gbp', 'eur', 'usd', 'nzd']

signature = '''<br>
-- 
<br>
<img src="https://www.pangeamaps.com/email/imgs/logo.png" width="130" height="111"><br><br>
WEB: www.pangeamaps.com<br>
INSTAGRAM: @pangeamaps'''


@main.route('/', methods=["GET"])
def index():
    current_app.logger.info(f'User {current_user.email} started a session')
    return main.send_static_file('index.html')


@main.route('/profile', methods=["GET"])
def profile():
    return render_template('profile.html', name=current_user.name, level=current_user.level, email=current_user.email)


@main.route('/s3/<bucket>/<path:s3key>', methods=["GET"])
def get_s3(bucket, s3key):
    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    current_app.logger.info(f'Redirection to {bucket} {s3key}')
    signed_url = s3_client.generate_presigned_url('get_object',
                                                  Params={'Bucket': bucket,
                                                          'Key': s3key},
                                                  ExpiresIn=3600)
    return redirect(signed_url)


@main.route('/lead/<lead_id>', methods=["GET"])
def get_lead(lead_id):
    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    table = dynamo_resource.Table(f"{current_app.config['USER']}Dashboard")
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')
    lead = get_lead_data(lead_id, table, lead_db)
    return Response(json.dumps(lead), mimetype="application/json")


@main.route('/draftemail/<lead_id>/<email_type>', methods=["GET"])
def draft_email(lead_id, email_type):
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')

    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    lead = lead_db.get(int(lead_id))
    currency = lead['status'].get('currency', 'usd')
    if type(currency) == int:
        currency = currency_list[currency]
    country_code = currency_reverse_dict[currency.lower()]

    body = f'''


            Kind
            regards,
            {current_user.name}
            '''
    if email_type.lower() == "quote":
        if country_code in ['AU', 'CA', 'EU', 'NZ', 'UK', 'US']:
            body = render_template(f'emails/quote_{country_code}.txt')
        else:
            body = render_template(f'emails/quote_US.txt')
    if email_type.lower() == "render":
        design_no = lead["status"].get('design', '')
        map_name = lead["status"]["mapName"]
        lead_hash = lead["status"]["id"]
        lead_name = lead["status"]["firstName"]
        design = f'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/{lead_hash}/Pangeamaps_{map_name}{design_no}.png'.replace(
            ' ', '%20')
        body = render_template('emails/design.txt', name=lead_name, design=design)
    return Response(json.dumps({"body": body}))


@main.route('/send/<lead_id>', methods=["POST"])
def send_email(lead_id):
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')

    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    data = json.loads(request.data)
    lead = lead_db.get(int(lead_id))
    email_address = lead['email']
    text_message = data['body']
    html_message = text_message.replace('\n', '<br>') + signature
    url = re.compile(r"(http[s]*://[^\s]+)")
    urls = url.findall(text_message)
    for href in set(urls):
        if href.lower().split('.')[-1] in ['jpeg', 'jpg', 'gif', 'png']:
            link = f"<img src='{href}' width=450 alt='{href}'>"
        else:
            link = "click here"
        html_message = html_message.replace(href, f"<a href='{href}'>{link}</a><br>")
        lead_hash = urllib.parse.quote(email_address)
        leads = lead_db.get(email_address, key_name="email", index_name="email-index")
        if leads:
            lead_hash = leads[0]['status'].get('id', lead_hash)
        u = urllib.parse.quote(email_address)
        html_message += f'<a href="mailto:unsubscribe@pangeamaps.com?Subject=Unsubscribe%20{lead_hash}">unsubscribe</a><br>'
    send_mail(text_message=text_message, toaddrs=email_address,
              images=[], html_message=html_message,
              mail_queue=f"{current_app.config['USER']}send_email_queue")
    return "success", 200


@main.route('/lead/<lead_id>', methods=["PUT"])
def update_lead(lead_id):
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')

    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)

    args = request.get_json(force=True)
    email = args.get("email", "").lower()
    if lead_id == 'new':
        web_id = args.get('id', uuid.uuid4().hex)
        lead_id = int(str(int(str(web_id).replace('-', ''), 16))[:15])
        args['id'] = web_id
    lead_id = int(lead_id)
    lead = lead_db.get(lead_id)
    if lead is None:
        lead = {'email': email, 'lead': lead_id, 'datetime': str(dt.datetime.now()), 'progress': 0, 'updates': [],
                'checkout': [], 'salesforce ID': None, 'state': Decimal(100)}
    if args.get("invoice", False):
        lead['invoice'] = int(args["invoice"])
    lead['email'] = email
    args['datetime']: str(dt.datetime.now())
    lead['updates'].append(args)
    lead['checkout'] = lead.get('checkout', [])
    lead_db.add(lead_id, lead)
    if args.get('topLeft', False):
        response = sqs.get_queue_url(QueueName=f"{current_app.config['USER']}lead_created")
        lead_created_queue_url = response['QueueUrl']
        sqs.send_message(QueueUrl=lead_created_queue_url, MessageBody=f"{lead_id}")
    print(lead)

    return Response(json.dumps({'id': lead_id}), mimetype="application/json")


@main.route('/status/<lead_id>/<status_code>', methods=["PUT"])
def set_status(lead_id, status_code):
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')

    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    lead_db.update_state(int(lead_id), int(status_code))
    if int(status_code) == 200:
        current_app.logger.info(f'Setting {lead_id} to 200 and sending builder request')
        # sqs.send_message(QueueUrl=lead_created_queue_url, MessageBody=f"{lead_id}")
        response = sqs.get_queue_url(QueueName=f"{current_app.config['USER']}FB_events")
        FB_events_url = response['QueueUrl']
        sqs.send_message(QueueUrl=FB_events_url, MessageBody=json.dumps(
            {"event": "CompleteRegistration", "lead": lead_id, "time": dt.datetime.now().timestamp()}))
    elif int(status_code) == 901:
        lead = lead_db.get(int(lead_id))
        email_address = lead['email']
        current_app.logger.info(f'Emailing {email_address} landscape ')
        text_message = '''
        Hi, at this time we just do waterscapes. We are launching a landscape range in a few months.
        
        Is there a waterscape we do for you?
        
        We'll keep you posted when the landscape range launches.
        
        Thanks, Tom
        '''
        html_message = text_message.replace('\n', '<br>') + signature
        send_mail(text_message=text_message, toaddrs=email_address,
                  images=[], html_message=html_message,
                  mail_queue=f"{current_app.config['USER']}send_email_queue")
    elif int(status_code) == 905:
        lead = lead_db.get(int(lead_id))
        email_address = lead['email']
        current_app.logger.info(f'Emailing {email_address} hold ')
        text_message = '''
        Ok will do, reach out when ready.
        
        Cheers, Tom
        '''
        html_message = text_message.replace('\n', '<br>') + signature
        send_mail(text_message=text_message, toaddrs=email_address,
                  images=[], html_message=html_message,
                  mail_queue=f"{current_app.config['USER']}send_email_queue")
    elif int(status_code) == 920:
        lead = lead_db.get(int(lead_id))
        email_address = lead['email']
        current_app.logger.info(f'Emailing {email_address} no data ')
        text_message = '''
        Hi, thanks for using our custom map builder!

        I've tried to download the chart for your boundary but I'm unable to retrieve the data.
        
        Is there anywhere else we can try to do for you?
        
        Kind regards, Tom
        '''
        html_message = text_message.replace('\n', '<br>') + signature
        send_mail(text_message=text_message, toaddrs=email_address,
                  images=[], html_message=html_message,
                  mail_queue=f"{current_app.config['USER']}send_email_queue")
    if int(status_code) in [911, 912, 913, 914, 900]:
        email_table = dynamo_resource.Table(f"{current_app.config['USER']}bad_email_queue")
        lead = lead_db.get(int(lead_id))
        read_emails(lead['email'], f"{current_app.config['USER']}seen_email_queue")
        email_table.put_item(Item={"email": lead['email']})
    return "success", 200


@main.route('/leads', methods=["GET"])
def get_leads():
    current_app.logger.info(request)
    db = dynamo_resource.Table(f"{current_app.config['USER']}Dashboard")
    return Response(json.dumps(lead_list(db)), mimetype="application/json")


@main.route('/emails/<lead_id>', methods=["GET"])
def get_lead_emails(lead_id):
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')

    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)

    if lead_id.isnumeric():
        lead = lead_db.get(int(lead_id))
        email_address = lead["email"]
    else:
        email_address = lead_id.lower()

    db = dynamo_resource.Table(f"{current_app.config['USER']}Dashboard")

    def email_generator(address):
        for m in get_emails(address, db):
            yield json.dumps(m) + '\n'

    return Response(email_generator(email_address), mimetype="application/json")


@main.route('/read/<lead_email>', methods=["GET"])
def read_lead_emails(lead_email):
    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    read_emails(lead_email)
    return 'success', 200


@main.route('/drawings', methods=['GET'])
def drawings():
    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)

    px2 = 360 / 2
    res = s3_client.get_object(Bucket=bucket_name, Key=master_file)
    pickle_data = res["Body"].read()
    master_list = pickle.loads(pickle_data)
    items = {
        'type': 'FeatureCollection',
        'features': []
    }
    for i, key in enumerate(master_list):
        item = master_list[key]
        if item.get('update', None):
            lat = item['center']['lat']
            lon = item['center']['lng']
            zoom = item['zoom']
            x, y = deg_to_num(lat, lon, zoom)
            lat_max, lon_max = num_to_deg(x + px2 / 512, y - px2 / 512, zoom)
            lat_min, lon_min = num_to_deg(x - px2 / 512, y + px2 / 512, zoom)
            image = key.split('\\')[-1].replace(' ', '').replace('.', '') + '.jpg'
            items['features'].append({
                'type': 'Feature',
                'properties': {'key': key, 'lat': lat, 'lng': lon, 'count': i, 'length': (lon_min - lon_max),
                               'image': f'https://s3-ap-southeast-2.amazonaws.com/temp.pangeamaps.com/{image}'},
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[[lon_min, lat_max],
                                     [lon_max, lat_max],
                                     [lon_max, lat_min],
                                     [lon_min, lat_min],
                                     [lon_min, lat_max]]]
                }
            })
        items['features'].sort(key=lambda sort_item: sort_item['properties']['length'])
    return Response(json.dumps(items), mimetype="application/json")


@main.route('/render/<lead_id>', methods=["POST"])
def set_render(lead_id):
    current_app.logger.info(f'User {current_user.email} made:')
    current_app.logger.info(request)
    req_file = request.files['file']

    update_render_daemon = Process(target=update_render, args=(lead_id, req_file.filename, req_file.stream.read()),
                                   daemon=True)
    update_render_daemon.start()
    return 'success', 200


def update_render(lead_id, file_name, file_data):
    lead_db = Dynamo(f"{current_app.config['User']}Lead", 'lead')

    if file_name.split('.')[-1].lower() in ['jpg', 'jpeg', 'png']:
        lead = lead_db.get(int(lead_id))
        design_no = lead["status"].get('design', '')
        map_name = lead["status"]["mapName"]
        lead_hash = lead["status"]["id"]
        s3_bucket = "pangea-render-data"
        s3_key = f'{lead_hash}/{map_name}{design_no}_canvas.png'
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(s3_bucket)
        bucket.put_object(Key=s3_key, Body=file_data,
                          ACL="public-read")
        s3_key = f'{lead_hash}/Pangeamaps_{map_name}{design_no}.png'
        bucket.put_object(Key=s3_key, Body=file_data,
                          ACL="public-read")
    else:
        lead_dat = lead_db.get(int(lead_id))
        uid = lead_dat['status']['id']
        url = current_app.config["BUILDER_URL"] + f'lead/{lead_id}/'
        res = requests.get(url)
        para = res.json()
        top_left = lead_dat['status']['topLeft']
        bottom_right = lead_dat['status']['bottomRight']
        size = lead_dat['status'].get('size', 0)
        if size.split('x') > 1:
            size = size
        else:
            sizes = [430, 600, 830]
            size = f'{sizes[size]}x{sizes[size]}'
        unit = lead_dat['status'].get('units', 'metric')
        if unit == 'metric':
            unit = 'M'
        else:
            unit = 'FT'
        bounds = [top_left['lat'], top_left['lng'], bottom_right['lat'], bottom_right['lng']]
        params = f"?extent={','.join([f'{x}' for x in bounds])}" \
                 f"&mark=[{para['mark'].replace(' ', ',')}]" \
                 f"&marksize=4&" \
                 f"minContour=15&" \
                 f"minIsland=10&" \
                 f"smoothing=10&" \
                 f"landSmoothing=0&" \
                 f"boundary=10&" \
                 f"buffer=2" \
                 f"&name={para['name']}" \
                 f"&msg=" \
                 f"&size={size}" \
                 f"&units={unit}" \
                 f"&samples=150" \
                 f"&resolution=1500" \
                 f"&res=1500" \
                 f"&output=jpeg" \
                 f"&levelid={uid}" \
                 f"&waterbuffer=0" \
                 f"&design_number=0"
        json_data = {'level': f'data:application/zip;base64,{base64.b64encode(file_data).decode()}'}
        requests.post(current_app.config["BUILDER_URL"] + f'lead/{lead_id}/' + params, json=json_data)
