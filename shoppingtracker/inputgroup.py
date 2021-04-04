from shoppingtracker.input import *


class InputGroup(BaseInputHandler):
    def __init__(self, displaynavigation, displayhandler):
        super().__init__(displaynavigation, displayhandler)
        self.input_handlers = []
        self.current_input_handler = 0
        self.text_tag = 'text_input'

    def add(self, inputhandler):
        self.input_handlers.append(inputhandler)
        self.input_handlers[self.current_input_handler].activate()
        return inputhandler

    def char_press_left(self):
        self.input_handlers[self.current_input_handler].char_press_left()

    def char_press_right(self):
        self.input_handlers[self.current_input_handler].char_press_right()

    def char_press_home(self):
        self.input_handlers[self.current_input_handler].char_press_home()

    def char_press_end(self):
        self.input_handlers[self.current_input_handler].char_press_end()

    def char_press_backspace(self):
        self.input_handlers[self.current_input_handler].char_press_backspace()

    def char_press_enter(self):
        self.char_press_down()

    def char_press_up(self):
        current_handler = self.input_handlers[self.current_input_handler]
        self.current_input_handler += -1
        if self.current_input_handler < 0:
            self.current_input_handler = len(self.input_handlers) - 1
        next_handler = self.input_handlers[self.current_input_handler]
        current_handler.deactivate()
        next_handler.activate()
        self.update_search_text()
        self.displayhandler.display()

    def char_press_down(self):
        current_handler = self.input_handlers[self.current_input_handler]
        self.current_input_handler += 1
        if self.current_input_handler >= len(self.input_handlers):
            self.current_input_handler = 0
        next_handler = self.input_handlers[self.current_input_handler]
        current_handler.deactivate()
        next_handler.activate()
        self.update_search_text()
        self.displayhandler.display()

    def char_press_text(self, c):
        self.input_handlers[self.current_input_handler].char_press_text(c)

    def update_search_text(self):
        self.input_handlers[self.current_input_handler].update_search_text()


class FocusableTypingInputHandler(TypingInputHandler):
    def __init__(self, displaynavigation, displayhandler, length=20, text=""):
        super().__init__(displaynavigation, displayhandler, length, text)
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def display_search_text(self):
        self.input_text.insert(tkinter.END, "INPUT > " + self.search_string)
        self.input_text.insert(tkinter.END, " ", 'text_input_cursor')

    def display(self, text):
        if not self.active:
            s = "{{:{}}}".format(str(self.length)).format(self.search_string)
            text.insert(tkinter.END, s, 'text_input')
        else:
            super().display(text)
