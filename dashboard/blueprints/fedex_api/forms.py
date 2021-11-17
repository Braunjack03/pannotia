from wtforms import (Form, BooleanField, StringField,
                     PasswordField, validators, IntegerField, FloatField, SelectField)
from dashboard.blueprints.fedex_api.api_codes.choices import FedExChoices as choices


# One_Rate_Shipment
class CreateShipmentForm(Form):
    # payload['requestedShipment']['recipients']
    recipients_personName = StringField('Recipients name',[validators.Length(min=4, max=50), validators.DataRequired()],default='auto-replace')
    recipients_phoneNumber = StringField('Phone Number',[validators.Length(min=8, max=15)],default='auto-replace' )
    recipients_companyName = StringField('Company Name (Optional)', default='')
    recipients_address_line_1 = StringField('Street Line 1', [validators.Length(min=4, max=35), validators.DataRequired()], default='auto-replace')
    recipients_address_line_2 = StringField('Street Line 2 (Optional)', [validators.Length(min=0, max=35)], default='' )
    recipients_city = StringField( 'City', [validators.Length(min=4, max=50), validators.DataRequired()], default='auto-replace' )
    recipients_stateOrProvinceCode = StringField( 'State Or ProvinceCode', [validators.Length(min=0, max=20)], default='auto-replace' )
    recipients_postalCode = StringField( 'Postal Code', [validators.Length(min=0, max=10)], default='auto-replace' )
    recipients_countryCode = StringField( 'Country Code', [validators.Length(min=2, max=2), validators.DataRequired()], default='auto-replace' )
    recipients_emailAddress = StringField('Email Address', [validators.Length(min=6, max=35)])

    # ============ Package details
    # payload['requestedShipment']['customsClearanceDetail']['commodities']
    commodities_description = StringField('Commodity description', [validators.Length(min=4, max=450)], default='Bespoke Map Art - Original Engravings, Framed')
    commodities_harmonizedCode = StringField('Harmonized Code', [validators.Length(min=0, max=10)], default='970200')
    commodities_countryOfManufacture = StringField('Country Of Manufacture', [validators.Length(min=0, max=3)], default='AU')
    commodities_quantity = IntegerField('Quantity', default=1)
    commodities_unit_price_amount = StringField('Unit Price', [validators.Length(min=1, max=8)])
    commodities_unit_currency = StringField('Currency', [validators.Length(min=2, max=3)])
    commodities_unit_weight = FloatField('Weight', [validators.InputRequired()])
    commodities_weight_units = StringField('Weight Units', [validators.Length(min=2, max=3)], default='KG')
    commodities_size_length = FloatField('Length', [validators.InputRequired()])
    commodities_size_width = FloatField('Width', [validators.InputRequired()])
    commodities_size_height = FloatField('Height', [validators.InputRequired()])
    commodities_size_units = StringField('Size Units', [validators.Length(min=2, max=3)], default='CM')

    # TODO shippingDocumentTypes

    # payload['requestedShipment']['serviceType']
    r_shipment_service_type = SelectField('Service Type', choices=choices.service_type, default='INTERNATIONAL_PRIORITY')

    # payload['requestedShipment']['packagingType']
    r_shipment_packaging_type = SelectField('Packaging Type', choices=choices.packaging_choices, default='YOUR_PACKAGING')

    # payload['requestedShipment']['pickupType']
    r_shipment_pickup_type = SelectField('Pickup Type', choices=choices.pickup_type, default='USE_SCHEDULED_PICKUP')

    # payload['requestedShipment']['customsClearanceDetail']['commercialInvoice']['shipmentPurpose']
    r_shipment_purpose = SelectField('Shipment Purpose', choices=choices.sh_purpose_choices, default='')
    # ============ END Package details

    # ============ Billing
    # payload['requestedShipment']['shippingChargesPayment']['paymentType']
    r_shipment_shippingChargesPayment = SelectField('Transportation coast', choices=choices.paymentType,
                                                    default='SENDER')
    # payload['requestedShipment']['customsClearanceDetail']['dutiesPayment']['paymentType']
    r_shipment_dutiesPayment = SelectField('Duties, taxes and fees', choices=choices.paymentType, default='RECIPIENT')
    # payload['requestedShipment']['recipients'][0]['tins'][0]['number']
    r_shipment_recipient_tins = StringField('Recipient Tax ID (optional)', [validators.Length(min=0, max=18)])
    # payload['requestedShipment']['shipper']['tins'][0]['number']
    r_shipment_shipper_tins = StringField('Sender Tax ID (optional)', [validators.Length(min=0, max=18)])
    # ============ END Billing

    validate_address = BooleanField('Validate Address', default=False)
    # blockInsightVisibility = BooleanField(
    #     'Block Insight Visibility',
    #     # [validators.DataRequired()],
    #     # default=True
    # )


# TODO remove RegistrationForm, this is only for testing
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
