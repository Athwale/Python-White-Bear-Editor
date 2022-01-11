import wx
from enchant.checker import SpellChecker
from Gui.Panels.CustomRichText import CustomRichText

from Constants.Constants import Strings, Numbers, Events


class RichTextSpellCheckerDialog(wx.Dialog):
    """
    Spellchecker dialog that works with a customized rich text control. It uses an external instance of
    enchant spellchecker.
    # TODO make this a subclass of a string based dialog used in all other fields in dialogs.
    """

    def __init__(self, parent, checker: SpellChecker, text_area: CustomRichText) -> None:
        """
        Spellchecker dialog constructor.
        :param parent: Dialog parent.
        :param checker: SpellChecker instance.
        :param text_area: RichTextCtrl instance to work with.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_spellcheck,
                           size=(Numbers.spellcheck_dialog_width, Numbers.spellcheck_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._checker = checker
        self._text_area = text_area
        # How much of the text around current mistake is shown.
        self._context_chars = Numbers.context_chars
        self._buttons = []

        self.mistake_preview_field = wx.TextCtrl(self, -1, size=wx.Size(-1, 76),
                                                 style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.replace_with_field = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        self.suggestions_list = wx.ListBox(self, -1, style=wx.LB_SINGLE)
        self._init_layout()

        self.Bind(wx.EVT_LISTBOX, self.list_select_handler, self.suggestions_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.list_doubleclick_handler, self.suggestions_list)
        self.Bind(wx.EVT_CLOSE, self._close_button_handler, self)
        self._run()

    def _init_layout(self) -> None:
        """
        Initialize layout.
        :return: None
        """
        size = wx.Size(150, -1)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_fields_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        replace_with_sizer = wx.BoxSizer(wx.HORIZONTAL)

        replace_with_sizer.Add(wx.StaticText(self, -1, Strings.label_replace_with), 0,
                               wx.ALL | wx.ALIGN_CENTER_VERTICAL, Numbers.widget_border_size)
        replace_with_sizer.Add(self.replace_with_field, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL,
                               Numbers.widget_border_size)

        mistakes_label = wx.StaticText(self, -1, Strings.label_unrecognized_word)
        text_fields_sizer.Add(mistakes_label, 0, wx.LEFT | wx.TOP, Numbers.widget_border_size)
        text_fields_sizer.Add(self.mistake_preview_field, 0, wx.ALL | wx.EXPAND, Numbers.widget_border_size)
        text_fields_sizer.Add(replace_with_sizer, 0, wx.EXPAND, Numbers.widget_border_size)
        text_fields_sizer.Add(self.suggestions_list, 0, wx.ALL | wx.EXPAND, Numbers.widget_border_size)

        buttons_sizer.AddSpacer(mistakes_label.GetSize()[1] + Numbers.widget_border_size)

        counter: int = 1
        for button_id, label, action in ((wx.ID_REPLACE, Strings.button_replace, self.buttons_handler),
                                         (wx.ID_REPLACE_ALL, Strings.button_replace_all, self.buttons_handler),
                                         (wx.ID_IGNORE, Strings.button_ignore, self.buttons_handler),
                                         (wx.ID_NOTOALL, Strings.button_ignore_all, self.buttons_handler),
                                         (wx.ID_ADD, Strings.button_add_to_dict, self.buttons_handler)):
            button = wx.Button(self, button_id, label, size=size)
            buttons_sizer.Add(button, 0, wx.ALL, Numbers.widget_border_size)
            button.Bind(wx.EVT_BUTTON, action)
            self._buttons.append(button)
            if (counter % 2) == 0:
                buttons_sizer.Add(wx.StaticLine(self, -1, size=size), 0, wx.ALIGN_CENTER_HORIZONTAL)
            counter += 1
        buttons_sizer.Add(wx.StaticLine(self, -1, size=size), 0, wx.ALIGN_CENTER_HORIZONTAL)
        # Close button will never have to be disabled and therefore is not in _buttons.
        close_button = wx.Button(self, wx.ID_CLOSE, Strings.button_close, size=size)
        buttons_sizer.Add(close_button, 0, wx.ALL, Numbers.widget_border_size)
        close_button.Bind(wx.EVT_BUTTON, self._close_button_handler)

        main_sizer.Add(text_fields_sizer, 1, wx.EXPAND, Numbers.widget_border_size)
        main_sizer.Add(buttons_sizer, 0, wx.RIGHT, Numbers.widget_border_size)
        # We are using a set dialog size, so Fit method is not needed.
        self.SetSizer(main_sizer)

    def _go_to_next(self) -> bool:
        """
        Moves the SpellChecker to the next mistake, if there is one. It then displays the mistake and some
        surrounding context, as well as listing the suggested replacements.
        :return: False if there is nothing to advance to.
        """
        # Go to next mistake, disable buttons except Close if no mistake is found.
        try:
            self._checker.next()
        except StopIteration:
            self.enable_buttons(False)
            self.mistake_preview_field.Clear()
            self.replace_with_field.Clear()
            self.suggestions_list.Clear()
            return False
        # Display mistake context with wrong word in red.
        self.mistake_preview_field.Clear()
        # Write leading context in black:
        self.mistake_preview_field.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.mistake_preview_field.AppendText(self._checker.leading_context(self._context_chars))
        # Write the wrong word in red:
        self.mistake_preview_field.SetDefaultStyle(wx.TextAttr(wx.RED))
        self.mistake_preview_field.AppendText(self._checker.word)
        # Write trailing context in black:
        self.mistake_preview_field.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.mistake_preview_field.AppendText(self._checker.trailing_context(self._context_chars))
        # Display suggestions in the replacements list
        suggestions = self._checker.suggest()
        self.suggestions_list.Set(suggestions)
        self.replace_with_field.SetValue(suggestions[0] if suggestions else '')
        self.enable_buttons()

        self._text_area.SelectWord(self._checker.wordpos)
        # The +1 ensures we always display a line even if it is the last line in currently visible portion of document.
        self._text_area.ShowPosition(self._checker.wordpos + 1)
        return True

    def _replace(self) -> None:
        """
        Instructs the spellchecker to replace current mistake with the contents of replace_with_field.
        :return: None
        """
        replacement = self.replace_with_field.GetValue()
        if replacement:
            # Replace text inside the rich text control as well as in the checker's text which the checker uses
            # internally.
            self._checker.replace(replacement)
            self._text_area.replace_with_style(replacement)
        self._go_to_next()

    def enable_buttons(self, state: bool = True) -> None:
        """
        Enable/disable buttons in the dialog.
        :param state: True to enable.
        :return: None
        """
        for button in self._buttons:
            button.Enable(state)

    def buttons_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks.
        :param event: The button event.
        :return: None
        """
        button_id = event.GetId()
        if button_id == wx.ID_IGNORE:
            self._go_to_next()
        elif button_id == wx.ID_NOTOALL:
            self._checker.ignore_always()
            self._go_to_next()
        elif button_id == wx.ID_REPLACE:
            self._replace()
        elif button_id == wx.ID_REPLACE_ALL:
            self._checker.replace_always(self.replace_with_field.GetValue())
            self._go_to_next()
        elif button_id == wx.ID_ADD:
            # Add new word to dictionary.
            self._checker.add()
            self._go_to_next()

    # noinspection PyUnusedLocal
    def _close_button_handler(self, event: wx.CloseEvent) -> None:
        """
        Handle dialog closing.
        :param event: Unused.
        :return: None
        """
        # Send an event to the main gui to signal dialog closing.
        done_evt = Events.SpellcheckEvent(self.GetId())
        # Dialog has its own event handler, so use the parent.
        wx.PostEvent(self.GetParent().GetEventHandler(), done_evt)
        self.Destroy()

    # noinspection PyUnusedLocal
    def list_select_handler(self, event: wx.CommandEvent) -> None:
        """
        Handler for the list of possible replacement words.
        :param event: Unused.
        :return: None
        """
        index: int = self.suggestions_list.GetSelection()
        selection: str = self.suggestions_list.GetString(index)
        self.replace_with_field.SetValue(selection)

    # noinspection PyUnusedLocal
    def list_doubleclick_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles double clicks in the suggestions list. Works like the replace button.
        :param event: Unused.
        :return: None
        """
        self._replace()

    def _run(self) -> None:
        """
        Run spellchecker using the text area given to it.
        :return: None.
        """
        self._checker.set_text(self._text_area.get_text())
        self._go_to_next()
