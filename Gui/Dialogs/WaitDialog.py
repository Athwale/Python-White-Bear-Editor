import wx
import wx.html

from Constants.Constants import Strings, Numbers
from Resources.Fetch import Fetch


class WaitDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, style=wx.STAY_ON_TOP, size=(Numbers.saving_dialog_width,
                                                                     Numbers.saving_dialog_height))
        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_status = wx.StaticText(self, -1, Strings.status_none + ':')
        self._content_message = wx.StaticText(self, -1, Strings.label_none,
                                              style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(wx.Image(Fetch.get_resource_path('save.png'),
                                                                    wx.BITMAP_TYPE_PNG)))
        self._horizontal_sizer.Add(Numbers.widget_border_size, Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._bitmap, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=1)
        self._horizontal_sizer.Add(self._label_status, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                                   border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._content_message, 1, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                                   border=Numbers.widget_border_size)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self.SetSizer(self._main_vertical_sizer)

    def set_status(self, status: str) -> None:
        """
        Set the status. This will be followed by the message.
        :param status: New status.
        :return: None
        """
        self._label_status.SetLabelText(status)

    def set_message(self, name: str) -> None:
        """
        Set the file name which was saved.
        :param name: The file name.
        :return: None
        """
        self._content_message.SetLabelText(name)

    def set_bitmap(self, bitmap: wx.Bitmap) -> None:
        """
        Set the image in the dialog.
        :param bitmap: The bitmap.
        :return: None
        """
        self._bitmap.SetBitmap(bitmap)
