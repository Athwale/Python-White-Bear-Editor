import enchant
import wx
from Constants.Constants import Numbers, Strings
from Tools.ConfigManager import ConfigManager
from pathlib import Path
from enchant.checker import SpellChecker


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
        # TODO what if hunspell is not installed
        # TODO fix layout
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_spellcheck_setup,
                           size=(Numbers.spellcheck_dialog_width, Numbers.spellcheck_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._checker = SpellChecker(self._config_manager.get_spelling_lang())

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Spelling package
        self._provider_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_provider = wx.StaticText(self, -1, Strings.label_dictionary_provider + ': ')
        self._content_provider = wx.StaticText(self, -1, Strings.label_none)
        self._provider_sub_sizer.Add(self._label_provider, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._provider_sub_sizer.Add(1, -1)
        self._provider_sub_sizer.Add(self._content_provider, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._provider_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Dictionary location
        self._dictionary_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_path = wx.StaticText(self, -1, Strings.label_dictionary_location + ': ')
        self._content_path = wx.StaticText(self, -1, Strings.label_none)
        self._dictionary_sub_sizer.Add(self._label_path, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._dictionary_sub_sizer.Add(self._content_path, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._dictionary_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Dictionary selection
        choices = enchant.list_languages() if enchant.list_languages() else ['-']
        self._selection_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_language = wx.StaticText(self, -1, Strings.label_spelling_language + ': ')
        self._language_list = wx.ComboBox(self, -1, choices=choices,
                                          style=wx.CB_DROPDOWN | wx.CB_SORT | wx.CB_READONLY)
        self._language_list.SetSelection(0)
        self._selection_sub_sizer.Add(self._label_language, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._selection_sub_sizer.Add(11, -1)
        self._selection_sub_sizer.Add(self._language_list, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._selection_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Restart info
        self._restart_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_restart = wx.StaticText(self, -1, Strings.label_restart_required)
        self._restart_sub_sizer.Add(self._label_restart, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._restart_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        self._ok_button.SetFocus()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._main_vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                      border=Numbers.widget_border_size)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            self._config_manager.store_spelling_language(self._language_list.GetValue())

    def _display_dialog_contents(self) -> None:
        """
        Display the information in the dialog.
        :return: None
        """
        self._content_provider.SetLabelText(str(self._checker.dict.provider))
        self._content_path.SetLabelText(str(Path(enchant.get_user_config_dir() / Path(self._checker.lang))))
        # todo what if not found?
        selection = self._language_list.FindString(self._config_manager.get_spelling_lang())
        self._language_list.SetSelection(selection)
