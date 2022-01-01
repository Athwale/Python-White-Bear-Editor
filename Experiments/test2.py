#!/usr/bin/python3
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_size_request(250, 200)

        textview: Gtk.TextView = Gtk.TextView()
        buffer: Gtk.TextBuffer = textview.get_buffer()
        text = "Sample text"
        buffer.set_text(text)

        line_start = buffer.get_iter_at_line(0)
        anchor = buffer.create_child_anchor(line_start)
        bullet = Gtk.Label(label='\t•\t')
        textview.add_child_at_anchor(bullet, anchor)

        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.add(textview)
        scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)

        self.add(scrolled_win)


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.example.myapp", **kwargs)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self, title="Child Widgets")
            self.window.show_all()
            self.window.present()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
