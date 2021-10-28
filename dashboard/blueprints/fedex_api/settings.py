from dashboard.config_fedex import FEDEX_ENV

class Endpoints: 
    """ Contains endpoints for `dev` and `production`
        Change `FEDEX_ENV` variable to change url type
    """   
    # development endpoints
    sandbox = {
        'create_shipment': 'https://apis-sandbox.fedex.com/ship/v1/shipments',
        'token_endpoint' : 'https://apis-sandbox.fedex.com/oauth/token'
    }
    # production endpoints
    production = {
        'create_shipment': 'https://apis.fedex.com/ship/v1/shipments',
        'token_endpoint' : 'https://apis.fedex.com/oauth/token'
    }

    urls = {}

    def __init__(self) -> None:
        if FEDEX_ENV == 'dev':
            self.urls = self.sandbox
        elif FEDEX_ENV == 'production':
            self.urls = self.production

