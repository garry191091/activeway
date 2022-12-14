import logging
from datetime import datetime
from pickletools import int4

import pytz
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from main.utils import checkfront_api, keap_api, sheet_api
from main.utils.locals import find_replace_product_name, find_replace_venue_name

logger = logging.getLogger(__name__)


class WebhooksView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the booking information from the webhook
        booking = request.data["booking"]
        logger.debug(f"Booking dict: {booking}")

        # Check what product the customer ordered
        items = booking.get("order").get("items", "").get("item", {})
        # Customer has ordered more than one item
        products = []
        if type(items) is list:
            for product in items:
                products.append(
                    checkfront_api.check_item_name(
                        product["@attributes"].get("item_id")
                    )
                )
        # Customer has ordered just one item
        elif type(items) is dict:
            products.append(
                checkfront_api.check_item_name(items["@attributes"].get("item_id"))
            )
        order_product_name = ", ".join(str(x) for x in products)
        logger.debug("order_product_name: %s", order_product_name)

        # Find & Replace Product Name
        product = find_replace_product_name(order_product_name)

        # Find & Replace Venue
        venue = find_replace_venue_name(order_product_name)

        # Breakdown data into its appropriate classes
        basic_contact_info = keap_api.BasicContacInfo(
            email=booking["customer"].get("email", ""),
            first_name=booking["customer"].get("name", ""),
            last_name=booking["customer"].get("lplastname", ""),
            title=keap_api.filter_title(booking["customer"].get("lptitle", "")),
            phone_number=booking["customer"].get("phone", ""),
        )
        billing_address = keap_api.BillingAddress(
            line_1=booking["customer"].get("address", ""),
            line_2=booking["customer"].get("addressline2", ""),
            city=booking["customer"].get("city", ""),
            zip_code=booking["customer"].get("postal_zip", ""),
            country=booking["customer"].get("country", ""),
        )
        booking_url = f'https://activeaway.checkfront.co.uk/booking/{booking["code"]}'
        booking_data_class = keap_api.Booking(
            id=booking.get("code", ""),
            url=booking_url,
            status=checkfront_api.CHECKFRONT_STATUSES.get(
                booking.get("status"), booking.get("status")
            ),
            created_date=datetime.fromtimestamp(
                int(booking.get("created_date")), pytz.timezone("Europe/London")
            ).strftime("%Y-%m-%d"),
            start_date=datetime.fromtimestamp(
                int(booking.get("start_date")), pytz.timezone("Europe/London")
            ).strftime("%Y-%m-%d"),
            end_date=datetime.fromtimestamp(
                int(booking.get("end_date")), pytz.timezone("Europe/London")
            ).strftime("%Y-%m-%d"),
            event_type=product,
            tennis_club=booking["customer"].get("tennisclub"),
            event_location=venue,
            group_organiser=booking.get("customer").get("p5grp_ldr"),
        )
        additional_passenger_1 = keap_api.AdditionalPassengerInfo(
            first_name=booking["fields"].get("p2firstname"),
            surname=booking["fields"].get("p2lastname"),
            tennis_standard=booking["fields"].get("p2tennislevel"),
        )
        additional_passenger_2 = keap_api.AdditionalPassengerInfo(
            first_name=booking["fields"].get("p3firstname"),
            surname=booking["fields"].get("p3lastname"),
            tennis_standard=booking["fields"].get("p3tennislevel"),
        )
        additional_passenger_3 = keap_api.AdditionalPassengerInfo(
            first_name=booking["fields"].get("p3firstname"),
            surname=booking["fields"].get("p3lastname"),
            tennis_standard=booking["fields"].get("p3tennislevel"),
        )
        keap_contact = keap_api.Contact(
            basic_info=basic_contact_info,
            product=product,
            venue=venue,
            booked_items=order_product_name,
            billing_address=billing_address,
            level_of_tennis=booking["customer"].get("iptennislevel"),
            tenis_standard_more_info=str(
                booking["fields"].get("tennis_standard__more_informat")
            ),
            additional_passenger_1=additional_passenger_1,
            additional_passenger_2=additional_passenger_2,
            additional_passenger_3=additional_passenger_3,
            booking_data=booking_data_class,
        )

        # Add or update contact in keap
        logger.info("Adding or updating contact in keap...")
        keap_contact.add_or_update_contact_in_keap()
        logger.info("Contact added or updated in keap.")

        # Lookup Booking ID in Master Data
        booking_row_in_sheet = sheet_api.lookup_code(booking.get("code"))

        product_quantity = 0
        if type(items) is list:
            for item in items:
                product_quantity += int(item.get("qty"))
        if type(items) is dict:
            product_quantity = int(items.get("qty"))

        # Format the data to add
        balance_due = float(booking.get("order").get("total", "")) - float(
            booking.get("order").get("paid_total", "")
        )
        tax_included_total = float(booking.get("order").get("sub_total", 0)) + float(
            booking.get("order").get("tax_total", 0)
        )
        booking_data = [
            booking.get("code"),
            checkfront_api.CHECKFRONT_STATUSES.get(
                booking.get("status"), booking.get("status")
            ),
            datetime.fromtimestamp(
                int(booking.get("created_date")), pytz.timezone("Europe/London")
            ).strftime("%d/%m/%Y"),
            "",
            "",
            product,
            venue,
            product_quantity,
            booking.get("order").get("sub_total", ""),
            booking.get("order").get("tax_total"),
            f"{tax_included_total:.2f}",
            booking.get("order").get("discount"),
            "",
            "",
            booking.get("order").get("paid_total", ""),
            f"{balance_due:.2f}",
            booking.get("order").get("total", ""),
            order_product_name,
            booking.get("customer").get("lptitle", ""),
            keap_contact.given_name,
            keap_contact.family_name,
            booking.get("customer").get("lpdob", ""),
            booking.get("customer").get("email"),
            booking.get("customer").get("phone", ""),
            booking.get("customer").get("iptennislevel", ""),
            booking.get("fields").get("tennis_standard__more_informat", ""),
            booking.get("customer").get("address", ""),
            booking.get("customer").get("addressline2", ""),
            booking.get("customer").get("city", ""),
            booking.get("customer").get("postal_zip", ""),
            booking.get("customer").get("country", ""),
            booking.get("fields").get("promo", ""),
            booking.get("fields").get("how_did_hear_about_this_holida", ""),
            booking.get("fields").get("numbertravelling", ""),
            booking.get("fields").get("how_many_players", ""),
            booking.get("fields").get("tennisclub", ""),
            booking.get("fields").get("coachgroup", ""),
            booking.get("customer").get("p5grp_ldr", ""),
            booking.get("fields").get("sales_agent", ""),
            booking.get("fields").get("linked_booking_id", ""),
            booking.get("fields").get("p5board_basis", ""),
            booking.get("fields").get("p5r1_type", ""),
            booking.get("fields").get("p5room1_basis", ""),
            booking.get("fields").get("p5r1_sharing", ""),
            booking.get("fields").get("room_1_id", ""),
            booking.get("fields").get("p5room2_type", ""),
            booking.get("fields").get("p5room2_basis", ""),
            booking.get("fields").get("p5r2_sharing", ""),
            booking.get("fields").get("room_2_id", ""),
            booking.get("fields").get("p5r3_type", ""),
            booking.get("fields").get("p5room3_basis", ""),
            booking.get("fields").get("p5r3_sharing", ""),
            booking.get("fields").get("room_3_id", ""),
            booking.get("fields").get("p2firstname", ""),
            booking.get("fields").get("p2lastname", ""),
            booking.get("fields").get("p2dob", ""),
            booking.get("fields").get("p2-email", ""),
            booking.get("fields").get("p2-phone", ""),
            booking.get("fields").get("p2tennislevel", ""),
            booking.get("fields").get("p3firstname", ""),
            booking.get("fields").get("p3lastname", ""),
            booking.get("fields").get("p3dob", ""),
            booking.get("fields").get("p3_email", ""),
            booking.get("fields").get("p3_phone", ""),
            booking.get("fields").get("p3tennislevel", ""),
            booking.get("fields").get("p4firstname", ""),
            booking.get("fields").get("p4lastname", ""),
            booking.get("fields").get("p4dob", ""),
            booking.get("fields").get("p4_email", ""),
            booking.get("fields").get("p4_phone", ""),
            booking.get("fields").get("p4tennislevel", ""),
            booking.get("fields").get("p5firstname", ""),
            booking.get("fields").get("p5lastname", ""),
            booking.get("fields").get("p5dob", ""),
            booking.get("fields").get("p5_email", ""),
            booking.get("fields").get("p5_phone", ""),
            booking.get("fields").get("p5tennislevel", ""),
            booking.get("fields").get("p6firstname", ""),
            booking.get("fields").get("p6lastname", ""),
            booking.get("fields").get("p6dob", ""),
            booking.get("fields").get("p6_email", ""),
            booking.get("fields").get("p6_phone", ""),
            booking.get("fields").get("p6tennislevel", ""),
            booking.get("fields").get("tenfitpackage", ""),
            booking.get("fields").get("outbound_flight_arrival_date", ""),
            booking.get("fields").get("outflighttime", ""),
            booking.get("fields").get("outbound_flight_departure_airp", ""),
            booking.get("fields").get("outbound_flight_arrival_airpor", ""),
            booking.get("fields").get("outflightnum", ""),
            booking.get("fields").get("inbound_flight_departure_date", ""),
            booking.get("fields").get("inflighttime", ""),
            booking.get("fields").get("inbound_flight_departure_airpo", ""),
            booking.get("fields").get("inbound_flight_arrival_airport", ""),
            booking.get("fields").get("inflightnum", ""),
            booking_url,
            "",
            datetime.fromtimestamp(
                int(booking.get("start_date")), pytz.timezone("Europe/London")
            ).strftime("%Y%m%d"),
            datetime.fromtimestamp(
                int(booking.get("end_date")), pytz.timezone("Europe/London")
            ).strftime("%Y%m%d"),
        ]

        # Create or update booking in Master Data
        if booking_row_in_sheet:
            logger.info("Updating booking in Master Data")
            sheet_api.update_entry(
                f"A{booking_row_in_sheet}:CU{booking_row_in_sheet}",
                [
                    [
                        (str(i) if i != {} else "") for i in booking_data
                    ]  # Formatting empty data
                ],
            )
        else:
            logger.info("Adding booking in Master Data")
            sheet_api.create_entry([(str(i) if i != {} else "") for i in booking_data])

        # Create additional passengers
        for i in range(2, 7):
            if (i == 2 and booking.get("fields").get("p2-email", "")) or booking.get(
                "fields"
            ).get(f"p{i}_email", ""):
                basic_contact_info = keap_api.BasicContacInfo(
                    email=booking.get("fields").get("p2-email", "")
                    if i == 2
                    else booking.get("fields").get(f"p{i}_email", ""),
                    first_name=booking.get("fields").get(f"p{i}firstname", ""),
                    last_name=booking.get("fields").get(f"p{i}lastname", ""),
                    title=keap_api.filter_title(
                        booking.get("fields").get(f"p{i}title", "")
                    ),
                    phone_number=booking.get("fields").get("p2-phone", "")
                    if i == 2
                    else booking.get("fields").get(f"p{i}_phone", ""),
                )
                billing_address = keap_api.BillingAddress(
                    line_1="",
                    line_2="",
                    city="",
                    zip_code="",
                    country="",
                )
                empty_additional_passenger = keap_api.AdditionalPassengerInfo(
                    first_name="",
                    surname="",
                    tennis_standard="",
                )
                keap_contact = keap_api.Contact(
                    basic_info=basic_contact_info,
                    product=product,
                    venue=venue,
                    booked_items=order_product_name,
                    billing_address=billing_address,
                    level_of_tennis=booking.get("fields").get(f"p{i}tennislevel", ""),
                    tenis_standard_more_info="",
                    booking_data=booking_data_class,
                    additional_passenger_1=empty_additional_passenger,
                    additional_passenger_2=empty_additional_passenger,
                    additional_passenger_3=empty_additional_passenger,
                )
                keap_contact.add_or_update_contact_in_keap()

        return Response("", status=status.HTTP_200_OK)


class GetKeapAuthorizationLink(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            f"https://accounts.infusionsoft.com/app/oauth/authorize?client_id={settings.KEAP_CLIENT_ID}&redirect_uri={settings.KEAP_REDIRECT_URI}&response_type=code"
        )


class KeapCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        token = keap_api.make_auth_request(self.request.query_params.get("code", None))
        return Response(
            {"message": "Sucess", "token": token.access_token}, status.HTTP_200_OK
        )
