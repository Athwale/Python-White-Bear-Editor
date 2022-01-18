from typing import Tuple

import wx

from Constants.Constants import Strings
from Gui.Dialogs.SpellCheckerDialog import SpellCheckerDialog


class SpellCheckedDialog(wx.Dialog):

    def __init__(self, parent, title, size, style):
        """
        Special dialog master class containing spellcheck function. This is used to inherit this functionality
        in all dialogs that need spellchecking.
        :param parent: Parent dialog.
        :param title: Dialog title.
        :param size: Dialog size.
        :param style: Style parameters
        """
        wx.Dialog.__init__(self, parent, title=title, size=size, style=style)

    def _run_spellcheck(self, fields: Tuple[Tuple[wx.TextCtrl, str], ...]) -> bool:
        """
        Checks spelling on all fields passed into it. Opens a spellcheck dialog if mistakes are found and replaces
        the text in the field.
        :param fields: Tuple of wx.TextCtrl and their names.
        :return: True if mistakes were found.
        """
        again = False
        for field, name in fields:
            dlg = SpellCheckerDialog(self, Strings.label_dialog_spellcheck + ': ' + name, field.GetValue())
            dlg.run()
            if dlg.found_mistake():
                if dlg.ShowModal() == wx.ID_OK:
                    # Replace text in field and recheck seo again as a result of it.
                    field.SetValue(dlg.get_fixed_text())
                    dlg.Destroy()
                again = True
        return again
