import json
from datetime import datetime
from functools import wraps

from dashboard import f_oauth
from dashboard.config_fedex import ApiConf
from dashboard.blueprints.fedex_api.settings import Endpoints

from dashboard.blueprints.fedex_api.forms import CreateShipmentForm
from dashboard.blueprints.fedex_api.payloads import (create_shipment_json,
                                                     validate_shipment_json)
from dashboard.blueprints.fedex_api.utils import (save_response, send_request,
                                                  shipment_sample, AddressParser,
                                                  validate_shipment_sample)
from dashboard.main import get_lead
from flask import (Blueprint, Response, current_app, flash, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user


fedex = Blueprint('fedex', __name__, template_folder='templates',
                  static_url_path='', static_folder='static')


# api_client = oauth.create_client('fedex')
api_client = f_oauth.register(
    'fedex',
    client_id=ApiConf.api_key,
    client_secret=ApiConf.secret_key,
    grant_type=ApiConf.grant_type,
    token_endpoint_auth_method=ApiConf.token_endpoint_auth_method,
    token_endpoint=Endpoints().urls.get('token_endpoint')
)


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


@fedex.route('/')
def index():
    return {'response': 'Index page'}


@fedex.route('/login')
def login():
    resp = fetch_and_save_token()
    if resp:
        return resp
    return {'err': 'fetch token error'}


@fedex.route('/create', methods=["GET"])
@fedex_token_required
def create_shipment_demo():
    token = session.get('fedex_token')

    input_data = create_shipment_json.get('One_Rate_Shipment')
    response = shipment_sample(input_data, token)
    # print(response)
    if response.status_code == 200:
        res = json.loads(response.content)
        return {'response': res}
    return {'error': response}


@fedex.route('/validate', methods=["GET"])
@fedex_token_required
def validate_shipment():
    import json
    token = session.get('fedex_token')

    input_json = validate_shipment_json.get('Minimal_Sample_Domestic')
    inp_d = json.loads(input_json)
    inp_j = json.dumps(inp_d)
    # input_data = Minimal_Sample_Domestic
    response = validate_shipment_sample(inp_j, token)
    print(response)
    return {'response': 'validate'}


@fedex.route('/shipment/create/', methods=['GET', 'POST'])
@fedex.route('/shipment/create/<string:lead_id>', methods=['GET', 'POST'])
@fedex_token_required
def create_shipment(lead_id='188602483043329'):
    form = CreateShipmentForm(request.form)

    if request.method == 'POST' and form.validate():
        token = session.get('fedex_token')
        form_data = form
        resp = send_request(form_data, token, request_type='create_shipment')

        if resp.status_code == 200:
            current_app.logger.info(f'Shipment created {resp.status_code}')
            save_response(resp)
            flash('Shipment created', 'success')
        elif resp.status_code >= 400:
            # TODO record in log or in DB
            current_app.logger.info(f'ERROR: resp code {resp.text}')
            flash(
                f'ERROR: resp code -> {resp.status_code} , details: {resp.text}', 'danger')

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
        form.recipients_city.data = lead_data.get('address').get('city')
        form.recipients_postalCode.data = lead_data.get(
            'address').get('postal_code')
        # package details
        form.commodities_description.data = lead_data.get('description')
        form.commodities_quantity.data = lead_data.get('total')
        form.commodities_unit_price_amount.data = lead_data.get('price')
        form.commodities_unit_currency.data = lead_data.get('currency').upper()
        # form.commodities_unit_weight.data = lead_data.get()
        # form.commodities_weight_units.data = lead_data.get('units')

    return render_template('fedex_api/create_shipment.html', form=form)
