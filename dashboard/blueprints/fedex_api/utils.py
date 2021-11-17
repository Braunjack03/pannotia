import json
import requests
from dashboard.config_fedex import FEDEX_ENV
from dashboard.config_fedex import company_info
from dashboard.blueprints.fedex_api.payloads import (create_shipment_json, validate_address_json)
from dashboard.blueprints.fedex_api.api_codes import mapper

from dashboard.models import Dynamo

lead_db = Dynamo('Lead', 'lead')


class Endpoints:
    """ Contains endpoints for `dev` and `production`
        Change `FEDEX_ENV` variable to change url type
    """
    # development endpoints
    sandbox = {
        'validate_address': 'https://apis-sandbox.fedex.com/address/v1/addresses/resolve',
        'create_shipment': 'https://apis-sandbox.fedex.com/ship/v1/shipments',
        'token_endpoint': 'https://apis-sandbox.fedex.com/oauth/token'
    }
    # production endpoints
    production = {
        'validate_address': 'https://apis.fedex.com/address/v1/addresses/resolve',
        'create_shipment': 'https://apis.fedex.com/ship/v1/shipments',
        'token_endpoint': 'https://apis.fedex.com/oauth/token'
    }

    urls = {}

    def __init__(self) -> None:
        if FEDEX_ENV == 'dev':
            self.urls = self.sandbox
        elif FEDEX_ENV == 'production':
            self.urls = self.production


def send(url, payload_json, token):
    payload = payload_json  # 'input' refers to JSON Payload
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
        url = endpoints.get(request_type)
        response = send(url, payload_json, token)
        return response

    return False


def _replace_data(form_data, request_type):
    """Replace default payload with data from form

    Args:
        form_data (dict): data from user form
        request_type (string): Request type - endpoints name/type
    """
    if request_type == 'validate_address':
        payload = validate_address_json
        payload['addressesToValidate'][0]['address']['streetLines'] = [form_data.recipients_address_line_1.data]
        payload['addressesToValidate'][0]['address']['city'] = form_data.recipients_city.data
        payload['addressesToValidate'][0]['address'][
            'stateOrProvinceCode'] = form_data.recipients_stateOrProvinceCode.data
        payload['addressesToValidate'][0]['address']['postalCode'] = form_data.recipients_postalCode.data
        payload['addressesToValidate'][0]['address']['countryCode'] = form_data.recipients_countryCode.data

        payload_json = json.dumps(payload)
    elif request_type == 'create_shipment':
        # payload = create_shipment_json.get('International_Shipment')
        payload = create_shipment_json.get('Custom_Shipment')

        # p_d = json.loads(payload)
        p_d = _set_comany_info_from_config(json.loads(payload))

        p_d['requestedShipment']['recipients'][0]['contact']['personName'] = form_data.recipients_personName.data
        p_d['requestedShipment']['recipients'][0]['contact']['phoneNumber'] = form_data.recipients_phoneNumber.data
        p_d['requestedShipment']['recipients'][0]['address']['streetLines'] = [form_data.recipients_address_line_1.data]
        p_d['requestedShipment']['recipients'][0]['address']['city'] = form_data.recipients_city.data
        p_d['requestedShipment']['recipients'][0]['address'][
            'stateOrProvinceCode'] = form_data.recipients_stateOrProvinceCode.data
        p_d['requestedShipment']['recipients'][0]['address']['postalCode'] = form_data.recipients_postalCode.data
        p_d['requestedShipment']['recipients'][0]['address']['countryCode'] = form_data.recipients_countryCode.data

        # Shipment details
        # p_d['requestedShipment']['recipients']['personName'] = form_data.recipients_emailAddress.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0][
            'description'] = form_data.commodities_description.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0][
            'harmonizedCode'] = form_data.commodities_harmonizedCode.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0][
            'countryOfManufacture'] = form_data.commodities_countryOfManufacture.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0][
            'quantity'] = form_data.commodities_quantity.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['unitPrice'][
            'amount'] = form_data.commodities_unit_price_amount.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['unitPrice'][
            'currency'] = form_data.commodities_unit_currency.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['customsValue'][
            'amount'] = form_data.commodities_unit_price_amount.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['customsValue'][
            'currency'] = form_data.commodities_unit_currency.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['weight'][
            'value'] = form_data.commodities_unit_weight.data
        p_d['requestedShipment']['customsClearanceDetail']['commodities'][0]['weight'][
            'units'] = form_data.commodities_weight_units.data

        p_d['requestedShipment']['serviceType'] = form_data.r_shipment_service_type.data
        p_d['requestedShipment']['packagingType'] = form_data.r_shipment_packaging_type.data
        p_d['requestedShipment']['pickupType'] = form_data.r_shipment_pickup_type.data
        if form_data.r_shipment_purpose.data:
            p_d['requestedShipment']['customsClearanceDetail']['commercialInvoice'][
                'shipmentPurpose'] = form_data.r_shipment_purpose.data
        else:
            del p_d['requestedShipment']['customsClearanceDetail']['commercialInvoice']['shipmentPurpose']

        p_d['requestedShipment']['requestedPackageLineItems'][0]['weight'][
            'value'] = form_data.commodities_unit_weight.data
        p_d['requestedShipment']['requestedPackageLineItems'][0]['weight'][
            'units'] = form_data.commodities_weight_units.data
        p_d['requestedShipment']['requestedPackageLineItems'][0]['dimensions'][
            'length'] = form_data.commodities_size_length.data
        p_d['requestedShipment']['requestedPackageLineItems'][0]['dimensions'][
            'width'] = form_data.commodities_size_width.data
        p_d['requestedShipment']['requestedPackageLineItems'][0]['dimensions'][
            'height'] = form_data.commodities_size_height.data
        p_d['requestedShipment']['requestedPackageLineItems'][0]['dimensions'][
            'units'] = form_data.commodities_size_units.data

        # billing
        p_d['requestedShipment']['shippingChargesPayment'][
            'paymentType'] = form_data.r_shipment_shippingChargesPayment.data
        p_d['requestedShipment']['customsClearanceDetail']['dutiesPayment'][
            'paymentType'] = form_data.r_shipment_dutiesPayment.data
        p_d['requestedShipment']['recipients'][0]['tins'][0]['number'] = form_data.r_shipment_recipient_tins.data
        p_d['requestedShipment']['shipper']['tins'][0]['number'] = form_data.r_shipment_shipper_tins.data

        # TODO test form_data.r_shipment_service_type.data and delete below
        # if shipper and recipient have the same country code -> FEDEX_EXPRESS_SAVER
        # shipper_country = p_d['requestedShipment']['shipper']['address']['countryCode']
        # recipient = form_data.recipients_countryCode.data
        # if shipper_country == recipient:
        #     p_d['requestedShipment']['serviceType'] = 'STANDARD_OVERNIGHT'

        payload_json = json.dumps(p_d)
        return payload_json
    else:
        assert False, f'request type {request_type} not implemented'

    return payload_json


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


def save_response(data, lead_id, request_type):
    if request_type == 'create_shipment':
        lead = lead_db.get(int(lead_id))
        for transaction in data['output']['transactionShipments']:
            for document in transaction.get('shipmentDocuments', []):
                if document['contentType'] == 'MERGED_LABEL_DOCUMENTS':
                    lead['shipping'] = document['url']
                    lead['tracking'] = document['trackingNumber']
                    break
        lead_db.update_table_item(int(lead_id), lead)
    else:
        print(data)


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
        self.country = address.get('country', 'US')
        self.country_code = None

    def get_address_line_1(self):
        if self.address_line_1 == "":
            if self.raw_address != "":
                self.address_line_1 = self.raw_address.split(',')[0]
        return self.address_line_1

    def get_country_code(self):
        if self.country == "":
            return None
        self.country_code = mapper.get_country_code(self.country)
        return self.country_code

    def _get_province_name(self):
        if self.state == "":
            parsed_raw_addr = self.raw_address.split(',')
            for i, item in enumerate(parsed_raw_addr):
                if i == 1 and mapper.has_code(self.country):
                    # get first word
                    province_name = item.strip().split(' ')[0]
                    return province_name
        return None

    def get_province_code(self):
        if self.state != "":
            return self.state
        province_name = self._get_province_name()
        if province_name:
            code = mapper.get_state_or_province_code(self.country, province_name)
            return code
        return None


def main():
    # testing
    # python -m dashboard.blueprints.fedex_api.utils

    print('=== testing utils ===')
    address = {
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


if __name__ == '__main__':
    main()
