import requests


def shipment_sample(input_data, token):
    url = "https://apis-sandbox.fedex.com/ship/v1/shipments"

    payload = input_data # 'input' refers to JSON Payload
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
        }
    response = requests.request("POST", url, data=payload, headers=headers)

    return response


def validate_shipment_sample(input_data, token):
    url = "https://apis-sandbox.fedex.com/ship/v1/shipments/packages/validate"
    

    # payload = input # 'input' refers to JSON Payload
    payload = input_data # 'input' refers to JSON Payload
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

    return response

