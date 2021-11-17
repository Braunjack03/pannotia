""" Choices
"""
class FedExChoices:

    packaging_choices = [
        'YOUR_PACKAGING',
        'FEDEX_ENVELOPE',
        'FEDEX_BOX',
        'FEDEX_SMALL_BOX',
        'FEDEX_MEDIUM_BOX',
        'FEDEX_LARGE_BOX',
        'FEDEX_EXTRA_LARGE_BOX',
        'FEDEX_10KG_BOX',
        'FEDEX_25KG_BOX',
        'FEDEX_PAK',
    ]

    sh_purpose_choices = [
        ('', 'Commercial'),
        ('GIFT', 'Gift'),
        ('NOT_SOLD', 'Not sold'),
        ('PERSONAL_EFFECTS', 'Personal Effects'),
        ('PERSONAL_USER', 'Personal Users'),
        ('REPAIR_AND_RETURN', 'Repair and return'),
        ('SAMPLE', 'SAMPLE'),
    ]

    service_type = [
        ("FEDEX_2_DAY", "FedEx 2Day®"),
        ("FEDEX_2_DAY_AM", "FedEx 2Day® A.M."),
        ("FEDEX_CUSTOM_CRITICAL_CHARTER_AIR", "FedEx Custom Critical Air"),
        ("FEDEX_CUSTOM_CRITICAL_AIR_EXPEDITE", "FedEx Custom Critical Air Expedite"),
        ("FEDEX_CUSTOM_CRITICAL_AIR_EXPEDITE_EXCLUSIVE_USE", "FedEx Custom Critical Air Expedite Exclusive Use"),
        ("FEDEX_CUSTOM_CRITICAL_AIR_EXPEDITE_NETWORK", "FedEx Custom Critical Air Expedite Network"),
        ("FEDEX_CUSTOM_CRITICAL_POINT_TO_POINT", "FedEx Custom Critical Point To Point"),
        ("FEDEX_CUSTOM_CRITICAL_SURFACE_EXPEDITE", "FedEx Custom Critical Surface Expedite"),
        ("FEDEX_CUSTOM_CRITICAL_SURFACE_EXPEDITE_EXCLUSIVE_USE", "FedEx Custom Critical Surface Expedite Exclusive Use"),
        ("EUROPE_FIRST_INTERNATIONAL_PRIORITY", "FedEx Europe First"),
        ("FEDEX_EXPRESS_SAVER", "FedEx Express Saver®"),
        ("FIRST_OVERNIGHT", "FedEx First Overnight®"),
        ("FEDEX_FIRST_OVERNIGHT_EXTRA_HOURS", "FedEx First Overnight® EH"),
        ("FEDEX_GROUND", "FedEx Ground"),
        ("GROUND_HOME_DELIVERY", "FedEx Home Delivery®"),
        ("FEDEX_CARGO_AIRPORT_TO_AIRPORT", "FedEx International Airport-to-Airport"),
        ("FEDEX_INTERNATIONAL_CONNECT_PLUS", "FedEx International Connect Plus®"),
        ("INTERNATIONAL_ECONOMY", "FedEx International Economy"),
        ("INTERNATIONAL_ECONOMY_DISTRIBUTION", "FedEx International Economy DirectDistributionSM"),
        ("INTERNATIONAL_FIRST", "FedEx International First®"),
        ("FEDEX_CARGO_MAIL", "FedEx International MailService®"),
        ("FEDEX_CARGO_INTERNATIONAL_PREMIUM", "FedEx International Premium™"),
        ("INTERNATIONAL_PRIORITY_DISTRIBUTION", "FedEx International Priority DirectDistribution®"),
        ("FEDEX_INTERNATIONAL_PRIORITY_PLUS", "FedEx International Priority Plus®"),
        ("INTERNATIONAL_PRIORITY", "FedEx International Priority®"),
        ("PRIORITY_OVERNIGHT", "FedEx Priority Overnight®"),
        ("PRIORITY_OVERNIGHT_EXTRA_HOURS", "FedEx Priority Overnight® EH"),
        ("SAME_DAY", "FedEx SameDay®"),
        ("SAME_DAY_CITY", "FedEx SameDay® City"),
        ("SMART_POST", "FedEx SmartPost®"),
        ("FEDEX_STANDARD_OVERNIGHT_EXTRA_HOURS", "FedEx Standard Overnight® EH"),
        ("STANDARD_OVERNIGHT", "FedEx Standard Overnight®"),
        ("TRANSBORDER_DISTRIBUTION_CONSOLIDATION", "FedEx Transborder Distribution"),
        ("FEDEX_CUSTOM_CRITICAL_TEMP_ASSURE_AIR", "Temp-Assure Air®"),
        ("FEDEX_CUSTOM_CRITICAL_TEMP_ASSURE_VALIDATED_AIR", "Temp-Assure Validated Air®"),
        ("FEDEX_CUSTOM_CRITICAL_WHITE_GLOVE_SERVICES", "White Glove Services®"),
        ("FEDEX_REGIONAL_ECONOMY", "FedEx Regional Economy®"),
        ("FEDEX_REGIONAL_ECONOMY_FREIGHT", "FedEx Regional Economy® Freight"),
        ("FEDEX_INTERNATIONAL_PRIORITY", "FedEx International Priority®"),
        ("FEDEX_INTERNATIONAL_PRIORITY_EXPRESS", "FedEx International Priority® Express"),
        ("FEDEX_1_DAY_FREIGHT", "FedEx 1 Day Freight"),
        ("FEDEX_2_DAY_FREIGHT", "FedEx 2 Day Freight"),
        ("FEDEX_3_DAY_FREIGHT", "FedEx 3 Day Freight"),
        ("FIRST_OVERNIGHT_FREIGHT", "FedEx First Overnight Freight"),
        ("FEDEX_NEXT_DAY_AFTERNOON", "FedEx Next Day Afternoon"),
        ("FEDEX_NEXT_DAY_EARLY_MORNING", "FedEx Next Day Morning"),
        ("FEDEX_NEXT_DAY_END_OF_DAY", "FedEx Next Day End of Day"),
        ("FEDEX_NEXT_DAY_MID_MORNING", "FedEx Next Day Mid Morning"),
        ("INTERNATIONAL_ECONOMY_FREIGHT", "International Economy Freight"),
        ("INTERNATIONAL_PRIORITY_FREIGHT", "International Priority Freight"),
    ]

    pickup_type = [
        ("DROPOFF_AT_FEDEX_LOCATION", "DROP OFF PACKAGE AT FEDEX LOCATION"),
        ("USE_SCHEDULED_PICKUP", "USE AN ALREADY SCHEDULED PICKUP AT MY LOCATION"),
        ("CONTACT_FEDEX_TO_SCHEDULE", "SCHEDULE A PICKUP"),
    ]

    paymentType = [
        "SENDER",
        "RECIPIENT",
        "THIRD_PARTY",
        "COLLECT"
    ]
