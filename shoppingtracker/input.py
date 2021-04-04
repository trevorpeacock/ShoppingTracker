import tkinter
import datetime


class BaseInputHandler(object):
    def __init__(self, displaynavigation, displayhandler):
        super().__init__()
        self.displaynavigation = displaynavigation
        self.input_text = displaynavigation.input_text
        self.displayhandler = displayhandler

    def navigate(self, cls, *k, **kk):
        self.displaynavigation.navigate(cls, *k, **kk)

    def navigate_replace(self, cls, *k, **kk):
        self.displaynavigation.navigate_replace(cls, *k, **kk)

    def navigate_back(self):
        self.displaynavigation.navigate_back()

    def update_search_text(self):
        self.input_text['state'] = tkinter.NORMAL
        self.input_text.delete('1.0', tkinter.END)
        self.display_search_text()
        self.input_text['state'] = tkinter.DISABLED

    def display_search_text(self):
        pass

    def char_press_up(self):
        self.displayhandler.char_press_up()

    def char_press_down(self):
        self.displayhandler.char_press_down()

    def char_press_left(self):
        self.displayhandler.char_press_left()

    def char_press_right(self):
        self.displayhandler.char_press_right()

    def char_press_pgup(self):
        self.displayhandler.char_press_pgup()

    def char_press_pgdown(self):
        self.displayhandler.char_press_pgdown()

    def char_press_home(self):
        pass

    def char_press_end(self):
        pass

    def char_press_backspace(self):
        pass

    def char_press_escape(self):
        self.navigate_back()

    def char_press_enter(self):
        pass

    def char_press_tab(self):
        pass

    def char_press_text(self, c):
        pass

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
            self.char_press_up()
            return
        if e.keysym == 'Down':
            self.char_press_down()
            return
        if e.keysym == 'Left':
            self.char_press_left()
            return
        if e.keysym == 'Right':
            self.char_press_right()
            return
        if e.keysym == 'Prior':
            self.char_press_pgup()
            return
        if e.keysym == 'Next':
            self.char_press_pgdown()
            return
        if e.keysym == 'Home':
            self.char_press_home()
            return
        if e.keysym == 'End':
            self.char_press_end()
            return

        if e.keycode == 22: # backspace
            self.char_press_backspace()
            return
        if e.keycode == 9: # escape
            self.char_press_escape()
            return
        if e.char == '\r':
            self.char_press_enter()
            return
        if e.char == '\t':
            self.char_press_tab()
            return

        if e.char != '':
            self.char_press_text(e.char)
            return
        print(e)


class BarcodeDetectionInputHandler(BaseInputHandler):

    barcode_char_max_interval = 10 # Milliseconds
    barcode_min_length = 8

    def __init__(self, displaynavigation, displayhandler):
        super().__init__(displaynavigation, displayhandler)
        self.keypress_queue = []
        self.keypress_queue_end = datetime.datetime.now()

    def process_keypress_queue(self):
        if len(self.keypress_queue) == 0:
            return
        # character is not a normal character (including enter and tab)
        if [e for e in self.keypress_queue if len(repr(e.char)) != 3 and e.char not in ['\t', '\r']]:
            #print('non barcode, dumping queue')
            while self.keypress_queue:
                super().keypress(self.keypress_queue.pop(0))
        if datetime.datetime.now() - self.keypress_queue_end < datetime.timedelta(milliseconds=self.barcode_char_max_interval):
            self.displaynavigation.root.after(self.barcode_char_max_interval, self.process_keypress_queue)
            return
        if len(self.keypress_queue) >= self.barcode_min_length and self.keypress_queue[-1].char in ['\t', '\r']:
            #print('BARCODE!')
            barcode = ''
            while self.keypress_queue:
                barcode += self.keypress_queue.pop(0).char
            self.process_barcode(barcode.strip())
        else:
            #print('too short, dumping queue')
            #print([e.char for e in self.keypress_queue])
            while self.keypress_queue:
                super().keypress(self.keypress_queue.pop(0))

    def process_barcode(self, barcode):
        self.displayhandler.process_barcode(barcode)

    def keypress(self, e):
        self.keypress_queue.append(e)
        self.keypress_queue_end = datetime.datetime.now()
        self.displaynavigation.root.after(10, self.process_keypress_queue)


class KeyInputHandler(BarcodeDetectionInputHandler):
    def char_press_text(self, c):
        self.displayhandler.text_search(c)

    def display_search_text(self):
        self.input_text.insert(tkinter.END, "COMMAND > ")
        self.input_text.insert(tkinter.END, " ", 'text_input_cursor')


class TypingInputHandler(KeyInputHandler):

    text_tag = 'text_input_active'

    def __init__(self, displaynavigation, displayhandler, length=20, text=""):
        super().__init__(displaynavigation, displayhandler)
        self.search_string = text
        self.cursor_pos = len(self.search_string)
        self.length = length

    def update_search_string(self, s=None):
        # We don't want to slow down key handling during barcode scanning
        # If an update is required, set a timer and handle it later to allow more input
        self.displaynavigation.root.trigger_search_update_timer()
        if s is not None:
            self.search_string = s

    def display_search_text(self):
        self.input_text.insert(tkinter.END, "INPUT > " + self.search_string)
        self.input_text.insert(tkinter.END, " ", 'text_input_cursor')

    def char_press_left(self):
        self.cursor_pos += -1
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        self.update_search_string()

    def char_press_right(self):
        self.cursor_pos += 1
        if self.cursor_pos > len(self.search_string):
            self.cursor_pos = len(self.search_string)
        self.update_search_string()

    def char_press_home(self):
        self.cursor_pos = 0
        self.update_search_string()

    def char_press_end(self):
        self.cursor_pos = len(self.search_string)
        self.update_search_string()

    def char_press_backspace(self):
        self.update_search_string(self.search_string[:self.cursor_pos-1] + self.search_string[self.cursor_pos:])
        self.char_press_left()

    def char_press_escape(self):
        if self.search_string != '':
            self.update_search_string('')
            self.cursor_pos = 0
        else:
            super().char_press_escape()

    def char_press_enter(self):
        self.displayhandler.text_search(self.search_string)
        self.update_search_string('')

    def char_press_text(self, c):
        if self.cursor_pos != self.length:
            if len(self.search_string) == self.length:
                return
            self.search_string = self.search_string[:self.cursor_pos] + c + self.search_string[self.cursor_pos:]
        else:
            self.search_string = self.search_string[:self.cursor_pos-1] + c
        self.search_string = self.search_string[:self.length]
        self.char_press_right()

    def display(self, text):
        s = "{{:{}}}".format(str(self.length)).format(self.search_string)
        if self.cursor_pos < self.length:
            text.insert(tkinter.END, s[:self.cursor_pos], self.text_tag)
            text.insert(tkinter.END, s[self.cursor_pos], 'text_input_cursor')
            text.insert(tkinter.END, s[self.cursor_pos+1:], self.text_tag)
        else:
            text.insert(tkinter.END, s[:self.cursor_pos-1], self.text_tag)
            text.insert(tkinter.END, s[self.cursor_pos-1], 'text_input_cursor')

    def update_search_text(self):
        super().update_search_text()
        self.displayhandler.display()


class SelectionInputHandler(KeyInputHandler):

    text_tag = 'text_input'

    def __init__(self, displaynavigation, displayhandler, length):
        super().__init__(displaynavigation, displayhandler)
        self.cursor_pos = 0
        self.length = length

    def update_search_string(self, s=None):
        # We don't want to slow down key handling during barcode scanning
        # If an update is required, set a timer and handle it later to allow more input
        self.displaynavigation.root.trigger_search_update_timer()

    def display_search_text(self):
        self.input_text.insert(tkinter.END, "SELECT {} / {}".format(self.cursor_pos + 1, self.length))

    def char_press_up(self):
        self.cursor_pos += -1
        if self.cursor_pos < 0:
            self.cursor_pos = self.length - 1
        self.update_search_string()

    def char_press_down(self):
        self.cursor_pos += 1
        if self.cursor_pos >= self.length:
            self.cursor_pos = 0
        self.update_search_string()

    def char_press_home(self):
        self.cursor_pos = 0
        self.update_search_string()

    def char_press_end(self):
        self.cursor_pos = self.length - 1
        self.update_search_string()

    def char_press_enter(self):
        self.displayhandler.text_search(str(self.cursor_pos))
        #self.update_search_string('')

    def update_search_text(self):
        super().update_search_text()
        self.displayhandler.display()
