import datetime
from xero_python.accounting import CurrencyCode

line_items = {
    "1":
        {
            "AccountCode": "200-4",
            "Description": "Shipping to",
            "ItemCode": "1",
            "Quantity": 1.0,
            "TaxType": "OUTPUT",
            "UnitAmount": 42.0
        },
    "2":
        {
            "AccountCode": "210-4",
            "Description": "Shipping to",
            "ItemCode": "2",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 42.0
        },
    "3":
        {
            "AccountCode": "210-1",
            "Description": "Wooden Box",
            "ItemCode": "3",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 18.0
        },
    "QQ":
        {
            "AccountCode": "200-1",
            "Description": "430mm Custom Map of",
            "ItemCode": "QQ",
            "Quantity": 1.0,
            "TaxType": "OUTPUT",
            "UnitAmount": 560.0
        },
    "AA":
        {
            "AccountCode": "200-1",
            "Description": "600mm Custom Map of",
            "ItemCode": "AA",
            "Quantity": 1.0,
            "TaxType": "OUTPUT",
            "UnitAmount": 740.0
        },
    "ZZ":
        {
            "AccountCode": "200-1",
            "Description": "830mm Custom Map of",
            "ItemCode": "ZZ",
            "Quantity": 1.0,
            "TaxType": "OUTPUT",
            "UnitAmount": 1280.0
        },
    "WW":
        {
            "AccountCode": "210-1",
            "Description": "17.5\" Custom Map of",
            "ItemCode": "WW",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 440.0
        },
    "SS":
        {
            "AccountCode": "210-1",
            "Description": "24\" Custom Map of",
            "ItemCode": "SS",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 590.0
        },
    "XX":
        {
            "AccountCode": "210-1",
            "Description": "32\" Custom Map of",
            "ItemCode": "XX",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 980.0
        },
    "EE":
        {
            "AccountCode": "210-1",
            "Description": "17.5in Custom Map of",
            "ItemCode": "EE",
            "LineAmount": 560.0,
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 560.0
        },
    "DD":
        {
            "AccountCode": "210-1",
            "Description": "24in Custom Map of",
            "ItemCode": "DD",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 740.0
        },
    "CC":
        {
            "AccountCode": "210-1",
            "Description": "32in Custom Map of",
            "ItemCode": "CC",
            "Quantity": 1.0,
            "TaxType": "EXEMPTEXPORT",
            "UnitAmount": 1280.0
        }
}

invoice = {
    "BrandingThemeID": "d10b7a46-2fb8-49e7-89d1-2e04b7d6d8d1",
    "Contact": {
        "Name": "Buzz",
    },
    "CreditNotes": [],
    "CurrencyCode": CurrencyCode['AUD'],
    "Date": datetime.datetime.now(),
    "DueDate": datetime.datetime.now() + datetime.timedelta(days=1),
    "LineAmountTypes": "Inclusive",
    "LineItems": line_items,
    "Reference": "Buzz",
    "Status": "DRAFT",
    "Type": "ACCREC",
}

invoices = {
    "Invoices": [
        invoice,
    ]
}
