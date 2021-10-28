""" Contains default FedEx API payloads for Shipment endpoints
    https://developer.fedex.com/api/en-us/catalog/ship/v1/docs.html#operation/Create%20Shipment

"""


create_shipment_json = {

  'International_Shipment': """{
    "labelResponseOptions": "URL_ONLY",
    "requestedShipment": {
      "shipper": {
        "contact": {
          "personName": "SHIPPER NAME",
          "phoneNumber": 1234567890,
          "companyName": "Shipper Company Name"
        },
        "address": {
          "streetLines": [
            "SHIPPER STREET LINE 1"
          ],
          "city": "Memphis",
          "stateOrProvinceCode": "TN",
          "postalCode": 38116,
          "countryCode": "US"
        }
      },
      "recipients": [
        {
          "contact": {
            "personName": "RECIPIENT NAME",
            "phoneNumber": 1234567890,
            "companyName": "Recipient Company Name"
          },
          "address": {
            "streetLines": [
              "RECIPIENT STREET LINE 1",
              "RECIPIENT STREET LINE 2",
              "RECIPIENT STREET LINE 3"
            ],
            "city": "RICHMOND",
            "stateOrProvinceCode": "BC",
            "postalCode": "V7C4V7",
            "countryCode": "CA"
          }
        }
      ],
      "shipDatestamp": "2020-07-03",
      "serviceType": "INTERNATIONAL_PRIORITY",
      "packagingType": "YOUR_PACKAGING",
      "pickupType": "USE_SCHEDULED_PICKUP",
      "blockInsightVisibility": false,
      "shippingChargesPayment": {
        "paymentType": "SENDER"
      },
      "labelSpecification": {
        "imageType": "PDF",
        "labelStockType": "PAPER_85X11_TOP_HALF_LABEL"
      },
      "customsClearanceDetail": {
        "dutiesPayment": {
          "paymentType": "SENDER"
        },
        "isDocumentOnly": true,
        "commodities": [
          {
            "description": "Commodity description",
            "countryOfManufacture": "US",
            "quantity": 1,
            "quantityUnits": "PCS",
            "unitPrice": {
              "amount": 100,
              "currency": "USD"
            },
            "customsValue": {
              "amount": 100,
              "currency": "USD"
            },
            "weight": {
              "units": "LB",
              "value": 20
            }
          }
        ]
      },
      "shippingDocumentSpecification": {
        "shippingDocumentTypes": [
          "COMMERCIAL_INVOICE"
        ],
        "commercialInvoiceDetail": {
          "documentFormat": {
            "stockType": "PAPER_LETTER",
            "docType": "PDF"
          }
        }
      },
      "requestedPackageLineItems": [
        {
          "weight": {
            "units": "LB",
            "value": 70
          },
          "dimensions": {
            "length": 90,
            "width": 90,
            "height": 10,
            "units": "CM"
         }
        }
      ]
    },
    "accountNumber": {
      "value": "XXX561073"
    }
  }
  """,

  'International_SingleShot_Multi_Piece_Shipment' : """
  {
    "labelResponseOptions": "URL_ONLY",
    "requestedShipment": {
      "shipper": {
        "contact": {
          "personName": "SHIPPER NAME",
          "phoneNumber": 1234567890,
          "companyName": "Shipper Company Name"
        },
        "address": {
          "streetLines": [
            "SHIPPER STREET LINE 1"
          ],
          "city": "Memphis",
          "stateOrProvinceCode": "TN",
          "postalCode": 38116,
          "countryCode": "US"
        }
      },
      "recipients": [
        {
          "contact": {
            "personName": "RECIPIENT NAME",
            "phoneNumber": 1234567890,
            "companyName": "Recipient Company Name"
          },
          "address": {
            "streetLines": [
              "RECIPIENT STREET LINE 1",
              "RECIPIENT STREET LINE 2",
              "RECIPIENT STREET LINE 3"
            ],
            "city": "RICHMOND",
            "stateOrProvinceCode": "BC",
            "postalCode": "V7C4V7",
            "countryCode": "CA"
          }
        }
      ],
      "shipDatestamp": "2020-07-03",
      "serviceType": "INTERNATIONAL_PRIORITY",
      "packagingType": "YOUR_PACKAGING",
      "pickupType": "USE_SCHEDULED_PICKUP",
      "blockInsightVisibility": false,
      "shippingChargesPayment": {
        "paymentType": "SENDER"
      },
      "labelSpecification": {
        "imageType": "PDF",
        "labelStockType": "PAPER_85X11_TOP_HALF_LABEL"
      },
      "customsClearanceDetail": {
        "dutiesPayment": {
          "paymentType": "SENDER"
        },
        "isDocumentOnly": false,
        "commodities": [
          {
            "description": "Commodity description",
            "countryOfManufacture": "US",
            "quantity": 3,
            "quantityUnits": "PCS",
            "unitPrice": {
              "amount": 100,
              "currency": "USD"
            },
            "customsValue": {
              "amount": 300,
              "currency": "USD"
            },
            "weight": {
              "units": "LB",
              "value": 20
            }
          }
        ]
      },
      "shippingDocumentSpecification": {
        "shippingDocumentTypes": [
          "COMMERCIAL_INVOICE"
        ],
        "commercialInvoiceDetail": {
          "documentFormat": {
            "docType": "PDF",
            "stockType": "PAPER_LETTER"
          }
        }
      },
      "requestedPackageLineItems": [
        {
          "groupPackageCount": 1,
          "weight": {
            "value": 10,
            "units": "LB"
          },
          "declaredValue": {
            "amount": 100,
            "currency": "USD"
          }
        },
        {
          "groupPackageCount": 2,
          "weight": {
            "value": 5,
            "units": "LB"
          },
          "declaredValue": {
            "amount": 100,
            "currency": "USD"
          }
        }
      ]
    },
    "accountNumber": {
      "value": "XXX561073"
    }
  }""",

  'One_Rate_Shipment' : """{
    "labelResponseOptions": "URL_ONLY",
    "requestedShipment": {
      "shipper": {
        "contact": {
          "personName": "SHIPPER NAME",
          "phoneNumber": 1234567890,
          "companyName": "Shipper Company Name"
        },
        "address": {
          "streetLines": [
            "SHIPPER STREET LINE 1"
          ],
          "city": "HARRISON",
          "stateOrProvinceCode": "AR",
          "postalCode": 72601,
          "countryCode": "US"
        }
      },
      "recipients": [
        {
          "contact": {
            "personName": "RECIPIENT NAME",
            "phoneNumber": 1234567890,
            "companyName": "Recipient Company Name"
          },
          "address": {
            "streetLines": [
              "RECIPIENT STREET LINE 1",
              "RECIPIENT STREET LINE 2"
            ],
            "city": "Collierville",
            "stateOrProvinceCode": "TN",
            "postalCode": 38017,
            "countryCode": "US"
          }
        }
      ],
      "shipDatestamp": "2020-12-30",
      "serviceType": "STANDARD_OVERNIGHT",
      "packagingType": "FEDEX_SMALL_BOX",
      "pickupType": "USE_SCHEDULED_PICKUP",
      "blockInsightVisibility": false,
      "shippingChargesPayment": {
        "paymentType": "SENDER"
      },
      "shipmentSpecialServices": {
        "specialServiceTypes": [
          "FEDEX_ONE_RATE"
        ]
      },
      "labelSpecification": {
        "imageType": "PDF",
        "labelStockType": "PAPER_85X11_TOP_HALF_LABEL"
      },
      "requestedPackageLineItems": [
        {}
      ]
    },
    "accountNumber": {
      "value": "510088000"
    }
  }""",


}



# =========== Validation
validate_shipment_json = {

  'Minimal_Sample_Domestic' : """{
    "requestedShipment": {
      "pickupType": "USE_SCHEDULED_PICKUP",
      "serviceType": "PRIORITY_OVERNIGHT",
      "packagingType": "YOUR_PACKAGING",
      "shipper": {
        "address": {
          "streetLines": [
            "10 FedEx Parkway",
            "Suite 302"
          ],
          "city": "Beverly Hills",
          "stateOrProvinceCode": "CA",
          "postalCode": 90210,
          "countryCode": "US"
        },
        "contact": {
          "personName": "SHIPPER NAME",
          "phoneNumber": 1234567890,
          "companyName": "Shipper Company Name"
        }
      },
      "recipients": {
        "address": {
          "streetLines": "-10 FedEx Parkway -Suite 302",
          "city": "Beverly Hills",
          "stateOrProvinceCode": "CA",
          "postalCode": 90210,
          "countryCode": "US"
        },
        "contact": {
          "personName": "SHIPPER NAME",
          "phoneNumber": 9612345671,
          "companyName": "Shipper Company Name"
        }
      },
      "shippingChargesPayment": {
        "paymentType": "SENDER",
        "payor": {
          "responsibleParty": {
            "accountNumber": {
              "value": "Your account number"
            }
          }
        }
      },
      "labelSpecification": {
        "labelStockType": "PAPER_7X475",
        "imageType": "PDF"
      },
      "requestedPackageLineItems": {
        "weight": {
          "units": "LB",
          "value": 68
        }
      }
    },
    "accountNumber": {
      "value": "510088000"
    }
  }
  """
}
# =========== END Validation


