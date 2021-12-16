#!/usr/bin/python3
import locale
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gtkspellcheck import SpellChecker


class AppWindow(Gtk.ApplicationWindow):
    """
    Main class for all the work.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text = Gtk.TextView()
        self.add(text)
        self.set_size_request(width=100, height=200)

        # Requires yum install hunspell-cs
        spellchecker = SpellChecker(text, language='cs_CZ', collapse=False)

    def on_destroy(self, widget, extra_arg):
        print(widget)


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(application_id="org.example.myapp", **kwargs)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self, title="Main Window")
            # Shows all widgets inside the window.
            self.window.show_all()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
