""" FEDEX API Reference
    https://developer.fedex.com/api/en-us/guides/api-reference.html
""" 
from dashboard.blueprints.fedex_api.api_codes.provinces_and_states import st_pr_codes


country_codes = {
    "Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "American Samoa": "AS",
    "Andorra": "AD",
    "Angola": "AO",
    "Anguilla": "AI",
    "Antarctica": "AQ",
    "Antigua, Barbuda": "AG",
    "Argentina": "AR",
    "Armenia": "AM",
    "Aruba": "AW",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Belize": "BZ",
    "Benin": "BJ",
    "Bermuda": "BM",
    "Bhutan": "BT",
    "Bolivia": "BO",
    "Bonaire, Caribbean Netherlands, Saba, St. Eustatius": "BQ",
    "Bosnia-Herzegovina": "BA",
    "Botswana": "BW",
    "Bouvet Island": "BV",
    "Brazil": "BR",
    "British Indian Ocean Territory": "IO",
    "Brunei": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Cape Verde": "CV",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China": "CN",
    "Christmas Island": "CX",
    "Cocos (Keeling) Islands": "CC",
    "Colombia": "CO",
    "Comoros": "KM",
    "Congo": "CG",
    "Congo, Democratic Republic Of": "CD",
    "Cook Islands": "CK",
    "Costa Rica": "CR",
    "Croatia": "HR",
    "Cuba": "CU",
    "Curacao": "CW",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominica": "DM",
    "Dominican Republic": "DO",
    "East Timor": "TL",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "England, Great Britain, Northern Ireland, Scotland, United Kingdom, Wales, Channel Islands": "GB",
    "Equatorial Guinea": "GQ",
    "Eritrea": "ER",
    "Estonia": "EE",
    "Ethiopia": "ET",
    "Faeroe Islands": "FO",
    "Falkland Islands": "FK",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "French Guiana": "GF",
    "French Southern Territories": "TF",
    "Gabon": "GA",
    "Gambia": "GM",
    "Georgia": "GE",
    "Germany": "DE",
    "Ghana": "GH",
    "Gibraltar": "GI",
    "Grand Cayman, Cayman Islands": "KY",
    "Great Thatch Island, Great Tobago Islands, Jost Van Dyke Islands, Norman Island, Tortola Island, British Virgin Islands": "VG",
    "Greece": "GR",
    "Greenland": "GL",
    "Grenada": "GD",
    "Guam": "GU",
    "Guatemala": "GT",
    "Guinea": "GN",
    "Guinea Bissau": "GW",
    "Guyana": "GY",
    "Haiti": "HT",
    "Heard and McDonald Islands": "HM",
    "Honduras": "HN",
    "Hong Kong": "HK",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Iraq": "IQ",
    "Ireland": "IE",
    "Israel": "IL",
    "Italy, Vatican City, San Marino": "IT",
    "Ivory Coast": "CI",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Kiribati": "KI",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Laos": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libya": "LY",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Macau": "MO",
    "Macedonia": "MK",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Malaysia": "MY",
    "Maldives": "MV",
    "Mali": "ML",
    "Malta": "MT",
    "Marshall Islands": "MH",
    "Martinique": "MQ",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mayotte": "YT",
    "Mexico": "MX",
    "Micronesia": "FM",
    "Moldova": "MD",
    "Monaco": "MC",
    "Mongolia": "MN",
    "Montenegro": "ME",
    "Montserrat": "MS",
    "Morocco": "MA",
    "Mozambique": "MZ",
    "Myanmar / Burma": "MM",
    "Namibia": "NA",
    "Nauru": "NR",
    "Nepal": "NP",
    "Netherlands, Holland": "NL",
    "New Caledonia": "NC",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "Niue": "NU",
    "Norfolk Island": "NF",
    "North Korea": "KP",
    "Northern Mariana Islands, Rota, Saipan, Tinian": "MP",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Palau": "PW",
    "Palestine": "PS",
    "Panama": "PA",
    "Papua New Guinea": "PG",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Pitcairn": "PN",
    "Poland": "PL",
    "Portugal": "PT",
    "Puerto Rico": "PR",
    "Qatar": "QA",
    "Reunion": "RE",
    "Romania": "RO",
    "Russia": "RU",
    "Rwanda": "RW",
    "Samoa": "WS",
    "Sao Tome and Principe": "ST",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Serbia": "RS",
    "Seychelles": "SC",
    "Sierra Leone": "SL",
    "Singapore": "SG",
    "Slovak Republic": "SK",
    "Slovenia": "SI",
    "Solomon Islands": "SB",
    "Somalia": "SO",
    "South Africa": "ZA",
    "South Georgia and South Sandwich Islands": "GS",
    "South Korea": "KR",
    "Spain, Canary Islands": "ES",
    "Sri Lanka": "LK",
    "GuadeloupeSt., Barthelemy": "GP",
    "St. Christopher, St. Kitts And Nevis": "KN",
    "St. John, St. Thomas, U.S. Virgin Islands, St. Croix Island": "VI",
    "St. Helena": "SH",
    "St. Lucia": "LC",
    "St. Maarten (Dutch Control)": "SX",
    "St. Martin (French Control)": "MF",
    "St. Pierre": "PM",
    "St. Vincent, Union Island": "VC",
    "Sudan": "SD",
    "Suriname": "SR",
    "Svalbard and Jan Mayen Island": "SJ",
    "Swaziland": "SZ",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Syria": "SY",
    "Tahiti, French Polynesia": "PF",
    "Taiwan": "TW",
    "Tajikistan": "TJ",
    "Tanzania": "TZ",
    "Thailand": "TH",
    "Togo": "TG",
    "Tokelau": "TK",
    "Tonga": "TO",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Turkmenistan": "TM",
    "Turks and Caicos Islands": "TC",
    "Tuvalu": "TV",
    "U.S. Minor Outlying Islands": "UM",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "United States": "US",
    "Uruguay": "UY",
    "Uzbekistan": "UZ",
    "Vanuatu": "VU",
    "Venezuela": "VE",
    "Vietnam": "VN",
    "Wallis and Futuna Islands": "WF",
    "Western Sahara": "EH",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Zimbabwe": "ZW"
}

def get_country_code(country_name):
    """Get Country code from FedEx API reference table

    Args:
        country_name (string): Full Country name

    Returns:
        string: Country code like `US`, `UK`, `AU`
    """
    if country_name:
        for key in country_codes.keys():
            if country_name.upper() in key.upper():
                country_code = country_codes.get(key)
                return country_code
    return None


def get_state_or_province_code(country_name, province):
    """Get Province or State code from FedEx API reference table
        Note: not all countries has a state or province code

    Args:
        country_name (string): Full Country name
        province (string): Province name

    Returns:
        string: Province code like `AL` for US->Alabama
    """
    country_code = get_country_code(country_name)
    if country_code:
        for k in st_pr_codes.keys():
            if country_code in k:
                codes = st_pr_codes.get(k)
                for province_k in codes:
                    if province.upper() in province_k.upper():
                        code = codes.get(province_k)
                        return code
    return None


def has_code(country_name):
    """ Check if Country has codes in FedEx API reference table

    Args:
        country_name (string): Full Country name

    Returns:
        bool: True if Country has codes
    """
    country_code = get_country_code(country_name)
    if country_code:
        for k in st_pr_codes.keys():
            if country_code in k:
                return True
    return False


if __name__=='__main__':
    # testing
    # python -m dashboard.blueprints.fedex_api.api_codes.mas

    # country_code = get_country_code('australia')
    # country_code = get_country_code('united States')
    # print(country_code)
    code = get_state_or_province_code('united states', 'alabama')
    print(code)
    pass