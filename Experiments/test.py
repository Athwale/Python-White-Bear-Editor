#!/usr/bin/python3
import sys
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango
from gtkspellcheck import SpellChecker


class AppWindow(Gtk.ApplicationWindow):
    """
    Main class for all the work.
    """
    # Character counts are offsets
    # Byte counts are indexes.
    # Tags apply attributes to a range of text. Tags are inside a buffer tag table.
    # Text widget stores a set of global text attributes that can be changed for text ranges with tags.
    # Text iterator is a position between two characters. They are all invalidated any time the text changes.
    # Text marks are also positions between characters but they are updates when text changes.
    # Text tags set text attributes.
    # gtk_text_buffer_get_bounds can be used with gtk_text_buffer_get_slice to get whole contents with images.
    # Empty buffer, one with zero characters is considered to have a single line with no characters in it,
    # and in particular, no line separator at the end.
    # gtk_text_buffer_get_line_count, char count and display that in the bottom status bar.
    # Tags have priority that can solve conflicts.
    # https://askubuntu.com/questions/272446/pygtk-textbuffer-adding-tags-and-reading-text finding tags

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Layout
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self._text = Gtk.TextView()
        self._text.set_wrap_mode(Gtk.WrapMode.WORD)
        # self._text.set_pixels_inside_wrap(50)
        # todo lists using a decoration in margin???
        # self._text.set_indent(50)
        self._buffer: Gtk.TextBuffer = self._text.get_buffer()

        text_scrolled = Gtk.ScrolledWindow()
        text_scrolled.set_size_request(300, -1)
        text_scrolled.add(self._text)

        for name in ['Bold', 'Red', 'Green', 'Orange']:
            button = Gtk.Button()
            button.set_label(name)
            button.set_size_request(200, -1)
            button.connect("clicked", self.on_button_clicked)
            v_box.add(button)

        v_box.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

        for name in ['H3', 'H4', 'Paragraph', 'List']:
            button = Gtk.Button()
            button.set_label(name)
            button.set_size_request(200, -1)
            button.connect("clicked", self.on_button_clicked)
            v_box.add(button)

        h_box.add(text_scrolled)
        h_box.add(v_box)
        self.add(h_box)
        self.set_size_request(width=400, height=550)
        self.set_border_width(3)

        # Requires yum install hunspell-cs
        # todo gtk text mark set visible is possible.
        spellchecker = SpellChecker(self._text, language='cs_CZ', collapse=False)

        self._buffer.create_tag("red_fg", foreground="red")
        self._buffer.create_tag("green_fg", foreground="green")
        self._buffer.create_tag("orange_fg", foreground="orange")
        self._buffer.create_tag("bold", weight=Pango.Weight.BOLD)

        self._write_text()

    def on_button_clicked(self, button: Gtk.Button):
        start_iter: Gtk.TextIter = self._buffer.get_start_iter()
        print(start_iter.get_tags())
        if self._buffer.get_has_selection():
            start, end = self._buffer.get_selection_bounds()
            button_id = button.get_label()
            # todo remove only color tags, eventually remove only a selection of tags based on what style is chosen.
            # self._buffer.remove_all_tags(start, end)
            if button_id == 'Red':
                self._buffer.apply_tag_by_name('red_fg', start, end)
            elif button_id == 'Green':
                self._buffer.apply_tag_by_name('green_fg', start, end)
            elif button_id == 'Orange':
                self._buffer.apply_tag_by_name('orange_fg', start, end)
            elif button_id == 'Bold':
                self._buffer.apply_tag_by_name('bold', start, end)

    def _write_text(self):
        text = 'test test test test test test test test test test test test'
        mark = self._buffer.get_insert()
        text_iter = self._buffer.get_iter_at_mark(mark)
        self._buffer.insert(text_iter, text, len(text))
        

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
