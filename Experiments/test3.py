import wx
from enchant.checker import SpellChecker


class SpellCheckerDialog(wx.Dialog):
    """
    Spellchecker.
    # TODO work with richtextctrl
    # TODO where is the dictionary?
    """

    def __init__(self, parent, checker: SpellChecker) -> None:
        """
        Spellchecker constructor
        :param parent: Dialog parent.
        :param checker: SpellChecker instance.
        """
        wx.Dialog.__init__(self, parent, title='Spelling', size=(500, 350), style=wx.DEFAULT_DIALOG_STYLE)
        self._checker = checker
        # How much of the text around current mistake is shown.
        self._context_chars = 40
        self._buttons = []

        self.mistake_preview_field = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.replace_with_field = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        self.suggestions_list = wx.ListBox(self, -1, style=wx.LB_SINGLE)
        self._init_layout()

        self.Bind(wx.EVT_LISTBOX, self.on_list_select, self.suggestions_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_replace, self.suggestions_list)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _init_layout(self) -> None:
        """
        Initialize layout.
        :return: None
        """
        border: int = 3
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_fields_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        replace_with_sizer = wx.BoxSizer(wx.HORIZONTAL)

        replace_with_sizer.Add(wx.StaticText(self, -1, 'Replace with:'), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border)
        replace_with_sizer.Add(self.replace_with_field, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border)

        mistakes_label = wx.StaticText(self, -1, 'Unrecognised Word:')
        text_fields_sizer.Add(mistakes_label, 0, wx.LEFT | wx.TOP, border)
        text_fields_sizer.Add(self.mistake_preview_field, 1, wx.ALL | wx.EXPAND, border)
        text_fields_sizer.Add(replace_with_sizer, 0, wx.EXPAND, border)
        text_fields_sizer.Add(self.suggestions_list, 1, wx.ALL | wx.EXPAND, border)

        buttons_sizer.AddSpacer(mistakes_label.GetSize()[1] + border)

        for label, action in (('Ignore', self.on_ignore),
                              ('Ignore All', self.on_ignore_all),
                              ('Replace', self.on_replace),
                              ('Replace All', self.on_replace_all),
                              ('Add to dictionary', self.on_add)):
            button = wx.Button(self, -1, label, size=(150, -1))
            buttons_sizer.Add(button, 0, wx.ALL, border)
            button.Bind(wx.EVT_BUTTON, action)
            self._buttons.append(button)
        close_button = wx.Button(self, -1, 'Close', size=(150, -1))
        buttons_sizer.Add(close_button, 0, wx.ALL, border)
        close_button.Bind(wx.EVT_BUTTON, self.on_done)

        main_sizer.Add(text_fields_sizer, 1, wx.EXPAND, border)
        main_sizer.Add(buttons_sizer, 0, wx.RIGHT, border)
        # We are using a set dialog size, so Fit method is not needed.
        self.SetSizer(main_sizer)

    def go_to_next(self) -> bool:
        """
        Advances the SpellChecker to the next mistake, if there is one. It then displays the mistake and some
        surrounding context, as well as listing the suggested replacements.
        :return: False if there is nothing to advance to.
        """
        # Advance to next mistake, disable buttons except Close if no mistake is found.
        try:
            self._checker.next()
        except StopIteration:
            self.enable_buttons(False)
            self.mistake_preview_field.Clear()
            self.suggestions_list.Clear()
            self.replace_with_field.Clear()
            if self.IsModal():
                # Close self if modal.
                # TODO remove these if they end up being useless.
                self.EndModal(wx.ID_OK)
            return False
        self.enable_buttons()
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
        suggests = self._checker.suggest()
        self.suggestions_list.Set(suggests)
        self.replace_with_field.SetValue(suggests[0] if suggests else '')
        return True

    def enable_buttons(self, state: bool = True) -> None:
        """
        Enable/disable buttons in the dialog.
        :param state: True to enable.
        :return: None
        """
        for button in self._buttons:
            button.Enable(state)

    # noinspection PyUnusedLocal
    def on_add(self, event: wx.CommandEvent) -> None:
        """
        Add new word to the dictionary.
        :param event: Unused.
        :return: None
        """
        self._checker.add()
        self.go_to_next()

    # noinspection PyUnusedLocal
    def on_done(self, event: wx.CommandEvent) -> None:
        """
        Cose dialog. Calls on_close.
        :param event: Unused.
        :return: None
        """
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    # noinspection PyUnusedLocal
    def on_close(self, event: wx.CommandEvent) -> None:
        """
        Close event handler.
        :param event: Unused.
        :return: None
        """
        print('out:', self._checker.get_text())
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_ignore(self, event: wx.CommandEvent) -> None:
        """
        Moves to the next error.
        :param event: Unused.
        :return: None
        """
        self.go_to_next()

    # noinspection PyUnusedLocal
    def on_ignore_all(self, event: wx.CommandEvent) -> None:
        """
        Sets the checker to ignore all occurrences of this mistake.
        :param event: Unused.
        :return: None
        """
        self._checker.ignore_always()
        self.go_to_next()

    # noinspection PyUnusedLocal
    def on_replace(self, event: wx.CommandEvent) -> None:
        """
        Replace button handler.
        :param event: Unused.
        :return: None
        """
        replacement = self.replace_with_field.GetValue()
        if replacement:
            self._checker.replace(replacement)
        self.go_to_next()

    # noinspection PyUnusedLocal
    def on_replace_all(self, event: wx.CommandEvent) -> None:
        """
        Replace all button handler.
        :param event: Unused.
        :return: None
        """
        self._checker.replace_always(self.replace_with_field.GetValue())
        self.go_to_next()

    # noinspection PyUnusedLocal
    def on_list_select(self, event: wx.CommandEvent) -> None:
        """
        Handler for the list of possible replacement words.
        :param event: Unused.
        :return: None
        """
        index: int = self.suggestions_list.GetSelection()
        selection: str = self.suggestions_list.GetString(index)
        self.replace_with_field.SetValue(selection)


def run():
    text = 'Toto je pkusny text s nkolika pravopismymy chibamy'
    # text = 'Text bez oiewru'
    print('in: ', text)
    checker = SpellChecker('cs_CZ', text)

    app = wx.App(False)
    dlg = SpellCheckerDialog(parent=None, checker=checker)
    dlg.Show()
    dlg.go_to_next()
    app.MainLoop()


if __name__ == '__main__':
    run()
