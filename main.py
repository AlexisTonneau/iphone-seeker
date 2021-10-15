import os

import requests

from twilio.rest import Client

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
phone_number = os.getenv('TWILIO_NUMBER')
my_phone_number = os.getenv('MY_NUMBER')

client = Client(account_sid, auth_token)
final_url = 'https://www.apple.com/shop/buy-iphone/iphone-13/6.1-inch-display-128gb-midnight-unlocked'
stores_here = ["R057", "R414", "R075"]


def send_message(text: str):
    msg = client.messages.create(to=my_phone_number, from_=phone_number, body=text)
    print(msg.sid)


def parse_request():
    res = requests.get(
        'https://www.apple.com/shop/fulfillment-messages?pl=true&cppart=UNLOCKED/US&parts.0=MLML3LL/A&location=94609')

    if not res.ok or not res.json()['head'] or res.json()['head']['status'] != '200':
        send_message(f'API Blocked request: {res.status_code}')
        return

    stores = res.json()['body']['content']['pickupMessage']['stores']

    available_stores = []

    for store in stores:
        if store['storeNumber'] in stores_here and store['partsAvailability']['MLML3LL/A'][
            'pickupDisplay'] == 'available':
            available_stores.append(store['address']['address'])
    print(available_stores)
    if len(available_stores) > 0:
        send_message("iPhone 13 dispo ! \n" + "\n".join(available_stores))


if __name__ == '__main__':
    parse_request()
