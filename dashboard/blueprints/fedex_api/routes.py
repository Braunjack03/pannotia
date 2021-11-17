import json
from datetime import datetime
from functools import wraps

import boto3

from dashboard.models import Dynamo
from dashboard.main import get_lead
from dashboard import f_oauth
from dashboard.email_manager import get_lead_data
from dashboard.config_fedex import ApiConf
from dashboard.blueprints.fedex_api.forms import CreateShipmentForm
from dashboard.blueprints.fedex_api.utils import (save_response, send_request, AddressParser, Endpoints)
from flask import (Blueprint, current_app, flash, render_template, request, session, redirect, url_for)

fedex = Blueprint('fedex', __name__, template_folder='templates',
                  static_url_path='', static_folder='../../static')

# api_client = oauth.create_client('fedex')
api_client = f_oauth.register(
    'fedex',
    client_id=ApiConf.api_key,
    client_secret=ApiConf.secret_key,
    grant_type=ApiConf.grant_type,
    token_endpoint_auth_method=ApiConf.token_endpoint_auth_method,
    token_endpoint=Endpoints().urls.get('token_endpoint')
)
dynamo_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')


def obtain_fedex_oauth2_token():
    fedex_token = session.get('fedex_token')
    expires_at = session.get('fedex_token_expires_at')

    if not expires_at or not fedex_token:
        return None
    need_to_refresh = datetime.now() > datetime.fromtimestamp(int(expires_at))
    # need_to_refresh =  True  # for testing only
    if need_to_refresh:
        return None

    return fedex_token


def fetch_and_save_token():
    resp = api_client.fetch_access_token()
    if resp:
        session["fedex_token"] = resp.get('access_token')
        session["fedex_token_expires_at"] = resp.get('expires_at')
        return resp
    return {'err': 'fetch token error'}


def fedex_token_required(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        fedex_token = obtain_fedex_oauth2_token()
        if not fedex_token:
            fetch_and_save_token()
            # return redirect(url_for("fedex.login", _external=True))

        return function(*args, **kwargs)

    return decorator


@fedex.route('/login')
def login():
    resp = fetch_and_save_token()
    if resp:
        return resp
    return {'err': 'fetch token error'}


@fedex.route('/shipment/get/<string:lead_id>', methods=['GET'])
@fedex_token_required
def get_shipment(lead_id):
    table = dynamo_resource.Table(f"{current_app.config['USER']}Dashboard")
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", 'lead')
    lead = get_lead_data(lead_id, table, lead_db)
    url = lead.get('shipping')
    if url is None:
        url = url_for('fedex.create_shipment', lead_id=lead_id)
    return redirect(url)


@fedex.route('/shipment/create/', methods=['GET', 'POST'])
@fedex.route('/shipment/create/<string:lead_id>', methods=['GET', 'POST'])
@fedex_token_required
def create_shipment(lead_id='188602483043329'):
    form = CreateShipmentForm(request.form)

    if request.method == 'POST' and form.validate():
        token = session.get('fedex_token')
        form_data = form
        if form.validate_address.data:
            request_type = 'validate_address'
            success = 'Address valid'
        else:
            request_type = 'create_shipment'
            success = 'Shipment created'

        resp = send_request(form_data, token, request_type=request_type)
        if resp.status_code == 200:
            if request_type == 'validate_address':
                success = resp.json()["output"]['resolvedAddresses'][0]
            current_app.logger.info(f'Shipment created {resp.status_code}')
            save_response(resp.json(), lead_id, request_type=request_type)
            flash(success, 'success')
        elif resp.status_code >= 400:
            current_app.logger.info(f'ERROR: resp code {resp.text}')
            flash(
                f'ERROR: resp code -> {resp.status_code} , details: {resp.text}', 'danger')
        else:
            current_app.logger.info(f'UNKNOWN ERROR: resp code {resp.text}')
            flash(
                f'UNKNOWN ERROR: resp code -> {resp.status_code} , details: {resp.text}', 'danger')

    elif request.method == "GET":
        lead = get_lead(lead_id)
        lead_data = json.loads(lead.data)
        form.recipients_personName.data = lead_data.get('name')
        form.recipients_phoneNumber.data = lead_data.get('phonenumber')
        form.recipients_emailAddress.data = lead_data.get('email')
        # address
        addr_parser = AddressParser(lead_data.get('address'))
        form.recipients_address_line_1.data = addr_parser.get_address_line_1()
        form.recipients_stateOrProvinceCode.data = addr_parser.get_province_code()
        form.recipients_countryCode.data = addr_parser.get_country_code()
        form.recipients_city.data = lead_data.get('address').get('city') or lead_data.get('address').get('city2')
        form.recipients_postalCode.data = lead_data.get('address').get('postal_code')
        # package details
        form.commodities_quantity.data = 1
        form.commodities_unit_price_amount.data = lead_data.get('price', 111)
        form.commodities_unit_currency.data = lead_data.get('currency', 'USD').upper()
        form.commodities_weight_units.data = 'KG'
        form.commodities_size_units.data = 'CM'
        size = int(lead_data.get('size', 2))
        if size == 0:
            form.commodities_unit_weight.data = 4
            form.commodities_size_length.data = 45
            form.commodities_size_width.data = 45
            form.commodities_size_height.data = 9
        elif size == 1:
            form.commodities_unit_weight.data = 7
            form.commodities_size_length.data = 63
            form.commodities_size_width.data = 63
            form.commodities_size_height.data = 9
        elif size == 2:
            form.commodities_unit_weight.data = 10
            form.commodities_size_length.data = 90
            form.commodities_size_width.data = 90
            form.commodities_size_height.data = 9
        else:
            form.commodities_unit_weight.data = 7
            form.commodities_size_length.data = 63
            form.commodities_size_width.data = 63
            form.commodities_size_height.data = 9

    return render_template('fedex_api/create_shipment.html', form=form)