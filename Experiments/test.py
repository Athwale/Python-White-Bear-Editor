#!/usr/bin/python3
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

        # Layout
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self._text = Gtk.TextView()
        self._buffer = self._text.get_buffer()

        text_scrolled = Gtk.ScrolledWindow()
        text_scrolled.set_size_request(200, -1)
        text_scrolled.add(self._text)

        for name in ['Bold', 'Color 1', 'Color 2']:
            button = Gtk.Button()
            button.set_label(name)
            button.set_size_request(200, -1)
            button.connect("clicked", self.on_button_clicked)
            v_box.add(button)

        h_box.add(text_scrolled)
        h_box.add(v_box)
        self.add(h_box)
        self.set_size_request(width=400, height=400)
        self.set_border_width(3)

        # Requires yum install hunspell-cs
        spellchecker = SpellChecker(self._text, language='cs_CZ', collapse=False)
        self._write_text()

    def on_button_clicked(self, button: Gtk.Button):
        print(button.get_label())

    def _write_text(self):
        self._buffer.set_text('test')


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(application_id="org.example.myapp", **kwargs)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self, title="Text test")
            # Shows all widgets inside the window.
            self.window.show_all()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
