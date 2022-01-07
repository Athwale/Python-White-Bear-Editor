from typing import Any, Optional
import wx
from enchant.checker import SpellChecker
"""
    enchant.checker.wxSpellCheckerDialog: wxPython spellchecker interface
    This module provides the class :py:class:`wxSpellCheckerDialog`, which provides
    a wxPython dialog that can be used as an interface to a spell checking
    session. Currently, it is intended as a proof-of-concept and demonstration
    class, but it should be suitable for general-purpose use in a program.
    The class must be given an :py:class:`enchant.checker.SpellChecker` object with
    which to operate.  It can (in theory...) be used in modal and non-modal
    modes.  Use `Show()` when operating on an array of characters as it will
    modify the array in place, meaning other work can be done at the same
    time.  Use `ShowModal()` when operating on a static string.
"""
_DOC_ERRORS = ["ShowModal"]


class SpellCheckerDialog(wx.Dialog):
    """Simple spellcheck dialog for wxPython

    This class implements a simple spellcheck interface for wxPython,
    in the form of a dialog.  It's intended mainly of an example of
    how to do this, although it should be useful for applications that
    just need a simple graphical spellchecker.

    To use, a :py:class:`SpellChecker` instance must be created and passed to the
    dialog before it is shown:

        >>> chkr = SpellChecker("en_AU",text)
        >>> dlg = SpellCheckerDialog(chkr,None,-1,"")
        >>> dlg.Show()

    This is most useful when the text to be checked is in the form of
    a character array, as it will be modified in place as the user
    interacts with the dialog.  For checking strings, the final result
    will need to be obtained from the `SpellChecker` object:

        >>> chkr = SpellChecker("en_AU",text)
        >>> dlg = SpellCheckerDialog(chkr,None,-1,"")
        >>> dlg.ShowModal()
        >>> text = chkr.get_text()

    Currently the checker must deal with strings of the same type as
    returned by wxPython - unicode or normal string depending on the
    underlying system.  This needs to be fixed, somehow...
    """

    _DOC_ERRORS = [
        "dlg",
        "chkr",
        "dlg",
        "chkr",
        "dlg",
        "dlg",
        "chkr",
        "dlg",
        "chkr",
        "dlg",
        "ShowModal",
        "dlg",
    ]

    # Remember dialog size across invocations by storing it on the class
    sz = (300, 70)

    def __init__(self, checker: SpellChecker, parent: Optional[Any] = None, id: int = -1, title: str = "Spelling",
                 size=(300, 70), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER) -> None:
        wx.Dialog.__init__(self, parent, title=title, size=size, style=style)
        self._numContext = 40
        self._checker = checker
        self.buttons = []
        self._buttonsEnabled = True
        self.error_text = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.replace_text = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.replace_list = wx.ListBox(self, -1, style=wx.LB_SINGLE)
        self.init_layout()
        self.Bind(wx.EVT_LISTBOX, self.on_repl_select, self.replace_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_replace, self.replace_list)

    def init_layout(self) -> None:
        """Lay out controls and add buttons."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        txt_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        replace_sizer = wx.BoxSizer(wx.HORIZONTAL)
        txt_sizer.Add(
            wx.StaticText(self, -1, "Unrecognised Word:"), 0, wx.LEFT | wx.TOP, 5
        )
        txt_sizer.Add(self.error_text, 1, wx.ALL | wx.EXPAND, 5)
        replace_sizer.Add(
            wx.StaticText(self, -1, "Replace with:"),
            0,
            wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            5,
        )
        replace_sizer.Add(self.replace_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        txt_sizer.Add(replace_sizer, 0, wx.EXPAND, 0)
        txt_sizer.Add(self.replace_list, 2, wx.ALL | wx.EXPAND, 5)
        sizer.Add(txt_sizer, 1, wx.EXPAND, 0)
        for label, action, tip in (
            ("Ignore", self.on_ignore, "Ignore this word and continue"),
            (
                "Ignore All",
                self.on_ignore_all,
                "Ignore all instances of this word and continue",
            ),
            ("Replace", self.on_replace, "Replace this word"),
            ("Replace All", self.on_replace_all, "Replace all instances of this word"),
            ("Add", self.on_add, "Add this word to the dictionary"),
            ("Done", self.on_done, "Finish spell-checking and accept changes"),
        ):
            btn = wx.Button(self, -1, label)
            btn.SetToolTip(wx.ToolTip(tip))
            btn_sizer.Add(btn, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
            btn.Bind(wx.EVT_BUTTON, action)
            self.buttons.append(btn)
        sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def advance(self) -> bool:
        """Advance to the next error.

        This method advances the SpellChecker to the next error, if
        any.  It then displays the error and some surrounding context,
        and well as listing the suggested replacements.
        """
        # Advance to next error, disable if not available
        try:
            self._checker.next()
        except StopIteration:
            self.enable_buttons(False)
            self.error_text.SetValue("")
            self.replace_list.Clear()
            self.replace_text.SetValue("")
            if self.IsModal():  # test needed for SetSpellChecker call
                # auto-exit when checking complete
                self.EndModal(wx.ID_OK)
            return False
        self.enable_buttons()
        # Display error context with erroneous word in red.
        # Restoring default style was misbehaving under win32, so
        # I am forcing the rest of the text to be black.
        self.error_text.SetValue("")
        self.error_text.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        l_context = self._checker.leading_context(self._numContext)
        self.error_text.AppendText(l_context)
        self.error_text.SetDefaultStyle(wx.TextAttr(wx.RED))
        self.error_text.AppendText(self._checker.word)
        self.error_text.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        t_context = self._checker.trailing_context(self._numContext)
        self.error_text.AppendText(t_context)
        # Display suggestions in the replacements list
        suggests = self._checker.suggest()
        self.replace_list.Set(suggests)
        self.replace_text.SetValue(suggests and suggests[0] or "")
        return True

    def enable_buttons(self, state: bool = True) -> None:
        """Enable the checking-related buttons"""
        if state != self._buttonsEnabled:
            for btn in self.buttons[:-1]:
                btn.Enable(state)
            self._buttonsEnabled = state

    def get_repl(self) -> str:
        """Get the chosen replacement string."""
        repl = self.replace_text.GetValue()
        return repl

    def on_add(self, evt: Any) -> None:
        """Callback for the "add" button."""
        self._checker.add()
        self.advance()

    def on_done(self, evt: Any) -> None:
        """Callback for the "close" button."""
        SpellCheckerDialog.sz = self.error_text.GetSize()
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    def on_ignore(self, evt: Any) -> None:
        """Callback for the "ignore" button.
        This simply advances to the next error.
        """
        self.advance()

    def on_ignore_all(self, evt: Any) -> None:
        """Callback for the "ignore all" button."""
        self._checker.ignore_always()
        self.advance()

    def on_replace(self, evt: Any) -> None:
        """Callback for the "replace" button."""
        repl = self.get_repl()
        if repl:
            self._checker.replace(repl)
        self.advance()

    def on_replace_all(self, evt: Any) -> None:
        """Callback for the "replace all" button."""
        repl = self.get_repl()
        self._checker.replace_always(repl)
        self.advance()

    def on_repl_select(self, evt: Any) -> None:
        """Callback when a new replacement option is selected."""
        sel = self.replace_list.GetSelection()
        if sel == -1:
            return
        opt = self.replace_list.GetString(sel)
        self.replace_text.SetValue(opt)


def run():
    class SpellDialog(SpellCheckerDialog):
        def __init__(self, *args):
            super().__init__(*args)
            self.Bind(wx.EVT_CLOSE, self.on_close)

        def on_close(self, evnt):
            print(["A:", dlg._checker.get_text()])
            self.Destroy()

    from enchant.checker import SpellChecker

    text = "This is sme text with a fw speling errors in it. Here are a fw more to tst it ut."
    print(["B:", text])
    checker = SpellChecker("en_US", text)

    app = wx.App(False)
    dlg = SpellDialog(checker)
    dlg.Show()
    app.MainLoop()


if __name__ == "__main__":
    run()
