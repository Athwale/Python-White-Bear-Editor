#!/usr/bin/python3
import sys
from typing import Dict

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango
from gtkspellcheck import SpellChecker
from gi.repository import Gdk


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
    """
    Main class for all the work.
    """
    # TODO when this is done post it to stack exchange as an example and hope for betterment.
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

    # Paragraph can not be mixed with other styles.
    # Paragraph retains text color and boldness.

    # List must automatically continue on a new line.

    # Urls ignore bold and color change.

    # TODO styles must combine when deleted/backspaced together.

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
        self._spellchecker = SpellChecker(self._text_view, language='cs_CZ', collapse=False)

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
        """
        Style buttons handler.
        :param button: The button that was pressed.
        :return: None
        """
        # TODO Carry the style in the button for all in some way.
        button_id = button.get_label()
        if button_id == 'h3':
            self._apply_style(Styles.STYLE_H3)
        elif button_id == 'h4':
            self._apply_style(Styles.STYLE_H4)
        elif button_id == 'Paragraph':
            self._apply_style(Styles.STYLE_PAR)
        elif button_id == 'List':
            self._apply_style(Styles.STYLE_LIST)
        elif button_id in Styles.COLORS.keys():
            self._apply_style(button_id)
        elif button_id == 'bold':
            self._apply_style(Styles.TAG_BOLD)
        self._text_view.grab_focus()

    def _apply_style(self, style: str) -> None:
        """
        Applies the style on either a selection or current paragraph.
        :param style: Style name from Styles class.
        :return: None
        """
        start: Gtk.TextIter
        end: Gtk.TextIter
        if self._buffer.get_has_selection():
            start, end = self._buffer.get_selection_bounds()
        else:
            # TODO starting s style without a selection does not seem to work yet.
            insertion_point: Gtk.TextIter = self._buffer.get_iter_at_mark(self._buffer.get_insert())
            start = end = insertion_point
        if style == Styles.STYLE_H3:
            self._apply_h_style(Styles.TAG_H3, start, end)
        elif style == Styles.STYLE_H4:
            self._apply_h_style(Styles.TAG_H4, start, end)
        elif style == Styles.STYLE_PAR:
            self._apply_paragraph_style(start, end)
        elif style == Styles.STYLE_LIST:
            self._apply_list_style(start, end)
        elif style in Styles.COLORS.keys():
            self._apply_color(style, start, end)
        elif style == Styles.TAG_BOLD:
            self._apply_bold(start, end)

    def _apply_color(self, color: str, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Applies color to the selected text. If a title is within the selection, the whole title is colored.
        :param color: Color name corresponding to the Gdk RGB color definition.
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        # Titles will always be whole lines, so we only need to check the start tags.
        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_iter_start: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            tag_table: Gtk.TextTagTable = self._buffer.get_tag_table()
            h3_tag: Gtk.TextTag = tag_table.lookup(Styles.TAG_H3)
            h4_tag: Gtk.TextTag = tag_table.lookup(Styles.TAG_H4)
            if line_iter_start.has_tag(h4_tag) or line_iter_start.has_tag(h3_tag):
                # Color the whole line
                line_iter_end: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
                line_iter_end.forward_to_line_end()
                for color_tag in Styles.COLORS.keys():
                    # Remove all other color tags on whole titles.
                    self._buffer.remove_tag_by_name(color_tag, line_iter_start, line_iter_end)
                self._buffer.apply_tag_by_name(color, line_iter_start, line_iter_end)
            else:
                for color_tag in Styles.COLORS.keys():
                    # Remove all other color tags.
                    self._buffer.remove_tag_by_name(color_tag, start, end)
                self._buffer.apply_tag_by_name(color, start, end)

    def _apply_bold(self, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Toggles bold style on/off on the current selection.
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        # Get bold state at insertion point and then either apply or remove bold.
        insertion_point: Gtk.TextIter = self._buffer.get_iter_at_mark(self._buffer.get_insert())
        if insertion_point.has_tag(self._buffer.get_tag_table().lookup(Styles.TAG_BOLD)):
            # The cursor is inside bold text. Just remove the bold tag.
            self._buffer.remove_tag_by_name(Styles.TAG_BOLD, start, end)
        else:
            # Cursor is not in bold text, reapply bold to the whole selection.
            # Remove bold tag on the whole selection and reapply it.
            self._buffer.remove_tag_by_name(Styles.TAG_BOLD, start, end)
            self._buffer.apply_tag_by_name(Styles.TAG_BOLD, start, end)

    def _apply_h_style(self, style_tag: str, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Applies h3/4 style to the current paragraph or all selected paragraphs.
        :param style_tag: One of the defined style tags (h3, h4)
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_iter_start: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end.forward_to_line_end()

            # Remove all other styles, titles do not keep anything.
            self._buffer.remove_all_tags(line_iter_start, line_iter_end)
            self._buffer.apply_tag_by_name(style_tag, line_iter_start, line_iter_end)

    def _apply_paragraph_style(self, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Applies standard paragraph style to the current paragraph or all selected paragraphs.
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_iter_start: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end.forward_to_line_end()

            # Remove all other styles, titles do not keep anything.
            for tag in [Styles.TAG_H3, Styles.TAG_H4, Styles.TAG_LIST]:
                self._buffer.remove_tag_by_name(tag, line_iter_start, line_iter_end)
            # A title is a larger and bold font.
            self._buffer.apply_tag_by_name(Styles.TAG_PAR, line_iter_start, line_iter_end)

    def _apply_list_style(self, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Applies standard list style to the current paragraph or all selected paragraphs.
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        # TODO Add bullet to the beginning of lines.
        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_iter_start: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            # Get the iterator at the end of the line.
            line_iter_end: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_iter_end.forward_to_line_end()

            for tag in [Styles.TAG_H3, Styles.TAG_H4, Styles.TAG_PAR]:
                self._buffer.remove_tag_by_name(tag, line_iter_start, line_iter_end)

            # Insert a special label widget that makes the list bullet.
            anchor = self._buffer.create_child_anchor(line_iter_start)

            bullet = Gtk.Label(label='•')
            bullet.set_size_request(30, 10)
            rgb = Gdk.RGBA()
            rgb.parse('rgb(255, 0, 0)')
            bullet.override_background_color(Gtk.StateFlags.NORMAL, rgb)

            self._text_view.add_child_at_anchor(bullet, anchor)

            # Writing invalidated the iterators.
            line_iter_start = self._buffer.get_iter_at_line(line_number)
            line_iter_end = self._buffer.get_iter_at_line(line_number)
            line_iter_end.forward_to_line_end()
            self._buffer.apply_tag_by_name(Styles.TAG_LIST, line_iter_start, line_iter_end)
            # Refresh the window to show the new label.
            self.show_all()


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(application_id="org.example.myapp", **kwargs)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self, title="Text test")
            # Shows all widgets inside the window.
            self.window.show_all()
            self.window.present()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
