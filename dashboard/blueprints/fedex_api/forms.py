from wtforms import Form, BooleanField, StringField, PasswordField, validators


# One_Rate_Shipment
class CreateShipmentForm(Form):
    # shipper
    shipper_personName = StringField(
        'SHIPPER NAME', 
        [validators.Length(min=4, max=25)],
        default='SHIPPER NAME'
        )
    shipper_phoneNumber = StringField(
        'phone Number', 
        [validators.Length(min=4, max=25)],
        default='1234567890'
        )
    shipper_companyName = StringField(
        'company Name', 
        [validators.Length(min=4, max=25)],
        default='Shipper Company Name'
        )
    
    blockInsightVisibility = BooleanField(
        'Block Insight Visibility', 
        # [validators.DataRequired()],
        # default=True
        )


