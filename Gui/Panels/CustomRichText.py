import wx.richtext as rt
import wx


class CustomRichText(rt.RichTextCtrl):
    """
    Custom rich text control
    """

    def __init__(self, *args, **kw):
        """
        Constructor for the custom rich text control.
        :param args: Forwarded
        :param kw: Forwarded
        """
        super().__init__(*args, **kw)
        self.Bind(wx.EVT_KEY_DOWN, self.OnSelectAll)

    def OnSelectAll(self, event):
        print('a')
        event.Skip()