from pathlib import Path

import wx

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager


class PlainTextEditDialog(wx.Dialog):

    def __init__(self, parent, file: Path):
        """
        Show a simple plain text editor with a file opened with the ability to save the file.
        :param parent: Parent frame.
        :param file: File to open and display.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_link,
                           size=(Numbers.plain_text_dialog_width, Numbers.plain_text_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._file_name = file
        self._config_manager = ConfigManager.get_instance()

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Text field sizer
        self._text_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._field_text = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self._text_sub_sizer.Add(self._field_text, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._text_sub_sizer, 1, flag=wx.EXPAND)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._save_button = wx.Button(self, wx.ID_OK, Strings.button_save)
        self._save_button.SetDefault()
        grouping_sizer.Add(self._save_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)
        self.SetTitle(Strings.label_dialog_edit_file + ': ' + str(self._file_name.name))
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._save_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, save the file.
        :param event: The button event
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            self._field_text.SaveFile(str(self._file_name))

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        self._field_text.LoadFile(str(self._file_name))
        self.Enable()
