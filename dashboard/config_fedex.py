"""Contain FedEx details"""

import os
import logging

logger = logging.getLogger("flask.app")

# use 'dev' for testing
FEDEX_ENV = os.environ.get("FEDEX_ENV", 'dev')
logger.info(f"Using environment {FEDEX_ENV}")

company_info = {
    # shipper
    # contact
    'personName': 'Tom',
    'phoneNumber': '+61738234652',
    'companyName': 'Pangea Maps',

    # address
    'streetLines': ['6/46 Smith St, Capalaba QLD 4157'],
    'city': 'Capalaba',
    'stateOrProvinceCode': 'QU',
    'postalCode': '4157',
    'countryCode': 'AU',

    'accountNumber': os.environ.get("ACCOUNT", '510088000')
}

logger.info(f"Using account {company_info['accountNumber']}")


class ApiConf:
    # === API credentials
    api_key = os.environ.get("API_KEY", 'l7c2dd7f9a218543f0af1ea46c462e84cf')
    secret_key = os.environ.get("SECRET_KEY", 'c39837dece64405cb2309d8eb6a8f8ca')
    logger.info(f"Using api_key ending:{api_key[-6:]}")
    logger.info(f"Using secret_key ending:{secret_key[-6:]}")

    # === do not change grant_type and token_endpoint_auth_method
    grant_type = "client_credentials"
    token_endpoint_auth_method = 'client_secret_post'
    # token_endpoint = 'https://apis-sandbox.fedex.com/oauth/token'


"""
    Fedex express

    Packaging Type
    We have 3 different packages sizes.
    48cm x 48cm x 9cm x 4kg
    65cm x 65cm x 9cm x 6kg
    90cm x 90cm x 9cm x 10kg

    Shipper Information.
    Pangea Maps
    2/51 Ross st
    Newstead, 4006
    Qld Australia

    Shipping payment
    Sender
"""
