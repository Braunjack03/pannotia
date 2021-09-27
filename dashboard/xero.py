# -*- coding: utf-8 -*-
import os
import datetime
from decimal import Decimal
import datetime as dt
from dateutil import parser
from functools import wraps
from io import BytesIO
from logging.config import dictConfig

from flask import Blueprint, render_template, redirect, url_for, session, json, send_file, current_app, request
from flask_login import current_user
from flask_oauthlib.contrib.client import OAuth, OAuth2Application
from xero_python.accounting import AccountingApi, Contact, Invoice, Invoices, CurrencyCode, LineItem, LineAmountTypes
from xero_python.api_client import ApiClient, serialize
from xero_python.api_client.configuration import Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.exceptions import AccountingBadRequestException
from xero_python.identity import IdentityApi
from xero_python.utils import getvalue

from .logging_settings import default_settings
from .utils import jsonify, serialize_model

from .models import Dynamo

currency_list = ["aud", "cad", "gbp", "eur", "usd", "nzd"]

line_item_codes = {
    "au": "1",
    "us": "2",
    "aud": ["QQ", "AA", "ZZ"],
    "usd": ["WW", "SS", "XX"],
    "cad": ["EE", "DD", "CC"]
}

dictConfig(default_settings)

# configure main flask application
xero_app = Blueprint("xero", __name__, template_folder="templates", static_url_path="", static_folder="static")

# configure flask-oauthlib application
# TODO fetch config from https://identity.xero.com/.well-known/openid-configuration #1
oauth = OAuth(xero_app)
xero = oauth.remote_app(
    name="xero",
    version="2",
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    endpoint_url="https://api.xero.com/",
    authorization_url="https://login.xero.com/identity/connect/authorize",
    access_token_url="https://identity.xero.com/connect/token",
    refresh_token_url="https://identity.xero.com/connect/token",
    scope="offline_access openid profile email accounting.transactions "
          "accounting.transactions.read accounting.reports.read "
          "accounting.journals.read accounting.settings accounting.settings.read "
          "accounting.contacts accounting.contacts.read accounting.attachments "
          "accounting.attachments.read assets projects",
)  # type: OAuth2Application

# configure xero-python sdk client
api_client = ApiClient(
    Configuration(
        debug=int(os.environ["DEBUG"]),
        oauth2_token=OAuth2Token(
            client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"]
        ),
    ),
    pool_threads=1,
)


def get_codes(lead, currency):
    country_code = lead["status"].get("countryCode", "").lower()
    shipping_code = line_item_codes.get(country_code, 2)
    size = int(lead["status"].get('size', 1))
    map_code = line_item_codes.get(currency, line_item_codes["usd"])[size]
    return shipping_code, map_code


# configure token persistence and exchange point between flask-oauthlib and xero-python
@xero.tokengetter
@api_client.oauth2_token_getter
def obtain_xero_oauth2_token():
    return session.get("token")


@xero.tokensaver
@api_client.oauth2_token_saver
def store_xero_oauth2_token(token):
    session["token"] = token
    session.modified = True


def xero_token_required(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        xero_token = obtain_xero_oauth2_token()
        if not xero_token:
            return redirect(url_for("xero.login", _external=True))

        return function(*args, **kwargs)

    return decorator


@xero_app.route("/tenants")
@xero_token_required
def tenants():
    identity_api = IdentityApi(api_client)
    accounting_api = AccountingApi(api_client)

    available_tenants = []
    for connection in identity_api.get_connections():
        tenant = serialize(connection)
        if connection.tenant_type == "ORGANISATION":
            organisations = accounting_api.get_organisations(
                xero_tenant_id=connection.tenant_id
            )
            tenant["organisations"] = serialize(organisations)

        available_tenants.append(tenant)

    return render_template(
        "code.html",
        title="Xero Tenants",
        code=json.dumps(available_tenants, sort_keys=True, indent=4),
    )


@xero_app.route("/create_invoice/<lead_id>", methods=["PUT"])
@xero_token_required
def create_invoice(lead_id):
    current_app.logger.info(f"User {current_user.email} made:")
    current_app.logger.info(request)

    args = request.get_json(force=True)
    for key_1 in args:
        if key_1 == "items":
            for item in args[key_1]:
                to_del = []
                for key_2 in item:
                    if item[key_2] == "None":
                        to_del.append(key_2)
                for key_2 in to_del:
                    del item[key_2]
            continue
        to_del = []
        for key_2 in args[key_1]:
            if args[key_1][key_2] == "None":
                to_del.append(key_2)
        for key_2 in to_del:
            del args[key_1][key_2]
    lead_db = Dynamo(f"{current_app.config['USER']}Lead", "lead")
    lead = lead_db.get(int(lead_id))

    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)

    args["customer"]["addresses"] = []
    contact = Contact(
        **args["customer"]
    )
    # contact_number=None,
    # account_number=None,
    # name='John Smith',
    # first_name=None,
    # last_name=None,
    # email_address=None,
    # addresses=[]

    line_items = [LineItem(**x) for x in args["items"]]
    #     [
    #     {'description': 'Map of blah', 'quantity': Decimal('1.0000'), 'unit_amount': Decimal('350.00'),
    #      'item_code': None, 'account_code': '200', 'tax_type': 'OUTPUT', 'discount_rate': None},
    #     {'description': 'Shipping to blah', 'quantity': Decimal('1.0000'), 'unit_amount': Decimal('55.00'),
    #      'item_code': None, 'account_code': '200', 'tax_type': 'OUTPUT', 'discount_rate': None},
    # ]

    args["data"]["contact"] = contact
    args["data"]["line_items"] = line_items
    args["data"]["date"] = datetime.date.today()
    args["data"]["due_date"] = parser.parse(args["data"]["due_date"]).date()
    currency = args["data"]["currency_code"]
    args["data"]["currency_code"] = CurrencyCode[currency.upper()]
    args["data"]["type"] = "ACCREC"
    args["data"]["line_amount_types"] = LineAmountTypes["INCLUSIVE"]

    inv = Invoice(
        **args["data"]
    )
    # amount_credited=None,
    # amount_due=None,
    # amount_paid=None,
    # attachments=None,
    # branding_theme_id=d10b7a46-2fb8-49e7-89d1-2e04b7d6d8d1,
    # cis_deduction=None,
    # contact=contact,
    # credit_notes=None,
    # currency_code=CurrencyCode.AUD,
    # currency_rate=None,
    # expected_payment_date=None,
    # fully_paid_on_date=None,
    # has_attachments=False,
    # has_errors=False,
    # invoice_id=None,
    # invoice_number=None,
    # is_discounted=None,
    # line_amount_types=None,
    # line_items=line_items,
    # overpayments=None,
    # payments=None,
    # planned_payment_date=None,
    # prepayments=None,
    # reference=None,
    # repeating_invoice_id=None,
    # sent_to_contact=None,
    # status='AUTHORISED',
    # status_attribute_string=None,
    # sub_total=None,
    # total=None,
    # total_discount=None,
    # total_tax=None,
    # type='ACCREC',
    # updated_date_utc=None,
    # url=None,
    # validation_errors=None,
    # warnings=None

    invoices = Invoices([inv])

    # accounting_api.email_invoice()

    try:
        created_invoices = accounting_api.create_invoices(xero_tenant_id, invoices=invoices)  # type: Invoices
        if inv.status == 'AUTHORISED':
            email_response = accounting_api.email_invoice(xero_tenant_id,
                                                          invoice_id=created_invoices.invoices[0].invoice_id,
                                                          request_empty={})
            try:
                current_app.logger.info(email_response)
            except Exception as e:
                current_app.logger.error("email response stuffed up")
                current_app.logger.error(e)
    except AccountingBadRequestException as exception:
        current_app.logger.error(exception)
        sub_title = "Error: " + exception.reason
        code = jsonify(exception.error_data)
    else:
        sub_title = f"Invoice {getvalue(created_invoices, 'contacts.0.name', '')} created."
        code = serialize_model(created_invoices)
        try:
            lead["status"]["price"] = float(created_invoices.invoices[0].total)
            lead["status"]["currency"] = currency.lower()
            lead["invoice"] = int(created_invoices.invoices[0].invoice_number.split('-')[1])
            args["datetime"]: str(dt.datetime.now())
            lead["updates"].append(lead["status"])
            lead["checkout"] = lead.get("checkout", [])
            lead_db.add(int(lead_id), lead)
        except Exception as e:
            current_app.logger.error(e)
            sub_title = f"ERROR UPDATING LEAD DB. Invoice {getvalue(created_invoices, 'contacts.0.name', '')} created. Error: {e}"
    return render_template(
        "invoice.html",
        code=code,
        title="Invoice Status",
        sub_title=sub_title
    )


@xero_app.route("/invoices")
@xero_token_required
def get_invoices():
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)

    invoices = accounting_api.get_invoices(
        xero_tenant_id, statuses=["DRAFT", "SUBMITTED", "AUTHORISED"]
    )
    code = serialize_model(invoices)

    sub_title = "Total invoices found: {}".format(len(invoices.invoices))

    return render_template(
        "code.html", title="Invoices", code=code, sub_title=sub_title
    )


@xero_app.route("/login")
def login():
    redirect_url = url_for("xero.oauth_callback", _external=True)
    response = xero.authorize(callback_uri=redirect_url)
    return response


@xero_app.route("/callback")
def oauth_callback():
    try:
        response = xero.authorized_response()
    except Exception as e:
        print(e)
        raise
    # todo validate state value
    if response is None or response.get("access_token") is None:
        return "Access denied: response=%s" % response
    store_xero_oauth2_token(response)
    return redirect(url_for("xero.index", _external=True))


@xero_app.route("/logout")
def logout():
    store_xero_oauth2_token(None)
    return redirect(url_for("xero.index", _external=True))


@xero_app.route("/export-token")
@xero_token_required
def export_token():
    token = obtain_xero_oauth2_token()
    buffer = BytesIO("token={!r}".format(token).encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="x.python",
        as_attachment=True,
        attachment_filename="oauth2_token.py",
    )


@xero_app.route("/refresh-token")
@xero_token_required
def refresh_token():
    xero_token = obtain_xero_oauth2_token()
    new_token = api_client.refresh_oauth2_token()
    return render_template(
        "code.html",
        title="Xero OAuth2 token",
        code=jsonify({"Old Token": xero_token, "New token": new_token}),
        sub_title="token refreshed",
    )


def get_xero_tenant_id():
    token = obtain_xero_oauth2_token()
    if not token:
        return None

    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_type == "ORGANISATION":
            return connection.tenant_id


@xero_app.route("/", methods=["GET"])
@xero_token_required
def index():
    args = request.args
    lead_id = None
    if args.get("lead"):
        lead_id = int(args.get("lead"))
        lead = lead_db.get(lead_id)
    else:
        lead = {"status": {}}
    line_items = []
    currency = lead["status"].get("currency", "usd")
    if type(currency) == int:
        currency = currency_list[currency]
    currency = currency.lower()
    shipping_code, map_code = get_codes(lead, currency)
    country = lead["status"].get("country", "United States of America")
    address = lead["status"].get("address", {'country': country})
    address = [address.get('line1'), address.get('city'), address.get('state'), address.get('country'),
               address.get('postal_code')]
    address = ', '.join([x for x in address if x])

    return render_template(
        "invoice.html",
        lead_id=lead_id,
        name=lead["status"].get("firstName", "Enter Name"),
        email_address=lead["status"].get("email", "Enter Email"),
        currency_code=currency,
        currency_codes=currency_list,
        line_items=line_items,
        map_name=lead["status"].get("mapName"),
        reference=lead["status"].get("firstName", "Enter Name"),
        branding_theme_id={"standard": "25fe1b8b-7a63-4aef-b79f-0693bb0f1094",
                           "pangea": "d10b7a46-2fb8-49e7-89d1-2e04b7d6d8d1"},
        status=["DRAFT", "AUTHORISED"],
        today=dt.date.today().strftime("%Y-%m-%d"),
        map_code=map_code,
        shipping_code=shipping_code,
        address=address,
    )
