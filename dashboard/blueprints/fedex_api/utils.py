import os
import json
import re
import requests
from dashboard.config_fedex import company_info
from dashboard.blueprints.fedex_api.payloads import (create_shipment_json, validate_shipment_json)
from dashboard.blueprints.fedex_api.settings import Endpoints
from dashboard.blueprints.fedex_api.api_codes import map


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


class AddressParser:
    """ Address Parser
        example of user data with address see: http://localhost:5000/lead/188602483043329
        where 188602483043329 -> user id

        parse address from string: 
        expected string:
        <street>,<province_or_state>,<country>

    """

    def __init__(self, address) -> None:
        self.raw_address = address.get('rawAddress')
        self.address_line_1 = address.get('line1')
        self.city = address.get('city')
        self.state = address.get('state')
        self.postal_code = address.get('postal_code')
        self.country = address.get('country')


    def get_address_line_1(self):
        if self.address_line_1 == "":
            if self.raw_address != "":
                self.address_line_1 = self.raw_address.split(',')[0]
        return self.address_line_1

    
    def get_country_code(self):
        if self.country == "":
            return None
        self.country_code = map.get_country_code(self.country)
        return self.country_code


    def _get_province_name(self):        
        if self.state == "":
            parsed_raw_addr = self.raw_address.split(',')
            for i, item in enumerate(parsed_raw_addr):
                if i == 1 and map.has_code(self.country):
                    # get first word 
                    province_name = item.strip().split(' ')[0]
                    return province_name               
        return None


    def get_province_code(self):
        if self.state != "":
            return self.state
        province_name = self._get_province_name()
        if province_name:
            code = map.get_state_or_province_code(self.country, province_name)
            return code



if __name__=='__main__':
    # testing
    # python -m dashboard.blueprints.fedex_api.utils

    print('=== testing utils ===')
    address =  {
        "rawAddress": "8 Danina Street, Mansfield QLD, Australia",
        "line1": "",
        "city": "Brisbane",
        "state": "",
        "postal_code": "",
        "country": "Australia"
    }
    # address =  {
    #     "rawAddress": "8 Danina Street, alabama QLD, United States",
    #     "line1": "",
    #     "city": "Brisbane",
    #     "state": "",
    #     "postal_code": "",
    #     "country": "United States"
    # }
    print('-- init parser --')
    parser = AddressParser(address)
    print('raw_address:', parser.raw_address)
    print('address_line_1:', parser.address_line_1)
    print('city:', parser.city)
    print('state:', parser.state)
    print('postal_code:', parser.postal_code)
    print('country:', parser.country)
    print('-- End init parser --')
    print()
    print(parser.get_address_line_1())
    print(parser.get_country_code())
    print(parser.get_province_code())

    pass    