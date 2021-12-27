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

    # Style limits:
    # H3/4 can only have one color.
    # H3/4 can not be mixed with other styles.
    # H3/$ can not contain urls.
    # H3/4 can not be bold twice.

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
        text_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        text_scrolled.set_size_request(300, -1)
        text_scrolled.add(self._text)

        for name in ['Bold', 'Red', 'Green', 'Orange']:
            button = Gtk.Button()
            button.set_label(name)
            button.set_size_request(200, -1)
            button.connect("clicked", self.on_button_clicked)
            v_box.add(button)

        v_box.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

        for name in ['h3', 'h4', 'Paragraph', 'List']:
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

        # Text effects:
        # Colors:
        self._buffer.create_tag("red_fg", foreground="red")
        self._buffer.create_tag("green_fg", foreground="green")
        self._buffer.create_tag("orange_fg", foreground="orange")
        # TODO Url can be clickable???
        # Weights:
        self._buffer.create_tag("bold", weight=Pango.Weight.BOLD)

        # Font sizes:
        self._buffer.create_tag("h3", scale=2)
        self._buffer.create_tag("h4", scale=1.5)
        self._buffer.create_tag("paragraph", scale=1)
        self._buffer.create_tag("list", scale=1)

        self._write_test_text()

    def on_button_clicked(self, button: Gtk.Button):
        button_id = button.get_label()
        start_iter: Gtk.TextIter = self._buffer.get_start_iter()
        print(start_iter.get_tags())

        if button_id == 'h3':
            self._apply_h_style('h3')
        elif button_id == 'h4':
            self._apply_h_style('h4')

        if self._buffer.get_has_selection():
            start, end = self._buffer.get_selection_bounds()
            # todo remove only color tags, eventually remove only a selection of tags based on what style is chosen.
            if button_id == 'Red':
                self._buffer.apply_tag_by_name('red_fg', start, end)
            elif button_id == 'Green':
                self._buffer.apply_tag_by_name('green_fg', start, end)
            elif button_id == 'Orange':
                self._buffer.apply_tag_by_name('orange_fg', start, end)
            elif button_id == 'Bold':
                self._buffer.apply_tag_by_name('bold', start, end)
            elif button_id == 'Paragraph':
                self._buffer.apply_tag_by_name('paragraph', start, end)
            elif button_id == 'List':
                self._buffer.apply_tag_by_name('list', start, end)

    def _apply_h_style(self, style: str) -> None:
        """
        Applies h3/4 style to the selected test or begins the style if nothing is selected.
        :param style: One of the defined style tags (h3, h4)
        :return: None
        """
        start: Gtk.TextIter
        end: Gtk.TextIter
        if self._buffer.get_has_selection():
            start, end = self._buffer.get_selection_bounds()
        else:
            insertion_point: Gtk.TextIter = self._buffer.get_iter_at_mark(self._buffer.get_insert())
            start = end = insertion_point

        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_iter_start: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end.forward_to_line_end()

            # Remove all other styles, titles do not keep anything.
            self._buffer.remove_all_tags(line_iter_start, line_iter_end)
            # A title is a larger and bold font.
            self._buffer.apply_tag_by_name(style, line_iter_start, line_iter_end)
            self._buffer.apply_tag_by_name('bold', line_iter_start, line_iter_end)

    def _write_test_text(self):
        for i in range(3):
            text = 'Line: {} Lorem ipsum dolor sit amet, consent additional elite, ' \
                   'sed do esmeralda temporary incidental ut labor\n'.format(i)
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
