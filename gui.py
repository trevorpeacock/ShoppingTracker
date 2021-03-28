import tkinter
import tkinter.font
import os
import traceback
from navigation import *
from input import *
from display import *


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


class TextApplication(tkinter.Tk):

    window_title = "Untitled"
    icon_file = None
    default_display = None

    def link_click_handler(self, name, event):
        text = click_text(event, name)[2].strip()
        self.link_handlers[name](text)

    def configure_link(self, name, handler, **styles):
        self.text.tag_configure(name, **styles)
        self.text.tag_bind(name, "<Enter>", show_hand_cursor)
        self.text.tag_bind(name, "<Leave>", hide_hand_cursor)
        self.link_handlers[name] = handler
        self.text.tag_bind(name, '<1>', lambda event: self.link_click_handler(name, event))


    def __init__(self):
        super().__init__()

        self.search_update_timer_set = False
        self.last_clipboard_contents = ''
        self.link_handlers = {}

        self.title(self.window_title)
        if self.icon_file:
            self.iconphoto(False, tkinter.PhotoImage(file=self.icon_file))
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

        self.text.tag_configure('text_input', background='Black', foreground='White')
        self.text.tag_configure('text_input_active', background='DarkBlue', foreground='White')

        self.text.pack(fill='both', expand=True)
        self.text['state'] = tkinter.DISABLED

        self.input_text = tkinter.Text(self, wrap='none', height=1, bg='Black', fg='White')
        self.input_text.configure(font=font)
        self.input_text.pack(fill='both', expand=False)

        self.input_text['state'] = tkinter.NORMAL
        self.input_text.delete('1.0', tkinter.END)
        self.input_text.insert(tkinter.END, "")
        self.input_text['state'] = tkinter.DISABLED

        self.blink_input_cursor1()

        self.bind("<KeyPress>", self.char_press)

        self.displaynavigation = DisplayNavigationManager(self)
        if self.default_display:
            self.displaynavigation.navigate(self.default_display)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<FocusIn>", self.handle_focus)

        tkinter.Tk.report_callback_exception = self.show_error

    def char_press(self, e):
        self.displaynavigation.char_press(e)

    def on_closing(self):
        self.displaynavigation.exit_all()
        self.destroy()

    def handle_focus(self, e):
        clipboard = self.clipboard_get()
        if clipboard != self.last_clipboard_contents:
            self.last_clipboard_contents = clipboard
            self.displaynavigation.clipboard_search(clipboard)

    def show_error(self, *args):
        err = traceback.format_exception(*args)
        err = ''.join(err)
        print(err)
        self.displaynavigation.navigate_replace(DisplayError, err)

    def trigger_search_update_timer(self):
        if not self.search_update_timer_set:
            self.search_update_timer_set = True
            self.after(50, self.search_update_timer)

    def search_update_timer(self):
        self.search_update_timer_set = False
        self.displaynavigation.update_search_text()

    def blink_input_cursor1(self):
        self.text.tag_configure('text_input_cursor', background='DarkBlue', foreground='White')
        self.input_text.tag_configure('text_input_cursor', background='DarkBlue', foreground='White')
        self.after(200, self.blink_input_cursor2)

    def blink_input_cursor2(self):
        self.text.tag_configure('text_input_cursor', background='White', foreground='DarkBlue')
        self.input_text.tag_configure('text_input_cursor', background='White', foreground='DarkBlue')
        self.after(200, self.blink_input_cursor1)
