import tkinter
from input import *


class DisplayHandlerBase(object):
    def __init__(self, displaynavigation):
        super().__init__()
        self.displaynavigation = displaynavigation
        self.text = displaynavigation.display_text
        self.input_handler = None

    key_input_handler_class = KeyInputHandler

    def create_input_handler(self):
        self.input_handler = self.key_input_handler_class(self.displaynavigation, self)

    def run_leave(self):
        pass

    def run_return(self):
        self.display()
        self.input_handler.update_search_text()

    def run_new(self):
        self.create_input_handler()
        self.input_handler.update_search_text()
        self.display()

    def run_exit(self):
        pass

    def navigate(self, cls, *k, **kk):
        self.displaynavigation.navigate(cls, *k, **kk)

    def navigate_replace(self, cls, *k, **kk):
        self.displaynavigation.navigate_replace(cls, *k, **kk)

    def navigate_back(self):
        self.displaynavigation.navigate_back()

    def display_contents(self):
        self.text.insert(tkinter.END, "Not implemented!")

    def display(self):
        self.text['state'] = tkinter.NORMAL
        self.text.delete('1.0', tkinter.END)
        self.display_contents()
        self.text['state'] = tkinter.DISABLED

    def text_search(self, s):
        raise NotImplementedError("Not Implemented")

    def process_barcode(self, barcode):
        self.text_search(barcode)

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
            self.displaynavigation.root.on_closing()
            return
        if s.lower() == 'n':
            self.navigate_back()
            return


class DisplayError(DisplayHandler):
    def __init__(self, displaynavigation, err):
        super().__init__(displaynavigation)
        self.err = err

    def display_contents(self):
        self.text.insert(tkinter.END, "ERROR\n")
        self.text.insert(tkinter.END, "=====\n")
        self.text.insert(tkinter.END, "\n")
        for l in self.err.split('\n'):
            self.text.insert(tkinter.END, l)
            self.text.insert(tkinter.END, "\n")
