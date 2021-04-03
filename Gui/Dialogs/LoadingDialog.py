import wx
import wx.html

from Constants.Constants import Strings, Numbers
from Resources.Fetch import Fetch


class LoadingDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, title=Strings.status_loading, style=wx.STAY_ON_TOP)
        self.SetSize(Numbers.splashscreen_dialog_size)
        self.SetIcon(wx.Icon(Fetch.get_resource_path('icon.ico')))
        self._image = wx.Bitmap(Fetch.get_resource_path('splashscreen.png'), wx.BITMAP_TYPE_PNG)
        self._bitmap = wx.StaticBitmap(self, -1, self._image)

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self._main_vertical_sizer.Add(self._bitmap, flag=wx.EXPAND)
        self.SetSizer(self._main_vertical_sizer)
