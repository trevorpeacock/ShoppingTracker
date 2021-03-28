

class DisplayNavigationManager(object):
    # TODO: Auto timeout, return to home
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.display_text = root.text
        self.input_text = root.input_text
        self.nav_history = []

    def update_search_text(self):
        self.nav_history[-1].update_search_text()

    def clipboard_search(self, clipboard):
        self.nav_history[-1].clipboard_search(clipboard)

    def exit_all(self):
        while len(self.nav_history)>1:
            self.nav_history[-1].run_exit()
            self.nav_history.pop()
            self.nav_history[-1].run_return()
        self.nav_history[0].run_exit()

    def _navigate(self, cls, *k, **kk):
        obj = cls(self, *k, **kk)
        self.nav_history.append(obj)
        obj.run_new()

    def navigate(self, cls, *k, **kk):
        if self.nav_history:
            self.nav_history[-1].run_leave()
        self._navigate(cls, *k, **kk)

    def navigate_replace(self, cls, *k, **kk):
        self.nav_history[-1].run_exit()
        self.nav_history.pop()
        self._navigate(cls, *k, **kk)

    def navigate_back(self):
        if len(self.nav_history) <= 1:
            return
        self.nav_history[-1].run_exit()
        self.nav_history.pop()
        nav = self.nav_history[-1]
        nav.run_return()

    def char_press(self, e):
        self.nav_history[-1].char_press(e)
