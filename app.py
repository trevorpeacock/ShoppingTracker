import db_setup
import db.models
import tkinter
import tkinter.font
import os
import datetime
import decimal
import traceback
import subprocess
from navigation import *
from input import *
from display import *
from gui import TextApplication
import openfoodfacts
import requests
import settings
import hashlib
import base64
import hmac


def lookup_item_online(stockitem):
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


class Home(DisplayHandler):
    def display_contents(self):
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Commands\n")
        self.text.insert(tkinter.END, "========\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "  Type a command and then press enter\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "      a  - Scan items to add to inventory\n")
        self.text.insert(tkinter.END, "      s  - Search inventory\n")
        self.text.insert(tkinter.END, "      l  - List inventory\n")
        self.text.insert(tkinter.END, "      p  - Print shopping list\n")
        self.text.insert(tkinter.END, "     < > - Scan item to use\n")
        self.text.insert(tkinter.END, "      q  - Quit\n")

    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'a':
            self.navigate(AddStock)
            return
        if s.lower() == 's':
            self.navigate(SearchStock)
            return
        if s.lower() == 'l':
            self.navigate(ListStock)
            return
        if s.lower() == 'p':
            self.navigate(PrintShoppingList)
            return
        if s.lower() == 'q':
            self.navigate(Quit)
            return
        try:
            stockitem = db.models.StockItem.objects.get(barcode=s.lower())
            change = db.models.LevelChange()
            change.item = stockitem
            change.change = -1
            change.save()
        except db.models.StockItem.DoesNotExist:
            subprocess.call(['play', 'bell.wav'])
        super().text_search(s)


class ListStock(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)

    def display_contents(self):
        self.text.insert(tkinter.END, "Pantry List\n")
        self.text.insert(tkinter.END, "===========\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Press ESC to go back or click on an item to view details\n")
        self.text.insert(tkinter.END, "\n")
        for item in db.models.StockItem.objects.all():
            self.text.insert(tkinter.END, "{:14}".format(item.barcode), 'stockitem')
            self.text.insert(tkinter.END, "  ")
            self.text.insert(tkinter.END, "{:3}".format(sum([c.change for c in item.levelchange_set.all()])))
            self.text.insert(tkinter.END, " x  ")
            self.text.insert(tkinter.END, item)
            self.text.insert(tkinter.END, "\n")


class SearchStockResults(DisplayHandler):
    def __init__(self, root, string):
        super().__init__(root)
        self.string = string

    def display_contents(self):
        self.text.insert(tkinter.END, f"Search Results\n")
        self.text.insert(tkinter.END, f"==============\n")
        self.text.insert(tkinter.END, f"\n")
        self.text.insert(tkinter.END, f"Press ESC to go back to menu. Click on an item to view details\n")
        self.text.insert(tkinter.END, f"\n")
        self.text.insert(tkinter.END, f"  Query: {self.string}\n")
        self.text.insert(tkinter.END, f"\n")
        self.text.insert(tkinter.END, f"  Results:\n")
        for item in db.models.StockItem.objects.all():
            if self.string.lower() in item.name.lower():
                self.text.insert(tkinter.END, "  ")
                self.text.insert(tkinter.END, "{:14}".format(item.barcode), 'stockitem')
                self.text.insert(tkinter.END, "  ")
                self.text.insert(tkinter.END, item)
                self.text.insert(tkinter.END, "\n")


class SearchStock(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)

    key_input_handler_class = TypingInputHandler

    def display_contents(self):
        self.text.insert(tkinter.END, "Type something to search, and press enter, or scan an item.\n")
        self.text.insert(tkinter.END, "Press ESC to cancel.\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Search: ")
        self.input_handler.display(self.text)
        self.text.insert(tkinter.END, "\n")

    def text_search(self, s):
        try:
            stockitem = db.models.StockItem.objects.get(barcode=s.lower())
            self.navigate_replace(DisplayStockItem, stockitem)
            return
        except db.models.StockItem.DoesNotExist:
            pass
        if s.strip() == '':
            return
        self.navigate_replace(SearchStockResults, s.strip().lower())
        return


class DisplayStockItem(DisplayHandler):
    # TODO: Edit stock item with multiple input fields
    def __init__(self, root, stockitem):
        super().__init__(root)
        self.stockitem = stockitem

    def display_contents(self):
        self.text.insert(tkinter.END, "Item Detail\n")
        self.text.insert(tkinter.END, "===========\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Press ESC to go back.\n")
        self.text.insert(tkinter.END, "\n")
        levelchanges = self.stockitem.levelchange_set.all().order_by('date')
        self.text.insert(tkinter.END, f"Barcode:  {self.stockitem.barcode}\n")
        self.text.insert(tkinter.END, f"Name:     {self.stockitem.name}\n")
        self.text.insert(tkinter.END, f"Brand:    {self.stockitem.brand}\n")
        quantity = sum([c.change for c in levelchanges])
        self.text.insert(tkinter.END, f"Quantity: {quantity}\n")
#        self.text.insert(tkinter.END, f"Category: {self.stockitem.category}\n")
        self.text.insert(tkinter.END, f"Notes:    {self.stockitem.notes}\n")
        self.text.insert(tkinter.END, "\n")
        for levelchange in levelchanges:
            self.text.insert(tkinter.END, f"  {levelchange.date} {levelchange.change}\n")


class NewStockItem(DisplayHandler):
    def __init__(self, root, stockitem):
        super().__init__(root)
        self.stockitem = stockitem
        self.step = 1

    key_input_handler_class = TypingInputHandler

    def create_input_handler(self):
        self.input_handler = self.key_input_handler_class(self.displaynavigation, self, 100, self.stockitem.name)

    def display_contents(self):
        self.text.insert(tkinter.END, "New Item Details\n")
        self.text.insert(tkinter.END, "================\n")
        self.text.insert(tkinter.END, "\n")
        if self.step == 1:
            self.text.insert(tkinter.END, "Enter name of new item\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, f"Barcode: {self.stockitem.barcode}\n")
        self.text.insert(tkinter.END, f"Name:    ")
        self.input_handler.display(self.text)
        self.text.insert(tkinter.END, f"\n")
        self.text.insert(tkinter.END, f"Brand:   {self.stockitem.brand}\n")

    def text_search(self, s):
        if self.step == 1:
            self.stockitem.name = s.strip()
            self.stockitem.save()
            self.navigate_back()


class LookupNewStockItem(DisplayHandler):
    def __init__(self, root, stockitem):
        super().__init__(root)
        self.stockitem = stockitem
        #self.step = 1
        #self.total_steps = 2

    key_input_handler_class = KeyInputHandler # TODO: need an ignore key handler

    def display_contents(self):
        self.text.insert(tkinter.END, "Looking up item online\n")
        self.text.insert(tkinter.END, "======================\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "   Please wait...\n")
        #self.text.insert(tkinter.END, "  {} / {}\n".format(self.step, self.total_steps))

    def run_new(self):
        super().run_new()
        subprocess.call(['play', 'bell.wav'])
        self.displaynavigation.root.after(50, self.lookup_online)

    def lookup_online(self):
        lookup_item_online(self.stockitem)
        self.navigate_replace(NewStockItem, self.stockitem)


class AddStock(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)
        self.list = {}
        self.newitem = None

    key_input_handler_class = TypingInputHandler

    def create_input_handler(self):
        self.input_handler = self.key_input_handler_class(self.displaynavigation, self, 50)

    def add_item(self, stockitem):
        if stockitem in self.list:
            self.list[stockitem] += 1
        else:
            self.list[stockitem] = 1

    def run_return(self):
        if self.newitem.id:
            self.add_item(self.newitem)
        else:
            self.newitem = None
        super().run_return()

    def run_exit(self):
        for item, quantity in self.list.items():
            change = db.models.LevelChange()
            change.item = item
            change.change = quantity
            change.save()
        super().run_exit()

    def display_contents(self):
        self.text.insert(tkinter.END, "Add Items to Pantry\n")
        self.text.insert(tkinter.END, "===================\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Scan items to add. Press ESC when done.\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Items:\n")
        self.text.insert(tkinter.END, "\n")
        for item, quantity in self.list.items():
            self.text.insert(tkinter.END, f"{quantity} x {item}\n")

    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'q':
            self.navigate_back()
            return
        try:
            stockitem = db.models.StockItem.objects.get(barcode=s.lower())
            self.add_item(stockitem)
            self.display()
        except db.models.StockItem.DoesNotExist:
            self.newitem = db.models.StockItem()
            self.newitem.barcode = s.lower()
            self.navigate(LookupNewStockItem, self.newitem)


class PrintShoppingList(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)

    def display_contents(self):
        self.text.insert(tkinter.END, "Shopping List\n")
        self.text.insert(tkinter.END, "=============\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Type p then enter to print. Press ESC to go back.\n")
        self.text.insert(tkinter.END, "\n")
        for item in db.models.StockItem.objects.all():
            levelchanges = list(item.levelchange_set.all().order_by('date'))
            levelchanges_pos = [c for c in levelchanges if c.change > 0]
            levelchanges_neg = [c for c in levelchanges if c.change < 0]
            if len(levelchanges_neg) == 0:
                continue
            levelchanges_neg_recent = [c for c in levelchanges_neg if len(levelchanges_pos) == 0 or c.date > levelchanges_pos[-1].date]
            if len(levelchanges_neg_recent) == 0:
                continue
            self.text.insert(tkinter.END, "{:14}".format(item.barcode), 'stockitem')
            self.text.insert(tkinter.END, "  ")
            self.text.insert(tkinter.END, "{:3}".format(-sum([c.change for c in levelchanges_neg_recent])))
            self.text.insert(tkinter.END, " x  ")
            self.text.insert(tkinter.END, item)
            self.text.insert(tkinter.END, " (")
            self.text.insert(tkinter.END, sum([c.change for c in levelchanges]))
            self.text.insert(tkinter.END, ")")
            self.text.insert(tkinter.END, "\n")

    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'p':
            subprocess.Popen(['lpr'], stdin=subprocess.PIPE).communicate(self.text.get("1.0", tkinter.END).encode('ascii'))
            return
        super().text_search(s)


class Application(TextApplication):
    window_title = "ShoppingList"
    icon_file = 'icon.png'
    default_display = Home

    def stock_item_link_handler(self, text):
        stockitem = db.models.StockItem.objects.get(barcode=text)
        self.displaynavigation.navigate(DisplayStockItem, stockitem)

    def __init__(self):
        super().__init__()
        self.configure_link('stockitem', self.stock_item_link_handler)


if __name__ == "__main__":
    Application().mainloop()
