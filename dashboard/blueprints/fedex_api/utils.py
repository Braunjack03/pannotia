import os
import json
import re
import requests
from dashboard.config_fedex import company_info
from dashboard.blueprints.fedex_api.payloads import (create_shipment_json, validate_shipment_json)
from dashboard.blueprints.fedex_api.settings import Endpoints


def shipment_sample(input_data, token):
    url = "https://apis-sandbox.fedex.com/ship/v1/shipments"

    payload = input_data # 'input' refers to JSON Payload
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
        }
    response = requests.request("POST", url, data=payload, headers=headers)

    return response


def validate_shipment_sample(input_data, token):
    url = "https://apis-sandbox.fedex.com/ship/v1/shipments/packages/validate"
    

    # payload = input # 'input' refers to JSON Payload
    payload = input_data # 'input' refers to JSON Payload
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

    return response

def send(url, payload_json, token):

    payload = payload_json # 'input' refers to JSON Payload
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
        }
    response = requests.request("POST", url, data=payload, headers=headers)

    return response


def send_request(form_data, token, request_type='create_shipment'):
    

    payload_json = _replace_data(form_data, request_type)
    if payload_json:
        endpoints = Endpoints().urls 
        url = endpoints.get('create_shipment')
        response  = send(url, payload_json, token)
        return response
    
    return False
    

def _replace_data(form_data, request_type):
    """Replace default payload with data from form

    Args:
        form_data (dict): data from user form
        request_type (string): Request type - endpoints name/type
    """
    if  request_type=='create_shipment':
        payload = create_shipment_json.get('International_Shipment')

        # p_d = json.loads(payload)
        p_d = _set_comany_info_from_config(json.loads(payload))
        
        p_d['requestedShipment']['recipients'][0]['contact']['personName'] = form_data.recipients_personName.data
        p_d['requestedShipment']['recipients'][0]['contact']['phoneNumber'] = form_data.recipients_phoneNumber.data
        p_d['requestedShipment']['recipients'][0]['address']['streetLines'] = [form_data.recipients_address_line_1.data]
        p_d['requestedShipment']['recipients'][0]['address']['city'] = form_data.recipients_city.data
        p_d['requestedShipment']['recipients'][0]['address']['stateOrProvinceCode'] = form_data.recipients_stateOrProvinceCode.data
        p_d['requestedShipment']['recipients'][0]['address']['postalCode'] = form_data.recipients_postalCode.data
        p_d['requestedShipment']['recipients'][0]['address']['countryCode'] = form_data.recipients_countryCode.data
        # p_d['requestedShipment']['recipients']['personName'] = form_data.recipients_emailAddress.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['description'] = form_data.commodities_description.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['quantity'] = form_data.commodities_quantity.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['unitPrice']['amount'] = form_data.commodities_unit_price_amount.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['unitPrice']['currency'] = form_data.commodities_unit_currency.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['customsValue']['amount'] = form_data.commodities_unit_price_amount.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['customsValue']['currency'] = form_data.commodities_unit_currency.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['weight']['value'] = form_data.commodities_unit_weight.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['weight']['units'] = form_data.commodities_weight_units.data

        p_d['requestedShipment']['requestedPackageLineItems'][0]['weight']['value'] = form_data.commodities_unit_weight.data
        p_d['requestedShipment']['requestedPackageLineItems'][0]['weight']['units'] = form_data.commodities_weight_units.data

        # if shipper and recipient have the same country code -> FEDEX_EXPRESS_SAVER
        shipper_country = p_d['requestedShipment']['shipper']['address']['countryCode']
        recipient = form_data.recipients_countryCode.data
        if shipper_country == recipient:
            p_d['requestedShipment']['serviceType'] = 'STANDARD_OVERNIGHT'

        payload_json = json.dumps(p_d)
        return payload_json
    
    # if endpoint type not implemented return false
    return False


def _set_comany_info_from_config(data):
    """Replace default payload with company data

    Args:
        payload (dict): updated dictionary with company data
    """
    data['accountNumber']['value'] = company_info['accountNumber']

    data['requestedShipment']['shipper']['contact']['personName'] = company_info['personName']
    data['requestedShipment']['shipper']['contact']['phoneNumber'] = company_info['phoneNumber']
    data['requestedShipment']['shipper']['contact']['companyName'] = company_info['companyName']

    data['requestedShipment']['shipper']['address']['streetLines'] = company_info['streetLines']
    data['requestedShipment']['shipper']['address']['city'] = company_info['city']
    data['requestedShipment']['shipper']['address']['stateOrProvinceCode'] = company_info['stateOrProvinceCode']
    data['requestedShipment']['shipper']['address']['postalCode'] = company_info['postalCode']
    data['requestedShipment']['shipper']['address']['countryCode'] = company_info['countryCode']
    return data




def save_response(d):
    cwd = os.getcwd()
    relative_path = 'dashboard\\blueprints\\fedex_api\\log\\created_shipment.json'
    file_path = os.path.join(os.getcwd(),relative_path )

    contenet = json.loads(d.content)
    
    if os.path.exists(file_path):
        mode = "r+"
    else:
        mode = "w"

    with open(file_path, mode, encoding='utf-8') as f:
        if mode == 'w':
            data = {}
            data['resp'] = []
        else:
            data = json.load(f)

    
        # remove image from response to save space in json log file
        contenet['output']['transactionShipments'][0]['completedShipmentDetail']['shipmentDocuments'][0]['parts']=[]
        data['resp'].append(contenet)
        f.seek(0)
        # json.dump(data, file)    
        json.dump(data, f, ensure_ascii=False, indent=2)
