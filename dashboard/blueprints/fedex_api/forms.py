from wtforms import (Form, BooleanField, StringField,
                     PasswordField, validators, IntegerField, FloatField)


# One_Rate_Shipment
class CreateShipmentForm(Form):
    # shipper
    recipients_personName = StringField(
        'Recipients name',
        [validators.Length(min=4, max=50), validators.DataRequired()],
        default='auto-replace'
    )
    recipients_phoneNumber = StringField(
        'Phone Number',
        [validators.Length(min=8, max=15)],
        default='auto-replace'
    )
    recipients_companyName = StringField(
        'Company Name (Optional)',
        default=''
    )
    recipients_address_line_1 = StringField(
        'Street Line 1',
        [validators.Length(min=4, max=35), validators.DataRequired()],
        default='auto-replace'
    )
    recipients_address_line_2 = StringField(
        'Street Line 2 (Optional)',
        [validators.Length(min=0, max=35)],
         default=''
         )
    recipients_city = StringField(
        'City',
        [validators.Length(min=4, max=50), validators.DataRequired()],
        default='auto-replace'
    )
    recipients_stateOrProvinceCode = StringField(
        'State Or ProvinceCode',
        [validators.Length(min=0, max=50), validators.DataRequired()],
        default='auto-replace'
    )
    recipients_postalCode = StringField(
        'Postal Code',
        [validators.Length(min=0, max=10)],
        default='auto-replace'
    )
    recipients_countryCode = StringField(
        'Country Code',
        [validators.Length(min=2, max=2), validators.DataRequired()],
        default='auto-replace'
    )
    recipients_emailAddress = StringField('Email Address', [validators.Length(min=6, max=35)])

    # ============ Package details
    commodities_description = StringField('Commodity description', [validators.Length(min=4, max=450)])
    commodities_quantity = IntegerField('Commodity quantity')
    commodities_unit_price_amount = StringField('Unit Price', [validators.Length(min=1, max=8)])
    commodities_unit_currency = StringField('Currency', [validators.Length(min=2, max=3)])
    commodities_unit_weight = FloatField('Weight', [validators.InputRequired()])
    commodities_weight_units = StringField(
        'Weight Units', 
        [validators.Length(min=2, max=3)],
        default='KG'
        )
    # ============ END Package details

    # ============ purpose
    """ All time
        "purpose": "GIFT",
    """
    # ============ END purpose

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
