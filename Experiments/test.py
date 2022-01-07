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

    TAG_PAR: str = 'tag-paragraph'
    TAG_H3: str = 'tag-h3'
    TAG_H4: str = 'tag-h4'
    TAG_LIST: str = 'tag-list'
    TAG_BOLD: str = 'tag-bold'

    LIST_BULLET_SIZE: int = 30
    H3_SPACING: int = 15
    H4_SPACING: int = 10

    COLORS: Dict[str, str] = {'red': 'rgb(255,0,0)',
                              'green': 'rgb(0,255,0)',
                              'orange': 'rgb(255,215,0)',
                              'black': 'rgb(0,0,0)'}


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

        self.connect('key-release-event', self._update_field_info)

        self._buffer: Gtk.TextBuffer = self._text_view.get_buffer()
        # Using modified signal does not work, iterators are invalid.
        self._buffer.connect('end-user-action', self.on_text_changed)

        text_scrolled = Gtk.ScrolledWindow()
        text_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        text_scrolled.set_size_request(300, -1)
        text_scrolled.add(self._text_view)

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

        self._label = Gtk.Label()
        self._label.set_text('Counter')
        v_box.add(self._label)

        h_box.add(text_scrolled)
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
        self._buffer.create_tag(Styles.TAG_H3, scale=2, weight=Pango.Weight.BOLD,
                                      pixels_above_lines=Styles.H3_SPACING,
                                      pixels_below_lines=Styles.H3_SPACING)
        self._buffer.create_tag(Styles.TAG_H4, scale=1.5, weight=Pango.Weight.BOLD,
                                      pixels_above_lines=Styles.H4_SPACING,
                                      pixels_below_lines=Styles.H4_SPACING)
        self._buffer.create_tag(Styles.TAG_PAR, scale=1)
        # List style:
        # Each new line is a separate bullet, so left marin is not necessary.
        self._buffer.create_tag(Styles.TAG_LIST, scale=1, indent=-30)
        self._write_test_text()

    # TODO write methods for all styles.
    def _write_test_text(self) -> None:
        """
        Write some test text into the text view.
        :return: None
        """
        self._write_text_in_style(Styles.TAG_H3, 'Title h3\n', 'black', False)
        self._write_text_in_style(Styles.TAG_PAR, 'Paragraph test text ', 'black', False)
        self._write_text_in_style(Styles.TAG_PAR, 'red text ', 'red', False)
        self._write_text_in_style(Styles.TAG_PAR, 'bold green text\n', 'green', True)
        self._write_text_in_style(Styles.TAG_H4, 'Title h4\n', 'black', False)

    def _write_text_in_style(self, style: str, text: str, color_tag: str, bold: bool) -> None:
        """
        Writes text to the text field at the current insertion point using the style.
        :param style: One of defined style constants from Styles.
        :param text: The text to insert.
        :param color_tag: The color to use.
        :param bold: True if text should be bold.
        :return: None
        """
        # TODO styles do not hold on the whole line if you type at the start of the line.
        # First insert text and only apply bold and color.
        tags = [color_tag, Styles.TAG_BOLD] if bold else [color_tag]
        current_line: int = self._buffer.get_iter_at_mark(self._buffer.get_insert()).get_line()
        self._buffer.insert_with_tags_by_name(self._buffer.get_iter_at_mark(self._buffer.get_insert()), text, *tags)
        # Apply style to the whole line.
        # TODO might need to apply color to the whole line on titles.
        line_start_iter: Gtk.TextIter = self._buffer.get_iter_at_line(current_line)
        line_end_iter: Gtk.TextIter = self._buffer.get_iter_at_line(current_line)
        # This moves the iterator one past the last valid character in the buffer which allows you to continue writing
        # in the same style, otherwise you continue in default no style.
        # TODO use this everywhere instead of to_line_end.
        # TODO still does not work entirely, backspacing a different style to a line breaks it.
        line_end_iter.forward_to_end()
        self._buffer.apply_tag_by_name(style, line_start_iter, line_end_iter)

    @staticmethod
    def _get_text(buffer: Gtk.TextBuffer) -> str:
        """
        Gets the whole text content of the buffer.
        :param buffer: Buffer to get text from.
        :return: String text from the buffer
        """
        start, end = buffer.get_bounds()
        return buffer.get_text(start, end, include_hidden_chars=True)

    def _update_field_info(self, window: Gtk.Window, _) -> None:
        """
        Rewrites the info label.
        :return: None
        """
        current_line: int = self._buffer.get_iter_at_mark(self._buffer.get_insert()).get_line()
        line_start_iter: Gtk.TextIter = self._buffer.get_iter_at_line(current_line)
        line_end_iter: Gtk.TextIter = self._buffer.get_iter_at_line(current_line)
        line_end_iter.forward_to_line_end()
        tag_table: Gtk.TextTagTable = self._buffer.get_tag_table()
        tag_names = [Styles.TAG_H3, Styles.TAG_H4, Styles.TAG_PAR, Styles.TAG_LIST, Styles.TAG_BOLD]
        tag_names.extend(Styles.COLORS.keys())
        used_tags_start = []
        used_tags_end = []
        for tag in line_start_iter.get_tags():
            for tag_name in tag_names:
                if tag_table.lookup(tag_name) == tag:
                    used_tags_start.append(tag_name)
        for tag in line_end_iter.get_tags():
            for tag_name in tag_names:
                if tag_table.lookup(tag_name) == tag:
                    used_tags_end.append(tag_name)
        self._label.set_text('Lines: {}\n'
                             'Chars: {}\n'
                             'Current line: {}\n'
                             'Style start: {}\n'
                             'Style end: {}'.format(self._buffer.get_line_count(),
                                                    self._buffer.get_char_count(),
                                                    current_line,
                                                    used_tags_start,
                                                    used_tags_end))

    def on_text_changed(self, buffer: Gtk.TextBuffer) -> None:
        """
        Text area handler called on end-user-action signal from buffer.
        :param buffer: The text_view's buffer that was used.
        :return: None
        """
        current_line: int = buffer.get_iter_at_mark(buffer.get_insert()).get_line()
        # TODO Catch text edits inside list and continue/cancel list/prevent multiple bullets on one line.
        line_start_iter: Gtk.TextIter = buffer.get_iter_at_line(current_line)
        # TODO the buffer does not have any default tag on empty lines.

        # TODO reapply style every time based on the first style found in the line if the styles do not mach.
        #  Might need to back up current style on key down.

        tag_table: Gtk.TextTagTable = buffer.get_tag_table()
        list_tag: Gtk.TextTag = tag_table.lookup(Styles.TAG_LIST)
        if line_start_iter.has_tag(list_tag):
            # TODO backspace can not remove list bullet. Because deleting the bullet does not remove the list style
            # TODO which is then immediately reapplied.
            # TODO get anchor get widgets
            # TODO on enter it continues to be a list without indent, reapply style to create new bullet
            self._apply_style(Styles.STYLE_LIST)

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
            line_start_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            tag_table: Gtk.TextTagTable = self._buffer.get_tag_table()
            h3_tag: Gtk.TextTag = tag_table.lookup(Styles.TAG_H3)
            h4_tag: Gtk.TextTag = tag_table.lookup(Styles.TAG_H4)
            if line_start_iter.has_tag(h4_tag) or line_start_iter.has_tag(h3_tag):
                # Color the whole line
                line_end_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
                line_end_iter.forward_to_line_end()
                for color_tag in Styles.COLORS.keys():
                    # Remove all other color tags on whole titles.
                    self._buffer.remove_tag_by_name(color_tag, line_start_iter, line_end_iter)
                self._buffer.apply_tag_by_name(color, line_start_iter, line_end_iter)
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
            line_start_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_end_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_end_iter.forward_to_line_end()

            # Remove all other styles, titles do not keep anything.
            self._buffer.remove_all_tags(line_start_iter, line_end_iter)
            self._buffer.apply_tag_by_name(style_tag, line_start_iter, line_end_iter)

    def _apply_paragraph_style(self, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Applies standard paragraph style to the current paragraph or all selected paragraphs.
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_start_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_end_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_end_iter.forward_to_line_end()

            # Remove all other styles, titles do not keep anything.
            for tag in [Styles.TAG_H3, Styles.TAG_H4, Styles.TAG_LIST]:
                self._buffer.remove_tag_by_name(tag, line_start_iter, line_end_iter)
            # A title is a larger and bold font.
            self._buffer.apply_tag_by_name(Styles.TAG_PAR, line_start_iter, line_end_iter)

    def _apply_list_style(self, start: Gtk.TextIter, end: Gtk.TextIter) -> None:
        """
        Applies standard list style to the current paragraph or all selected paragraphs.
        :param start: Text buffer start iterator.
        :param end: Text buffer end iterator.
        :return: None
        """
        for line_number in range(start.get_line(), end.get_line() + 1):
            # Start iterator is already at the current line start.
            line_start_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            # Get the iterator at the end of the line.
            line_end_iter: Gtk.TextIter = self._buffer.get_iter_at_line(line_number)
            line_end_iter.forward_to_line_end()

            for tag in [Styles.TAG_H3, Styles.TAG_H4, Styles.TAG_PAR]:
                self._buffer.remove_tag_by_name(tag, line_start_iter, line_end_iter)

            # Insert a special label widget that makes the list bullet.
            anchor: Gtk.TextChildAnchor = line_start_iter.get_child_anchor()
            if not anchor:
                anchor: Gtk.TextChildAnchor = self._buffer.create_child_anchor(line_start_iter)
                bullet = Gtk.Label(label='•')
                bullet.set_size_request(Styles.LIST_BULLET_SIZE, -1)
                self._text_view.add_child_at_anchor(bullet, anchor)

            # Writing invalidated the iterators.
            line_start_iter = self._buffer.get_iter_at_line(line_number)
            line_end_iter = self._buffer.get_iter_at_line(line_number)
            line_end_iter.forward_to_line_end()
            self._buffer.apply_tag_by_name(Styles.TAG_LIST, line_start_iter, line_end_iter)
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
