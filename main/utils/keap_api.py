import json
import logging

import requests
from main import exceptions
from main.models import KeapAuth

BASE_URL = "https://api.infusionsoft.com/crm/rest/v1"

logger = logging.getLogger(__name__)

COUNTRY_CODES = {
    "BD": "BGD",
    "BE": "BEL",
    "BF": "BFA",
    "BG": "BGR",
    "BA": "BIH",
    "BB": "BRB",
    "WF": "WLF",
    "BL": "BLM",
    "BM": "BMU",
    "BN": "BRN",
    "BO": "BOL",
    "BH": "BHR",
    "BI": "BDI",
    "BJ": "BEN",
    "BT": "BTN",
    "JM": "JAM",
    "BV": "BVT",
    "BW": "BWA",
    "WS": "WSM",
    "BQ": "BES",
    "BR": "BRA",
    "BS": "BHS",
    "JE": "JEY",
    "BY": "BLR",
    "BZ": "BLZ",
    "RU": "RUS",
    "RW": "RWA",
    "RS": "SRB",
    "TL": "TLS",
    "RE": "REU",
    "TM": "TKM",
    "TJ": "TJK",
    "RO": "ROU",
    "TK": "TKL",
    "GW": "GNB",
    "GU": "GUM",
    "GT": "GTM",
    "GS": "SGS",
    "GR": "GRC",
    "GQ": "GNQ",
    "GP": "GLP",
    "JP": "JPN",
    "GY": "GUY",
    "GG": "GGY",
    "GF": "GUF",
    "GE": "GEO",
    "GD": "GRD",
    "GB": "GBR",
    "GA": "GAB",
    "SV": "SLV",
    "GN": "GIN",
    "GM": "GMB",
    "GL": "GRL",
    "GI": "GIB",
    "GH": "GHA",
    "OM": "OMN",
    "TN": "TUN",
    "JO": "JOR",
    "HR": "HRV",
    "HT": "HTI",
    "HU": "HUN",
    "HK": "HKG",
    "HN": "HND",
    "HM": "HMD",
    "VE": "VEN",
    "PR": "PRI",
    "PS": "PSE",
    "PW": "PLW",
    "PT": "PRT",
    "SJ": "SJM",
    "PY": "PRY",
    "IQ": "IRQ",
    "PA": "PAN",
    "PF": "PYF",
    "PG": "PNG",
    "PE": "PER",
    "PK": "PAK",
    "PH": "PHL",
    "PN": "PCN",
    "PL": "POL",
    "PM": "SPM",
    "ZM": "ZMB",
    "EH": "ESH",
    "EE": "EST",
    "EG": "EGY",
    "ZA": "ZAF",
    "EC": "ECU",
    "IT": "ITA",
    "VN": "VNM",
    "SB": "SLB",
    "ET": "ETH",
    "SO": "SOM",
    "ZW": "ZWE",
    "SA": "SAU",
    "ES": "ESP",
    "ER": "ERI",
    "ME": "MNE",
    "MD": "MDA",
    "MG": "MDG",
    "MF": "MAF",
    "MA": "MAR",
    "MC": "MCO",
    "UZ": "UZB",
    "MM": "MMR",
    "ML": "MLI",
    "MO": "MAC",
    "MN": "MNG",
    "MH": "MHL",
    "MK": "MKD",
    "MU": "MUS",
    "MT": "MLT",
    "MW": "MWI",
    "MV": "MDV",
    "MQ": "MTQ",
    "MP": "MNP",
    "MS": "MSR",
    "MR": "MRT",
    "IM": "IMN",
    "UG": "UGA",
    "TZ": "TZA",
    "MY": "MYS",
    "MX": "MEX",
    "IL": "ISR",
    "FR": "FRA",
    "IO": "IOT",
    "SH": "SHN",
    "FI": "FIN",
    "FJ": "FJI",
    "FK": "FLK",
    "FM": "FSM",
    "FO": "FRO",
    "NI": "NIC",
    "NL": "NLD",
    "NO": "NOR",
    "NA": "NAM",
    "VU": "VUT",
    "NC": "NCL",
    "NE": "NER",
    "NF": "NFK",
    "NG": "NGA",
    "NZ": "NZL",
    "NP": "NPL",
    "NR": "NRU",
    "NU": "NIU",
    "CK": "COK",
    "XK": "XKX",
    "CI": "CIV",
    "CH": "CHE",
    "CO": "COL",
    "CN": "CHN",
    "CM": "CMR",
    "CL": "CHL",
    "CC": "CCK",
    "CA": "CAN",
    "CG": "COG",
    "CF": "CAF",
    "CD": "COD",
    "CZ": "CZE",
    "CY": "CYP",
    "CX": "CXR",
    "CR": "CRI",
    "CW": "CUW",
    "CV": "CPV",
    "CU": "CUB",
    "SZ": "SWZ",
    "SY": "SYR",
    "SX": "SXM",
    "KG": "KGZ",
    "KE": "KEN",
    "SS": "SSD",
    "SR": "SUR",
    "KI": "KIR",
    "KH": "KHM",
    "KN": "KNA",
    "KM": "COM",
    "ST": "STP",
    "SK": "SVK",
    "KR": "KOR",
    "SI": "SVN",
    "KP": "PRK",
    "KW": "KWT",
    "SN": "SEN",
    "SM": "SMR",
    "SL": "SLE",
    "SC": "SYC",
    "KZ": "KAZ",
    "KY": "CYM",
    "SG": "SGP",
    "SE": "SWE",
    "SD": "SDN",
    "DO": "DOM",
    "DM": "DMA",
    "DJ": "DJI",
    "DK": "DNK",
    "VG": "VGB",
    "DE": "DEU",
    "YE": "YEM",
    "DZ": "DZA",
    "US": "USA",
    "UY": "URY",
    "YT": "MYT",
    "UM": "UMI",
    "LB": "LBN",
    "LC": "LCA",
    "LA": "LAO",
    "TV": "TUV",
    "TW": "TWN",
    "TT": "TTO",
    "TR": "TUR",
    "LK": "LKA",
    "LI": "LIE",
    "LV": "LVA",
    "TO": "TON",
    "LT": "LTU",
    "LU": "LUX",
    "LR": "LBR",
    "LS": "LSO",
    "TH": "THA",
    "TF": "ATF",
    "TG": "TGO",
    "TD": "TCD",
    "TC": "TCA",
    "LY": "LBY",
    "VA": "VAT",
    "VC": "VCT",
    "AE": "ARE",
    "AD": "AND",
    "AG": "ATG",
    "AF": "AFG",
    "AI": "AIA",
    "VI": "VIR",
    "IS": "ISL",
    "IR": "IRN",
    "AM": "ARM",
    "AL": "ALB",
    "AO": "AGO",
    "AQ": "ATA",
    "AS": "ASM",
    "AR": "ARG",
    "AU": "AUS",
    "AT": "AUT",
    "AW": "ABW",
    "IN": "IND",
    "AX": "ALA",
    "AZ": "AZE",
    "IE": "IRL",
    "ID": "IDN",
    "UA": "UKR",
    "QA": "QAT",
    "MZ": "MOZ",
}

TITLES = ["Mr.", "Mrs.", "Dr.", "Ms.", "Miss", "Mstr", "Professor"]


def filter_title(title):
    if title in TITLES:
        return title
    return ""


def make_auth_request(code: str):
    return KeapAuth().request_access_token(code)


class BillingAddress:
    def __init__(self, line_1, line_2, city, zip_code, country):
        self.line_1 = line_1 if line_1 else ""
        self.line_2 = line_2 if line_2 else ""
        self.city = city if city else ""
        self.zip_code = zip_code if zip_code else ""
        self.country = country if country else ""


class AdditionalPassengerInfo:
    def __init__(self, first_name, surname, tennis_standard):
        self.first_name = first_name if first_name else ""
        self.surname = surname if surname else ""
        self.tennis_standard = tennis_standard if tennis_standard else ""


class Booking:
    def __init__(
        self,
        id,
        url,
        status,
        created_date,
        start_date,
        end_date,
        event_type,
        tennis_club,
        group_organiser,
        event_location,
    ):
        self.id = id if id else ""
        self.url = url if url else ""
        self.status = status if status else ""
        self.created_date = created_date if created_date else ""
        self.start_date = start_date if start_date else ""
        self.end_date = end_date if end_date else ""
        self.event_type = event_type if event_type else ""
        self.tennis_club = tennis_club if tennis_club else ""
        self.group_organiser = group_organiser if group_organiser else ""
        self.event_location = event_location if event_location else ""


class BasicContacInfo:
    def __init__(
        self, email: str, first_name: str, last_name: str, title: str, phone_number: str
    ):
        self.email = email if email else ""
        self.first_name = first_name if first_name else ""
        self.last_name = last_name if last_name else ""
        self.title = title if title else ""
        self.phone_number = phone_number if phone_number else ""


class Contact:
    def __init__(
        self,
        basic_info: BasicContacInfo,
        product: str,
        venue: str,
        booked_items: str,
        billing_address: BillingAddress,
        level_of_tennis: str,
        tenis_standard_more_info: str,
        additional_passenger_1: AdditionalPassengerInfo,
        additional_passenger_2: AdditionalPassengerInfo,
        additional_passenger_3: AdditionalPassengerInfo,
        booking_data: Booking,
    ):
        self.opt_in_reason = "User has authorized."
        self.duplicate_option = "Email"
        self.tag_ids = [1342, 13988]
        self.source_type = "OTHER"
        self.email_addresses = [{"email": basic_info.email, "field": "EMAIL1"}]
        self.given_name = basic_info.first_name
        self.family_name = basic_info.last_name
        self.lead_source_id = 784
        self.note = f"""
        Booking created - {product} - {venue}
        Booking - {booked_items}        
        """
        self.addresses = [
            {
                "country_code": COUNTRY_CODES.get(
                    billing_address.country, billing_address.country
                ),
                "field": "BILLING",
                "line1": billing_address.line_1,
                "line2": billing_address.line_2,
                "locality": billing_address.city,
                "postal_code": "",
                "region": "",
                "zip_code": billing_address.zip_code,
                "zip_four": "",
            }
        ]
        self.phone_numbers = [
            {
                "extension": "",
                "field": "PHONE1",
                "number": basic_info.phone_number,
                "type": "",
            }
        ]
        self.prefix = basic_info.title
        self.custom_fields = [
            {
                "content": f"{level_of_tennis} - {tenis_standard_more_info}",
                "id": 9,
            },
            {
                "content": additional_passenger_1.first_name,
                "id": 239,
            },
            {
                "content": additional_passenger_1.surname,
                "id": 241,
            },
            {
                "content": additional_passenger_1.tennis_standard,
                "id": 245,
            },
            {
                "content": additional_passenger_2.first_name,
                "id": 247,
            },
            {
                "content": additional_passenger_2.surname,
                "id": 249,
            },
            {
                "content": additional_passenger_2.tennis_standard,
                "id": 255,
            },
            {
                "content": additional_passenger_3.first_name,
                "id": 257,
            },
            {
                "content": additional_passenger_3.surname,
                "id": 259,
            },
            {
                "content": booking_data.id,
                "id": 514,
            },
            {
                "content": booking_data.url,
                "id": 516,
            },
            {
                "content": booking_data.status,
                "id": 518,
            },
            {
                "content": booking_data.start_date,
                "id": 520,
            },
            {
                "content": booking_data.end_date,
                "id": 524,
            },
            {
                "content": booking_data.event_type,
                "id": 526,
            },
            {
                "content": booking_data.tennis_club,
                "id": 528,
            },
            {
                "content": booking_data.group_organiser,
                "id": 530,
            },
            {
                "content": booking_data.created_date,
                "id": 532,
            },
            {
                "content": booking_data.event_location,
                "id": 534,
            },
        ]

    def check_if_booking_exists(self):
        token = KeapAuth.objects.all()[0].get_actual_access_token()
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        # Check if the contact exists
        response = requests.get(
            f"{BASE_URL}/contacts",
            headers=headers,
            params={
                "email": self.email_addresses[0].get("email"),
                "optional_properties": "custom_fields",
            },
        )
        json = response.json()
        logger.debug(f"Checking if booking exists response: {json}")
        # If it doesn't exist, return False
        if json.get("count") == 0:
            return False
        # If it exists, check if the booking id is the same
        custom_fields_index = next(
            (index for (index, d) in enumerate(self.custom_fields) if d["id"] == 514),
            None,
        )
        booking_id_index = next(
            (
                index
                for (index, d) in enumerate(
                    json.get("contacts", {})[0].get("custom_fields")
                )
                if d["id"] == 514
            ),
            None,
        )
        return self.custom_fields[custom_fields_index].get("content") == json.get(
            "contacts"
        )[0].get("custom_fields")[booking_id_index].get("content")

    def add_or_update_additional_passenger_in_keap(self):
        self.tag_ids = [13988]
        return self.add_or_update_contact_in_keap()

    def add_or_update_contact_in_keap(self):
        token = KeapAuth.objects.all()[0].get_actual_access_token()
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Check if the booking exists and set the correct tag
        booking_exists = self.check_if_booking_exists()
        logger.debug(f"Booking exists: {booking_exists}")
        self.tag_ids = [14052] if booking_exists else [13988]

        # Create a copy of a dictionary containing all the attributes
        fields = vars(self).copy()

        # Delete the fields that are not used in the first request
        del fields["note"]
        del fields["tag_ids"]

        logger.debug(f"Fields send through request: {fields}")
        # Do the request
        response = requests.put(
            f"{BASE_URL}/contacts", data=json.dumps(fields), headers=headers
        )
        json_response = response.json()
        logger.info(
            f"Keap contact status: {response.status_code}; Response: {json_response}"
        )
        if response.status_code == 200 or response.status_code == 201:
            self.add_tags_to_contact(json_response["id"])
            self.create_contact_notes(json_response["id"])
            return json_response

        # Raise an exception if the request fails
        raise exceptions.RequestError(f"{response.status_code}: {json_response}")

    def add_tags_to_contact(self, contact_id):
        token = KeapAuth.objects.all()[0].get_actual_access_token()
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(
            f"{BASE_URL}/contacts/{contact_id}/tags",
            json.dumps({"tagIds": self.tag_ids}),
            headers=headers,
        )
        logger.info(
            f"Keap tag status: {response.status_code}; Response: {response.json()}"
        )
        if response.status_code == 200:
            return True
        raise exceptions.RequestError(f"{response.status_code}: {response.json()}")

    def create_contact_notes(self, contact_id):
        token = KeapAuth.objects.all()[0].get_actual_access_token()
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        request_body = {
            "contact_id": contact_id,
            "body": self.note,
        }
        response = requests.post(
            f"{BASE_URL}/notes", json.dumps(request_body), headers=headers
        )
        logger.info(
            f"Keap notes status: {response.status_code}; Response: {response.json()}"
        )
        if response.status_code == 201:
            return True
        raise exceptions.RequestError(f"{response.status_code}: {response.json()}")
