import json
from functools import wraps
from datetime import datetime
from flask import (Blueprint, render_template, request,
                   Response,  redirect, session, flash, url_for)
from flask_login import current_user
from dashboard import f_oauth

from dashboard.blueprints.fedex_api.payloads import (One_Rate_Shipment, Minimal_Sample_Domestic)
from dashboard.blueprints.fedex_api.utils import shipment_sample, validate_shipment_sample
from dashboard.blueprints.fedex_api.forms import CreateShipmentForm
from dashboard.main import get_lead
from dashboard.blueprints.fedex_api.api_codes.map import get_country_code


# TODO move to config
api_key = 'l7c2dd7f9a218543f0af1ea46c462e84cf'
secret_key = 'c39837dece64405cb2309d8eb6a8f8ca'
grant_type="client_credentials"
token_endpoint = 'https://apis-sandbox.fedex.com/oauth/token'
token_endpoint_auth_method='client_secret_post'
# === END config

fedex = Blueprint('fedex', __name__, template_folder='templates',
                  static_url_path='', static_folder='static')


# api_client = oauth.create_client('fedex')
api_client = f_oauth.register(
            'fedex',
            client_id=api_key,
            client_secret=secret_key,
            grant_type=grant_type,
            token_endpoint=token_endpoint,
            token_endpoint_auth_method=token_endpoint_auth_method
        )


def obtain_fedex_oauth2_token(): 
    fedex_token = session.get('fedex_token')
    expires_at = session.get('fedex_token_expires_at')

    if not expires_at or not fedex_token:
        return None
    need_to_refresh =  datetime.now() > datetime.fromtimestamp(int(expires_at))
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

    input_data = One_Rate_Shipment
    response = shipment_sample(input_data, token)
    print(response)
    return {'response': 'create'}


@fedex.route('/validate', methods=["GET"])
@fedex_token_required
def validate_shipment():
    import json
    token = session.get('fedex_token')

    inp_d = json.loads(Minimal_Sample_Domestic)
    inp_j = json.dumps(inp_d)
    input_data = Minimal_Sample_Domestic
    response = validate_shipment_sample(input_data, token)
    print(response)
    return {'response': 'validate'}


@fedex.route('/shipment/create/', methods=['GET', 'POST'])
@fedex.route('/shipment/create/<string:lead_id>', methods=['GET', 'POST'])
def create_shipment(lead_id='188602483043329'):
    form = CreateShipmentForm(request.form)

    if request.method == 'POST' and form.validate():
        form_data = form
        flash('Shipment created(NOTE: form valid but not sent)', 'success')

    elif request.method == "GET":        
        lead  = get_lead(lead_id)
        lead_data = json.loads(lead.data)
        form.recipients_personName.data = lead_data.get('name')
        form.recipients_phoneNumber.data = lead_data.get('phonenumber')
        form.recipients_address_line_1.data = lead_data.get('address').get('rawAddress')
        form.recipients_city.data = lead_data.get('address').get('city')
        form.recipients_stateOrProvinceCode.data = lead_data.get('address').get('rawAddress')
        form.recipients_postalCode.data = lead_data.get('address').get('postal_code')
        country = lead_data.get('address').get('country')
        form.recipients_countryCode.data = get_country_code(country)
        form.recipients_emailAddress.data = lead_data.get('email')
        # package details
        form.commodities_description.data = lead_data.get('description')
        form.commodities_quantity.data = lead_data.get('total')
        form.commodities_unit_price_amount.data = lead_data.get('price')
        form.commodities_unit_currency.data = lead_data.get('currency').upper()
        # form.commodities_unit_weight.data = lead_data.get()
        # form.commodities_weight_units.data = lead_data.get('units')


    return render_template('fedex_api/create_shipment.html', form=form)




