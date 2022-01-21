import wx
from Constants.Constants import Numbers, Strings
from Tools.ConfigManager import ConfigManager


class SpellCheckSetupDialog(wx.Dialog):
    """
    Spellchecker dialog that works with a string. It uses an external instance of enchant spellchecker.
    To get the fixed string back use the checker instance passed into the dialog.
    """

    def __init__(self, parent) -> None:
        """
        Spellchecker dialog constructor.
        :param parent: Dialog parent.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_menu_item_spellcheck_setup,
                           size=(Numbers.spellcheck_dialog_width, Numbers.spellcheck_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._config_manager: ConfigManager = ConfigManager.get_instance()
