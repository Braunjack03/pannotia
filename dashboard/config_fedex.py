"""Contain FedEx details
"""

# use 'dev' for testing 
FEDEX_ENV = 'dev'  # FEDEX_ENV = 'production'

company_info ={
    # shipper 
        # contact
    'personName' : 'Pangea',        # TODO replace
    'phoneNumber' : '1234567890',   # TODO replace
    'companyName' : 'Pangea Maps',

        # address
    'streetLines' : ['2/51 Ross st Newstead, 4006 Qld'],
    'city' : 'Brisbane',
    'stateOrProvinceCode' : 'AU',
    'postalCode' : '4006',
    'countryCode' : 'AU',

    'accountNumber': "510088000"

}

class ApiConf:
    # === API credentials
    api_key = 'l7c2dd7f9a218543f0af1ea46c462e84cf'
    secret_key = 'c39837dece64405cb2309d8eb6a8f8ca'

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