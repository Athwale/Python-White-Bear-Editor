import wx
import wx.html

from Constants.Constants import Strings, Numbers


class UploadDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE, title=Strings.label_upload,
                           size=(Numbers.upload_dialog_width, Numbers.upload_dialog_height))
        self.small_font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)

        self._main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._filelist_sizer = wx.BoxSizer(wx.VERTICAL)
        self._file_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self._file_list.SetFont(self.small_font)
        self._file_list.InsertColumn(0, Strings.label_files_to_upload, format=wx.LIST_FORMAT_LEFT)
        self._file_list.SetColumnWidth(0, Numbers.initial_panel_size)
        self._file_list.EnableCheckBoxes()

        self._filelist_sizer.Add(self._file_list, flag=wx.EXPAND, border=Numbers.widget_border_size, proportion=1)
        self._main_horizontal_sizer.Add(self._filelist_sizer, flag=wx.EXPAND)
        self.SetSizer(self._main_horizontal_sizer)
        self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the contents of dialog.
        :return: None
        """
        # List all files in the directory, check those that are changed or belong to changed documents.
        self._file_list.InsertItem(0, str(i))
