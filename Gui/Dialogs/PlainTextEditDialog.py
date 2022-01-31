from pathlib import Path

import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.SpellCheckedDialog import SpellCheckedDialog
from Tools.ConfigManager import ConfigManager
from Tools.Tools import Tools


class PlainTextEditDialog(SpellCheckedDialog):

    def __init__(self, parent, file: Path):
        """
        Display a dialog with information about the link where the user can edit it.
        :param parent: Parent frame.
        :param link: the Link instance to display.
        """
        super().__init__(parent, title=Strings.label_dialog_edit_link,
                         size=(Numbers.edit_link_dialog_width, Numbers.edit_link_dialog_height),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._file_name = file
        self._config_manager = ConfigManager.get_instance()

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Text field sizer
        self._text_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._field_text = wx.TextCtrl(self, -1)
        self._text_sub_sizer.Add(self._field_text, proportion=1)
        self._information_sizer.Add(self._text_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_link_text_tip = Tools.get_warning_tip(self._field_text, Strings.label_text)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._delete_button)

        self._original_text = self._link.get_text()[0]
        self._original_url = self._link.get_url()[0]
        self._original_title = self._link.get_title()[0]

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing on ok if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OK:
            self._run_spellcheck(((self._field_link_title, Strings.label_link_title),
                                  (self._field_text, Strings.label_text)))
            # Save new information into the file
        else:
            self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self._field_url: (self._link.get_url(), self._field_url_tip),
                          self._field_link_title: (self._link.get_title(), self._field_link_title_tip),
                          self._field_text: (self._link.get_text(), self._field_link_text_tip)}
        for field, value in field_to_value.items():
            tip = value[1]
            if value[0][1]:
                tip.SetMessage(Strings.seo_check + '\n' + value[0][1])
                tip.EnableTip(True)
                field.SetBackgroundColour(Numbers.RED_COLOR)
            else:
                tip.SetMessage(Strings.seo_check + '\n' + Strings.status_ok)
                tip.DoHideNow()
                field.SetBackgroundColour(Numbers.GREEN_COLOR)
            field.SetValue(value[0][0])

        # Set checkbox local state
        self._checkbox_local.SetValue(self._link.is_local())
        self.Enable()
