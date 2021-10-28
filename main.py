import os

import requests

from twilio.rest import Client
import pickle

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


def check_current_stores(stores):
    output = []
    with open('available_stores.txt', 'rb') as f:
        try:
            available_stores = pickle.load(f)
        except EOFError:
            available_stores = []
    for store in stores:
        if store not in available_stores:
            output.append(store)
    return output


def rewrite_current_stores(stores):
    open('available_stores.txt', 'w').close()
    with open('available_stores.txt', 'wb') as f:
        pickle.dump(stores, f)


def parse_request():
    res = requests.get(
        'https://www.apple.com/shop/fulfillment-messages?pl=true&cppart=UNLOCKED/US&parts.0=MLN13LL/A&location=94710')

    if not res.ok or not res.json()['head'] or res.json()['head']['status'] != '200':
        send_message(f'API Blocked request: {res.status_code}')
        return

    stores = res.json()['body']['content']['pickupMessage']['stores']

    available_stores = []

    for store in stores:
        if store['storeNumber'] in stores_here and store['partsAvailability']['MLN13LL/A'][
            'pickupDisplay'] == 'available':
            available_stores.append(store['address']['address'])
    checked_stores = check_current_stores(available_stores)
    if len(checked_stores) > 0:
        send_message("iPhone 13 dispo ! \n" + "\n".join(available_stores))
        rewrite_current_stores(available_stores)
        return
    print('Not available' if len(available_stores) == 0 else f"Not available but {','.join(available_stores)}")


if __name__ == '__main__':
    parse_request()
