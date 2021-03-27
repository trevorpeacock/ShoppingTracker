import db_setup
import db.models
import tkinter
import tkinter.font
import os
import datetime
import decimal
import traceback
import subprocess


def click_text(event, tag):
    # get the index of the mouse click
    index = event.widget.index("@%s,%s" % (event.x, event.y))

    # get the indices of all "adj" tags
    tag_indices = list(event.widget.tag_ranges(tag))

    # iterate them pairwise (start and end index)
    for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
        # check if the tag matches the mouse click index
        if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
            # return string between tag start and end
            return start, end, event.widget.get(start, end)


def show_hand_cursor(a):
    a.widget.config(cursor="hand2")


def hide_hand_cursor(a):
    a.widget.config(cursor='')


class KeyInputHandler(object):
    def __init__(self, root, displayhandler):
        super().__init__()
        self.root = root
        self.input_text = root.input_text
        self.displayhandler = displayhandler
        self.search_string = ''

    def update_search_text(self):
        self.input_text['state'] = tkinter.NORMAL
        self.input_text.delete('1.0', tkinter.END)
        self.input_text.insert(tkinter.END, self.search_string)
        self.input_text['state'] = tkinter.DISABLED

    def update_search_string(self, s):
        # We don't want to slow down key handling during barcode scanning
        # If an update is required, set a timer and handle it later to allow more input
        self.root.trigger_search_update_timer()
        self.search_string = s

    def keypress(self, e):
        if e.state & 0x0001: # Shift
            pass
        if e.state & 0x0002: # Caps Lock
            pass
        if e.state & 0x0004: # Control
            if e.keysym == 'v':
                #self.update_search_string(self.root.search_string + self.root.clipboard_get())
                return
            if e.keysym == 'c':
                #self.root.clipboard_clear()
                #self.root.clipboard_append(self.text.selection_get())
                #self.root.text.selection_clear()
                return
            return
        if e.state & 0x0008: # Left Alt
            return
        if e.state & 0x0010: # Numlock
            pass
        if e.state & 0x0080: # Right Alt
            return
        if e.state & 0x0100: # Mouse 1
            return
        if e.state & 0x0200: # Mouse 2
            return
        if e.state & 0x0400: # Mouse 3
            return

        if e.keysym == 'Up':
            self.displayhandler.char_press_up()
            return
        if e.keysym == 'Down':
            self.displayhandler.char_press_down()
            return
        if e.keysym == 'Left':
            self.displayhandler.char_press_left()
            return
        if e.keysym == 'Right':
            self.displayhandler.char_press_right()
            return
        if e.keysym == 'Prior':
            self.displayhandler.char_press_pgup()
            return
        if e.keysym == 'Next':
            self.displayhandler.char_press_pgdown()
            return

        if e.keycode == 22: # backspace
            self.update_search_string(self.search_string[:-1])
            return
        if e.keycode == 9: # escape
            if self.search_string == '':
                if len(self.root.nav_history) > 1:
                    self.displayhandler.navigate_back()
                    return
            self.update_search_string('')
            return
        if e.char == '\r':
            self.displayhandler.text_search(self.search_string)
            self.update_search_string('')
            return

        if e.char != '':
            self.update_search_string(self.search_string + e.char)
            return
        print(e)

class DisplayHandlerBase(object):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.text = root.text
        self.run_new()
        self.input_handler = KeyInputHandler(self.root, self)

    def navigate(self, cls, *k, **kk):
        self.root.navigate(cls, *k, **kk)

    def navigate_replace(self, cls, *k, **kk):
        self.run_exit()
        self.root.nav_history.pop()
        self.root.navigate(cls, *k, **kk)

    def navigate_back(self):
        self.run_exit()
        self.root.nav_history.pop()
        nav = self.root.nav_history[-1]
        nav.run_return()
        nav.display()

    def run_new(self):
        pass

    def run_return(self):
        pass

    def run_exit(self):
        pass

    def display_contents(self):
        self.text.insert(tkinter.END, "Not implemented!")

    def display(self):
        self.text['state'] = tkinter.NORMAL
        self.text.delete('1.0', tkinter.END)

        self.display_contents()

        self.text['state'] = tkinter.DISABLED

    def text_search(self, s):
        raise NotImplementedError("Not Implemented")

    def char_press_up(self):
        self.text.yview_scroll(-1, 'units')

    def char_press_down(self):
        self.text.yview_scroll(1, 'units')

    def char_press_left(self):
        self.text.xview_scroll(-1, 'page')

    def char_press_right(self):
        self.text.xview_scroll(1, 'page')

    def char_press_pgup(self):
        self.text.yview_scroll(-1, 'page')

    def char_press_pgdown(self):
        self.text.yview_scroll(1, 'page')

    def char_press(self, e):
        self.input_handler.keypress(e)

    def clipboard_search(self, clipboard):
        pass#self.text_search(clipboard)

    def update_search_text(self):
        self.input_handler.update_search_text()

class DisplayHandler(DisplayHandlerBase):
    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'q':
            self.navigate(Quit)
            return

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


class Quit(DisplayHandler):
    def display_contents(self):
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Are you sure you want to quit?\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, "Press y or n then enter.\n")

    def text_search(self, s):
        s = s.strip()
        if s.lower() == 'y':
            self.root.on_closing()
            return
        if s.lower() == 'n':
            self.navigate_back()
            return


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
            self.text.insert(tkinter.END, "{:10}".format(item.barcode), 'stockitem')
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
                self.text.insert(tkinter.END, "{:10}".format(item.barcode), 'stockitem')
                self.text.insert(tkinter.END, "  ")
                self.text.insert(tkinter.END, item)
                self.text.insert(tkinter.END, "\n")


class SearchStock(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)

    def display_contents(self):
        self.text.insert(tkinter.END, "Type something to search, and press enter, or scan an item.\n")
        self.text.insert(tkinter.END, "Press ESC to cancel.\n")

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

    def display_contents(self):
        self.text.insert(tkinter.END, "New Item Details\n")
        self.text.insert(tkinter.END, "================\n")
        self.text.insert(tkinter.END, "\n")
        if self.step == 1:
            self.text.insert(tkinter.END, "Enter name of new item\n")
        self.text.insert(tkinter.END, "\n")
        self.text.insert(tkinter.END, f"Barcode: {self.stockitem.barcode}\n")
        self.text.insert(tkinter.END, f"Name:    {self.stockitem.name}\n")

    def text_search(self, s):
        if self.step == 1:
            self.stockitem.name = s.strip()
            self.stockitem.save()
            self.navigate_back()


class AddStock(DisplayHandler):
    def __init__(self, root):
        super().__init__(root)
        self.list = {}
        self.newitem = None

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

    def run_exit(self):
        for item, quantity in self.list.items():
            change = db.models.LevelChange()
            change.item = item
            change.change = quantity
            change.save()

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
            stockitem = db.models.StockItem()
            stockitem.barcode = s.lower()
            subprocess.call(['play', 'bell.wav'])
            self.newitem = stockitem
            self.navigate(NewStockItem, stockitem)


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
            if len(levelchanges_pos) == 0 or len(levelchanges_neg) == 0:
                continue
            levelchanges_neg_recent = [c for c in levelchanges_neg if c.date > levelchanges_pos[-1].date]
            if len(levelchanges_neg_recent) == 0:
                continue
            self.text.insert(tkinter.END, "{:10}".format(item.barcode), 'stockitem')
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

class Root(tkinter.Tk):

    def __init__(self):
        super().__init__()

        #self.search_string = ''
        self.search_update_timer_set = False
        self.last_clipboard_contents = ''
        self.nav_history = []

        self.title("Parts DB")
        self.iconphoto(False, tkinter.PhotoImage(file='icon.png'))
        self.minsize(700, 500)
        if os.path.exists('window'):
            with open('window') as w:
                self.geometry(w.read())
        else:
            self.geometry('1100x900')

        font = tkinter.font.Font(self, family='Courier', size=12, weight='normal')
        font_bold = tkinter.font.Font(self, family='Courier', size=12, weight='bold')
        font_underline = tkinter.font.Font(self, family='Courier', size=12, weight='normal', underline = True)

        scroll = tkinter.Scrollbar(self)
        scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.text = tkinter.Text(self, yscrollcommand=scroll.set, wrap='none')
        self.text.configure(font=font)

        self.text.tag_configure('underline', font=font_underline)

        self.text.tag_configure('stockitem', font=font_bold)
        self.text.tag_bind("stockitem", "<Enter>", show_hand_cursor)
        self.text.tag_bind("stockitem", "<Leave>", hide_hand_cursor)
        self.text.tag_bind('stockitem', '<1>', self.open_stockitem)

        """self.text.tag_configure('location', font=font_bold)
        self.text.tag_bind("location", "<Enter>", show_hand_cursor)
        self.text.tag_bind("location", "<Leave>", hide_hand_cursor)
        self.text.tag_bind('location', '<1>', self.open_location)

        self.text.tag_configure('invoiceno', font=font_bold)
        self.text.tag_bind("invoiceno", "<Enter>", show_hand_cursor)
        self.text.tag_bind("invoiceno", "<Leave>", hide_hand_cursor)
        self.text.tag_bind('invoiceno', '<1>', self.open_invoice)

        self.text.tag_configure('part', font=font_bold)
        self.text.tag_bind("part", "<Enter>", show_hand_cursor)
        self.text.tag_bind("part", "<Leave>", hide_hand_cursor)
        self.text.tag_bind('part', '<1>', self.open_part)

        self.text.tag_configure('supplierpart', font=font_bold)
        self.text.tag_bind("supplierpart", "<Enter>", show_hand_cursor)
        self.text.tag_bind("supplierpart", "<Leave>", hide_hand_cursor)
        self.text.tag_bind('supplierpart', '<1>', self.open_supplierpart)

        self.text.tag_configure('manufacturerpart', font=font_bold)
        self.text.tag_bind("manufacturerpart", "<Enter>", show_hand_cursor)
        self.text.tag_bind("manufacturerpart", "<Leave>", hide_hand_cursor)
        self.text.tag_bind('manufacturerpart', '<1>', self.open_manufacturerpart)"""

        self.text.pack(fill='both', expand=True)
        self.text['state'] = tkinter.DISABLED

        #self.search_label_string = tkinter.StringVar()
        #self.search_label = tkinter.Label(self, textvariable=self.search_label_string)
        #self.search_label.pack()

        self.input_text = tkinter.Text(self, wrap='none', height=1, bg='Black', fg='White')
        self.input_text.configure(font=font)
        self.input_text.pack(fill='both', expand=False)
        #self.input_text.pack()

        self.input_text['state'] = tkinter.NORMAL
        self.input_text.delete('1.0', tkinter.END)
        self.input_text.insert(tkinter.END, "hi")
        self.input_text['state'] = tkinter.DISABLED

        self.bind("<KeyPress>", self.char_press)

        self.navigate(Home)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<FocusIn>", self.handle_focus)

        tkinter.Tk.report_callback_exception = self.show_error

    def char_press(self, e):
        self.nav_history[-1].char_press(e)

    def navigate(self, cls, *k, **kk):
        obj = cls(self, *k, **kk)
        self.nav_history.append(obj)
        obj.display()

    def on_closing(self):
        while len(self.nav_history)>1:
            self.nav_history[-1].run_exit()
            self.nav_history.pop()
            self.nav_history[-1].run_return()
        self.nav_history[0].run_exit()

        self.destroy()

    def handle_focus(self, e):
        clipboard = self.clipboard_get()
        if clipboard != self.last_clipboard_contents:
            self.last_clipboard_contents = clipboard
            self.nav_history[-1].clipboard_search(clipboard)

    def show_error(self, *args):
        err = traceback.format_exception(*args)
        print(''.join(err))

    def trigger_search_update_timer(self):
        if not self.search_update_timer_set:
            self.search_update_timer_set = True
            self.after(50, self.search_update_timer)

    def search_update_timer(self):
        self.search_update_timer_set = False
        self.nav_history[-1].update_search_text()
        #self.search_label_string.set(self.search_string)

    def open_stockitem(self, k):
        stockitem = click_text(k, 'stockitem')[2].strip()
        stockitem = db.models.StockItem.objects.get(barcode=stockitem)
        self.navigate(DisplayStockItem, stockitem)

    """

    def open_location(self, k):
        self.navigate(LocationItem, tuple(click_text(k, 'location')[2].split(' > ')))

    def open_invoice(self, k):
        self.navigate(InvoiceHandler, click_text(k, 'invoiceno')[2])

    def open_part(self, k):
        pn = click_text(k, 'part')[2].replace(' ', '')
        index = db.StockPartList.init().indexes['Internal PN']
        self.navigate(PartHandler, index[pn])

    def open_supplierpart(self, k):
        pn = tuple(click_text(k, 'supplierpart')[2].split(':', 1))
        index = db.SupplierPartList.init().indexes['OrderCode']
        self.navigate(PartHandler, index[pn])

    def open_manufacturerpart(self, k):
        pn = tuple(click_text(k, 'manufacturerpart')[2].split(':', 1))
        index = db.StockPartList.init().indexes['MPN']
        self.navigate(PartHandler, index[pn])
"""


if __name__ == "__main__":
    Root().mainloop()
