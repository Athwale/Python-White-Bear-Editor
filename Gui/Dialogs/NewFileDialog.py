import os
from typing import List, Dict

import wx

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu
from Tools.Tools import Tools


class NewFileDialog(wx.Dialog):

    def __init__(self, parent, menus: Dict[str, WhitebearDocumentMenu]):
        """
        Display a dialog that allows editing additional data used in html generation.
        Default main title, author, contact, keywords, main page meta description. script, main page red/black text
        :param parent: The parent frame.
        :param menus: List of available menu pages.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_new_document,
                           size=(Numbers.new_file_dialog_width, Numbers.new_file_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._menus = menus
        self._doc_path = None

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Name sub sizer
        self._name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_file_name = wx.StaticText(self, -1, Strings.label_name + ': ')
        self._field_name = wx.TextCtrl(self, -1)
        self._name_sub_sizer.Add(self._label_file_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._name_sub_sizer.Add(8, -1)
        self._name_sub_sizer.Add(self._field_name, proportion=1)
        self._information_sizer.Add(self._name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_name_tip = Tools.get_warning_tip(self._field_name, Strings.label_article_title)
        self._field_name.SetBackgroundColour(Numbers.RED_COLOR)
        self._field_name_tip.SetMessage(Strings.warning_name_incorrect)

        choices: List[str] = [menu.get_section_name() for menu in self._menus.values()]
        # Category sub sizer
        self._category_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_category = wx.StaticText(self, -1, Strings.label_target_section + ': ')
        self._box_menu = wx.ComboBox(self, -1, choices=choices, style=wx.CB_DROPDOWN | wx.CB_SORT | wx.CB_READONLY)
        self._box_menu.SetSelection(0)
        self._category_sub_sizer.Add(self._label_category, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._category_sub_sizer.Add(self._box_menu, proportion=1)
        self._information_sizer.Add(self._category_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        self._ok_button.Disable()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_TEXT, self._handle_name_change, self._field_name)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, check if target file exists and prevent overwriting it.
        :param event: The button event, used to distinguish between buttons.
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            # Check for file existence.
            # We must have at least one parsed menu which has a working directory at this point, otherwise we would
            # not be in this dialog.
            working_dir: str = next(iter(self._menus.values())).get_working_directory()
            file_name: str = self._field_name.GetValue() + Strings.extension_html

            path = os.path.join(working_dir, file_name)
            if os.path.exists(path):
                wx.MessageBox(Strings.warning_file_exists, Strings.status_error, wx.OK | wx.ICON_ERROR)
            else:
                self._doc_path = path

    # noinspection PyUnusedLocal
    def _handle_name_change(self, event: wx.CommandEvent) -> None:
        """
        Disable OK button if the name field is empty.
        :param event: Not used
        :return: None
        """
        new_name = self._field_name.GetValue()
        wrong_name: bool = False
        for c in new_name:
            if not c.isalnum():
                wrong_name = True
            if c == '-':
                wrong_name = False
        if wrong_name:
            self._field_name.SetBackgroundColour(Numbers.RED_COLOR)
            self._field_name_tip.SetMessage(Strings.warning_name_incorrect)
            self._field_name_tip.EnableTip(True)
            self._field_name_tip.Show(True)
            self._ok_button.Disable()
        else:
            self._field_name_tip.SetMessage(Strings.status_ok)
            self._field_name_tip.DoHideNow()
            self._field_name.SetBackgroundColour(Numbers.GREEN_COLOR)
            self._ok_button.Enable()

    def get_path(self) -> str:
        """
        Returns the disk path for a new document. Call this before destroying the dialog and only if OK is pressed.
        :return: The disk path for a new document.
        """
        return self._doc_path

    def get_section(self) -> WhitebearDocumentMenu:
        """
        Returns menu section for a new document. Call this before destroying the dialog and only if OK is pressed.
        :return: The menu section for a new document.
        """
        for menu in self._menus.values():
            if menu.get_section_name() == self._box_menu.GetValue():
                return menu
