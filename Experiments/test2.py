#!/usr/bin/python3
import sys
from typing import Dict

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango


class Styles:
    STYLE_PAR: str = 'paragraph_style'
    STYLE_H3: str = 'heading3_style'
    STYLE_H4: str = 'heading4_style'
    STYLE_LIST: str = 'list_style'

    TAG_PAR: str = 'paragraph'
    TAG_H3: str = 'h3'
    TAG_H4: str = 'h4'
    TAG_LIST: str = 'list'
    TAG_BOLD: str = 'bold'

    COLORS: Dict[str, str] = {'red': 'rgb(255,0,0)', 'green': 'rgb(0,255,0)', 'orange': 'rgb(255,215,0)'}


class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Layout
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self._text_view = Gtk.TextView()
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        # self._text.set_pixels_inside_wrap(50)
        # self._text.set_indent(50)
        self._buffer: Gtk.TextBuffer = self._text_view.get_buffer()

        self._text_scrolled = Gtk.ScrolledWindow()
        self._text_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        self._text_scrolled.set_size_request(300, -1)
        self._text_scrolled.add(self._text_view)

        # Create text effect buttons:
        for color_name in Styles.COLORS.keys():
            button = Gtk.Button()
            button.set_label(color_name)
            button.set_size_request(200, -1)
            button.connect("clicked", self.on_button_clicked)
            v_box.add(button)

        v_box.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        button = Gtk.Button()
        button.set_label(Styles.TAG_BOLD)
        button.set_size_request(200, -1)
        button.connect("clicked", self.on_button_clicked)
        v_box.add(button)
        v_box.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

        # Create text style buttons:
        for name in ['h3', 'h4', 'Paragraph', 'List']:
            button = Gtk.Button()
            button.set_label(name)
            button.set_size_request(200, -1)
            button.connect("clicked", self.on_button_clicked)
            v_box.add(button)

        h_box.add(self._text_scrolled)
        h_box.add(v_box)
        self.add(h_box)
        self.set_size_request(width=400, height=550)
        self.set_border_width(3)

        # Requires yum install hunspell-cs
        # todo gtk text mark set visible is possible.
        #self._spellchecker = SpellChecker(self._text_view, language='cs_CZ', collapse=False)

        # Styles are combination of set tags.
        # Text effects:
        # Colors:
        for color_name, definition in Styles.COLORS.items():
            rgb = Gdk.RGBA()
            rgb.parse(definition)
            self._buffer.create_tag(color_name, foreground_rgba=rgb)
        # TODO Url can be clickable???
        # Weights:
        self._buffer.create_tag(Styles.TAG_BOLD, weight=Pango.Weight.BOLD)

        # Tag definitions:
        # TODO add line spacing to styles.
        self._buffer.create_tag(Styles.TAG_H3, scale=2, weight=Pango.Weight.BOLD)
        self._buffer.create_tag(Styles.TAG_H4, scale=1.5, weight=Pango.Weight.BOLD)
        self._buffer.create_tag(Styles.TAG_PAR, scale=1)
        # List style:
        self._buffer.create_tag(Styles.TAG_LIST, scale=1)
        self._write_test_text()

    def _write_test_text(self) -> None:
        """
        Write some test text into the text view.
        :return: None
        """
        for i in range(3):
            text = 'Line: {} Lorem ipsum dolor sit amet, consent additional elite, ' \
                   'sed do esmeralda temporary incidental ut labor\n'.format(i)
            mark = self._buffer.get_insert()
            text_iter = self._buffer.get_iter_at_mark(mark)
            self._buffer.insert(text_iter, text)

    def on_button_clicked(self, button: Gtk.Button) -> None:
        line_start = self._buffer.get_iter_at_line(0)
        anchor = self._buffer.create_child_anchor(line_start)

        bullet = Gtk.Label(label='•')
        bullet.set_size_request(30, 10)
        rgb = Gdk.RGBA()
        rgb.parse('rgb(255, 0, 0)')
        bullet.override_background_color(Gtk.StateFlags.NORMAL, rgb)

        self._text_view.add_child_at_anchor(bullet, anchor)
        self.show_all()


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
