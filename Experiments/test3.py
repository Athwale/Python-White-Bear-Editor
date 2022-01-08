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
        self._buttons_enabled = True

        self.mistake_preview = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.replace_text = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        self.suggestions_list = wx.ListBox(self, -1, style=wx.LB_SINGLE)
        self.init_layout()

        self.Bind(wx.EVT_LISTBOX, self.on_repl_select, self.suggestions_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_replace, self.suggestions_list)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def init_layout(self) -> None:
        """
        Initialize layout.
        :return: None
        """
        border: int = 3
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_fields_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        replace_with_sizer = wx.BoxSizer(wx.HORIZONTAL)

        replace_with_sizer.Add(wx.StaticText(self, -1, "Replace with:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border)
        replace_with_sizer.Add(self.replace_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border)

        mistakes_label = wx.StaticText(self, -1, "Unrecognised Word:")
        text_fields_sizer.Add(mistakes_label, 0, wx.LEFT | wx.TOP, border)
        text_fields_sizer.Add(self.mistake_preview, 1, wx.ALL | wx.EXPAND, border)
        text_fields_sizer.Add(replace_with_sizer, 0, wx.EXPAND, border)
        text_fields_sizer.Add(self.suggestions_list, 1, wx.ALL | wx.EXPAND, border)

        buttons_sizer.AddSpacer(mistakes_label.GetSize()[1] + border)

        for label, action in (("Ignore", self.on_ignore),
                              ("Ignore All", self.on_ignore_all),
                              ("Replace", self.on_replace),
                              ("Replace All", self.on_replace_all),
                              ("Add to dictionary", self.on_add),
                              ("Close", self.on_done)):
            button = wx.Button(self, -1, label, size=(150, -1))
            buttons_sizer.Add(button, 0, wx.ALL, border)
            button.Bind(wx.EVT_BUTTON, action)
            self._buttons.append(button)

        main_sizer.Add(text_fields_sizer, 1, wx.EXPAND, border)
        main_sizer.Add(buttons_sizer, 0, wx.RIGHT, border)
        # We are using a set dialog size, so Fit method is not needed.
        self.SetSizer(main_sizer)

    def advance(self) -> bool:
        """
        Advances the SpellChecker to the next mistake, if there is one. It then displays the mistake and some
        surrounding context, as well as listing the suggested replacements.
        :return:
        """
        # Advance to next mistake, disable buttons if not available
        try:
            self._checker.next()
        except StopIteration:
            self.enable_buttons(False)
            self.mistake_preview.SetValue("")
            self.suggestions_list.Clear()
            self.replace_text.SetValue("")
            if self.IsModal():  # test needed for SetSpellChecker call
                # auto-exit when checking complete
                self.EndModal(wx.ID_OK)
            return False
        self.enable_buttons()
        # Display error context with erroneous word in red.
        # Restoring default style was misbehaving under win32, so
        # I am forcing the rest of the text to be black.
        self.mistake_preview.SetValue("")
        self.mistake_preview.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        l_context = self._checker.leading_context(self._context_chars)
        self.mistake_preview.AppendText(l_context)
        self.mistake_preview.SetDefaultStyle(wx.TextAttr(wx.RED))
        self.mistake_preview.AppendText(self._checker.word)
        self.mistake_preview.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        t_context = self._checker.trailing_context(self._context_chars)
        self.mistake_preview.AppendText(t_context)
        # Display suggestions in the replacements list
        suggests = self._checker.suggest()
        self.suggestions_list.Set(suggests)
        self.replace_text.SetValue(suggests and suggests[0] or "")
        return True

    def enable_buttons(self, state: bool = True) -> None:
        """
        Enable buttons in dialog.
        :param state: True to enable.
        :return: None
        """
        if state != self._buttons_enabled:
            for btn in self._buttons[:-1]:
                btn.Enable(state)
            self._buttons_enabled = state

    def get_repl(self) -> str:
        """
        Get the chosen replacement string.
        :return: The chosen string.
        """
        repl = self.replace_text.GetValue()
        return repl

    # noinspection PyUnusedLocal
    def on_add(self, evt) -> None:
        """
        Add new word to the dictionary.
        :param evt: Unused.
        :return: None
        """
        self._checker.add()
        self.advance()

    # noinspection PyUnusedLocal
    def on_done(self, evt) -> None:
        """
        Cose dialog. Calls on_close.
        :param evt: Unused.
        :return: None
        """
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    # noinspection PyUnusedLocal
    def on_close(self, event) -> None:
        """
        Close event handler.
        :param event: Unused.
        :return: None
        """
        print('out:', self._checker.get_text())
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_ignore(self, evt) -> None:
        """
        Moves to the next error.
        :param evt: Unused.
        :return: None
        """
        self.advance()

    # noinspection PyUnusedLocal
    def on_ignore_all(self, evt) -> None:
        """
        Sets the checker to ignore all occurrences of this mistake.
        :param evt: Unused.
        :return: None
        """
        self._checker.ignore_always()
        self.advance()

    # noinspection PyUnusedLocal
    def on_replace(self, evt) -> None:
        """
        Replace button handler.
        :param evt: Unused.
        :return: None
        """
        repl = self.get_repl()
        if repl:
            self._checker.replace(repl)
        self.advance()

    # noinspection PyUnusedLocal
    def on_replace_all(self, evt) -> None:
        """
        Replace all button handler.
        :param evt: Unused.
        :return: None
        """
        repl = self.get_repl()
        self._checker.replace_always(repl)
        self.advance()

    # noinspection PyUnusedLocal
    def on_repl_select(self, evt) -> None:
        """
        Handler for the list of possible replacement words.
        :param evt: Unused.
        :return: None
        """
        sel = self.suggestions_list.GetSelection()
        if sel == -1:
            return
        opt = self.suggestions_list.GetString(sel)
        self.replace_text.SetValue(opt)


def run():
    text = "Toto je pkusny text s nkolika pravopismymy chibamy"
    print('in: ', text)
    checker = SpellChecker("cs_CZ", text)

    app = wx.App(False)
    dlg = SpellCheckerDialog(parent=None, checker=checker)
    dlg.Show()
    dlg.advance()
    app.MainLoop()


if __name__ == "__main__":
    run()
