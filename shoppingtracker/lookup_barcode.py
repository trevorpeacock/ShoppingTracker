import openfoodfacts
import requests
import shoppingtracker.settings
import hashlib
import base64
import hmac


def lookup_item_online(stockitem):
    if not stockitem.barcode.isdigit():
        return
    print("Looking up", stockitem.barcode)
    sig = base64.b64encode(
        hmac.new(
            settings.DIGITEYES_AUTH_KEY.encode('ascii'),
            stockitem.barcode.encode('ascii'),
            hashlib.sha1
        ).digest()
    ).decode('ascii')
    search_result = requests.get(
        'https://www.digit-eyes.com/gtin/v2_0/?upcCode={}&field_names=all&language=en&app_key={}&signature={}'.format(
            stockitem.barcode, settings.DIGITEYES_APP_KEY, sig)).json()
    print(search_result)
    if search_result['return_code'] == '0':
        if search_result['description']:
            stockitem.name = search_result['description']
        if search_result['brand']:
            stockitem.brand = search_result['brand']
        return True
    search_result = openfoodfacts.products.get_product(stockitem.barcode)
    print(search_result)
    if search_result['status'] == 1:
        stockitem.name = search_result['product']['product_name']
        if 'product_name_en' in search_result['product']:
            stockitem.name = search_result['product']['product_name_en']
        if 'brands' in search_result['product']:
            stockitem.brand = search_result['product']['brands']
        return True
    search_result = requests.get(
        "https://eandata.com/feed/?v=3&keycode={}&mode=json&find={}".format(
            settings.EANDATA_KEY, stockitem.barcode)).json()
    print(search_result)
    if search_result['status']['code'] == '200':
        stockitem.name = search_result['product']['attributes']['product']
        return True
