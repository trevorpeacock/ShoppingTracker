#!/usr/bin/env python3

import shoppingtracker.db_setup
import shoppingtracker.db.models
import tkinter
import tkinter.font
import os
import datetime
import decimal
import traceback
import subprocess
from shoppingtracker.navigation import *
from shoppingtracker.input import *
from shoppingtracker.inputgroup import *
from shoppingtracker.display import *
from shoppingtracker.gui import TextApplication
from shoppingtracker.lookup_barcode import lookup_item_online
import shoppingtracker.settings


bell_file = os.path.join(os.path.dirname(__file__), 'bell.wav')
woosh_file = os.path.join(os.path.dirname(__file__), 'woosh.wav')


class Home(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)
        self.newitem = None

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

    def run_return(self):
        if self.newitem and self.newitem.id:
            change = shoppingtracker.db.models.LevelChange()
            change.item = self.newitem
            change.change = -1
            change.save()
        self.newitem = None
        super().run_return()

    def process_barcode(self, barcode):
        try:
            stockitem = shoppingtracker.db.models.StockItem.objects.get(barcode=barcode.lower())
            subprocess.call(['play', woosh_file])
            change = shoppingtracker.db.models.LevelChange()
            change.item = stockitem
            change.change = -1
            change.save()
        except shoppingtracker.db.models.StockItem.DoesNotExist:
            self.newitem = shoppingtracker.db.models.StockItem()
            self.newitem.barcode = barcode.lower()
            self.navigate(LookupNewStockItem, self.newitem)


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
        super().text_search(s)


class ListStock(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)
        self.list = list(shoppingtracker.db.models.StockItem.objects.all().order_by('name'))

    key_input_handler_class = SelectionInputHandler

    def run_new(self):
        self.list = list(shoppingtracker.db.models.StockItem.objects.all().order_by('name'))
        super().run_new()

    def run_return(self):
        self.list = list(shoppingtracker.db.models.StockItem.objects.all().order_by('name'))
        super().run_return()

    def create_input_handler(self):
        self.input_handler = self.key_input_handler_class(self.displaynavigation, self, len(self.list))

    def display_contents(self):
        self.text.insert(tkinter.END, "Pantry List\n")
        self.text.insert(tkinter.END, "===========\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Press ESC to go back or click on an item to view details\n")
        self.text.insert(tkinter.END, "\n")
        for pos, item in enumerate(self.list):
            self.text.insert(tkinter.END, "   ")
            if self.input_handler.cursor_pos == pos:
                self.text.insert(tkinter.END, "{:14}".format(item.barcode), ['stockitem', 'text_input'])
            else:
                self.text.insert(tkinter.END, "{:14}".format(item.barcode), 'stockitem')
            self.text.insert(tkinter.END, "  ")
            self.text.insert(tkinter.END, "{:3}".format(sum([c.change for c in item.levelchange_set.all()])))
            self.text.insert(tkinter.END, " x  ")
            self.text.insert(tkinter.END, item)
            self.text.insert(tkinter.END, "\n")

    def text_search(self, s):
        if s.isdigit():
            self.navigate(DisplayStockItem, self.list[int(s)])
            return
        super().text_search(s)

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
        for item in shoppingtracker.db.models.StockItem.objects.all():
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
            stockitem = shoppingtracker.db.models.StockItem.objects.get(barcode=s.lower())
            self.navigate_replace(DisplayStockItem, stockitem)
            return
        except shoppingtracker.db.models.StockItem.DoesNotExist:
            pass
        if s.strip() == '':
            return
        self.navigate_replace(SearchStockResults, s.strip().lower())
        return


class DeleteStockItem(DisplayHandler):
    def __init__(self, root, stockitem):
        super().__init__(root)
        self.stockitem = stockitem

    def display_contents(self):
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Are you sure you want to delete {}?\n".format(self.stockitem.name))
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Press y or n then enter.\n")

    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'y':
            self.stockitem.levelchange_set.all().delete()
            self.stockitem.delete()
            self.navigate_back()
            return
        if s.lower() == 'n':
            self.navigate_replace(DisplayStockItem, self.stockitem)
            return


class DisplayStockItem(DisplayHandler):
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

    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'e':
            self.navigate(NewStockItem, self.stockitem)
            return
        if s.lower() == 'd':
            self.navigate_replace(DeleteStockItem, self.stockitem)
            return
        super().text_search(s)


class NewStockItem(DisplayHandler):
    def __init__(self, root, stockitem):
        super().__init__(root)
        self.stockitem = stockitem
        self.step = 1

    key_input_handler_class = InputGroup

    def create_input_handler(self):
        self.input_handler = self.key_input_handler_class(self.displaynavigation, self)
        self.name_input = self.input_handler.add(FocusableTypingInputHandler(self.displaynavigation, self, 100, self.stockitem.name))
        self.brand_input = self.input_handler.add(FocusableTypingInputHandler(self.displaynavigation, self, 100, self.stockitem.brand))

    def run_exit(self):
        self.stockitem.name = self.name_input.search_string
        self.stockitem.brand = self.brand_input.search_string
        self.stockitem.save()

    def display_contents(self):
        self.text.insert(tkinter.END, "New Item Details\n")
        self.text.insert(tkinter.END, "================\n")
        self.text.insert(tkinter.END, "\n")
        if self.step == 1:
            self.text.insert(tkinter.END, "Enter name of new item\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, f"Barcode: {self.stockitem.barcode}\n")
        self.text.insert(tkinter.END, f"Name:    ")
        self.name_input.display(self.text)
        self.text.insert(tkinter.END, f"\n")
        self.text.insert(tkinter.END, f"Brand:   ")
        self.brand_input.display(self.text)
        self.text.insert(tkinter.END, f"\n")


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
        subprocess.call(['play', bell_file])
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
            change = shoppingtracker.db.models.LevelChange()
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
            stockitem = shoppingtracker.db.models.StockItem.objects.get(barcode=s.lower())
            self.add_item(stockitem)
            self.display()
        except shoppingtracker.db.models.StockItem.DoesNotExist:
            self.newitem = shoppingtracker.db.models.StockItem()
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
        for item in shoppingtracker.db.models.StockItem.objects.all():
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
    icon_file = os.path.join(os.path.dirname(__file__), 'icon.png')
    default_display = Home
    window_position_file = shoppingtracker.settings.DATA_DIR / 'window'

    def stock_item_link_handler(self, text):
        stockitem = shoppingtracker.db.models.StockItem.objects.get(barcode=text)
        self.displaynavigation.navigate(DisplayStockItem, stockitem)

    def __init__(self):
        super().__init__()
        self.configure_link('stockitem', self.stock_item_link_handler)


if __name__ == "__main__":
    Application().mainloop()
