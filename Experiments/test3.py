import wx
from enchant.checker import SpellChecker


class SpellCheckerDialog(wx.Dialog):
    """
    Spellchecker.
    # TODO work with richtextctrl
    # TODO where is the dictionary?
    # TODO replace strings with Constants variables.
    """

    def __init__(self, parent, title, checker: SpellChecker) -> None:
        """
        Spellchecker constructor
        :param parent: Dialog parent.
        :param title: Dialog title.
        :param checker: SpellChecker instance.
        """
        wx.Dialog.__init__(self, parent, title=title, size=(500, 357), style=wx.DEFAULT_DIALOG_STYLE)
        self._checker = checker
        # How much of the text around current mistake is shown.
        self._context_chars = 40
        self._buttons = []

        self.mistake_preview_field = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.replace_with_field = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        self.suggestions_list = wx.ListBox(self, -1, style=wx.LB_SINGLE)
        self._init_layout()

        self.Bind(wx.EVT_LISTBOX, self.list_select_handler, self.suggestions_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.list_doubleclick_handler, self.suggestions_list)

    def _init_layout(self) -> None:
        """
        Initialize layout.
        :return: None
        """
        border: int = 3
        size = (150, -1)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_fields_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        replace_with_sizer = wx.BoxSizer(wx.HORIZONTAL)

        replace_with_sizer.Add(wx.StaticText(self, -1, 'Replace with:'), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border)
        replace_with_sizer.Add(self.replace_with_field, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border)

        mistakes_label = wx.StaticText(self, -1, 'Unrecognised word:')
        text_fields_sizer.Add(mistakes_label, 0, wx.LEFT | wx.TOP, border)
        text_fields_sizer.Add(self.mistake_preview_field, 1, wx.ALL | wx.EXPAND, border)
        text_fields_sizer.Add(replace_with_sizer, 0, wx.EXPAND, border)
        text_fields_sizer.Add(self.suggestions_list, 1, wx.ALL | wx.EXPAND, border)

        buttons_sizer.AddSpacer(mistakes_label.GetSize()[1] + border)

        counter: int = 1
        for button_id, label, action in ((wx.ID_IGNORE, 'Ignore', self.buttons_handler),
                                         (wx.ID_NOTOALL, 'Ignore all', self.buttons_handler),
                                         (wx.ID_REPLACE, 'Replace', self.buttons_handler),
                                         (wx.ID_REPLACE_ALL, 'Replace all', self.buttons_handler),
                                         (wx.ID_ADD, 'Add to dictionary', self.buttons_handler)):
            button = wx.Button(self, button_id, label, size=size)
            buttons_sizer.Add(button, 0, wx.ALL, border)
            button.Bind(wx.EVT_BUTTON, action)
            self._buttons.append(button)
            if (counter % 2) == 0:
                buttons_sizer.Add(wx.StaticLine(self, -1, size=size), 0, wx.ALIGN_CENTER_HORIZONTAL)
            counter += 1
        buttons_sizer.Add(wx.StaticLine(self, -1, size=size), 0, wx.ALIGN_CENTER_HORIZONTAL)
        # Close button will never have to be disabled and therefore is not in _buttons.
        close_button = wx.Button(self, wx.ID_CLOSE, 'Close', size=size)
        buttons_sizer.Add(close_button, 0, wx.ALL, border)
        close_button.Bind(wx.EVT_BUTTON, self.buttons_handler)

        main_sizer.Add(text_fields_sizer, 1, wx.EXPAND, border)
        main_sizer.Add(buttons_sizer, 0, wx.RIGHT, border)
        # We are using a set dialog size, so Fit method is not needed.
        self.SetSizer(main_sizer)

    def go_to_next(self) -> bool:
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
        return True

    def _replace(self) -> None:
        """
        Instructs the spellchecker to replace current mistake with the contents of replace_with_field.
        :return: None
        """
        replacement = self.replace_with_field.GetValue()
        if replacement:
            self._checker.replace(replacement)
        self.go_to_next()

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
            self.go_to_next()
        elif button_id == wx.ID_NOTOALL:
            self._checker.ignore_always()
            self.go_to_next()
        elif button_id == wx.ID_REPLACE:
            self._replace()
        elif button_id == wx.ID_REPLACE_ALL:
            self._checker.replace_always(self.replace_with_field.GetValue())
            self.go_to_next()
        elif button_id == wx.ID_ADD:
            # Add new word to dictionary.
            self._checker.add()
            self.go_to_next()
        elif button_id == wx.ID_CLOSE:
            if self.IsModal():
                self.EndModal(wx.ID_OK)
            else:
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

def run():
    text = 'Toto je pkusny text s nkolika pravopismymy chibamy'
    # text = 'Text bez oiewru'
    checker = SpellChecker('cs_CZ', text)
    print('in:  ', checker.get_text())

    app = wx.App(False)
    dlg = SpellCheckerDialog(parent=None, title='Spellchecker', checker=checker)
    dlg.Show()
    dlg.go_to_next()
    app.MainLoop()
    print('out: ', checker.get_text())


if __name__ == '__main__':
    run()
