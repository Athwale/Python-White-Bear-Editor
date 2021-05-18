import wx
import wx.lib.scrolledpanel as scrolled


class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Scroll test", size=(200, 200))
        self._panel = wx.Panel(self, wx.ID_ANY)
        self._scrolled_panel = scrolled.ScrolledPanel(self._panel, -1)

        self._scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        self._scrolled_panel.SetSizer(self._scroll_sizer)

        self._add_button = wx.Button(self._panel, label="Add")
        self.Bind(wx.EVT_BUTTON, self.on_add)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(self._scrolled_panel, 1, wx.EXPAND)
        panel_sizer.Add(self._add_button)
        self._panel.SetSizer(panel_sizer)

    def on_add(self, event: wx.CommandEvent):
        new_text = wx.StaticText(self._scrolled_panel, -1, "New text")
        self._scroll_sizer.Add(new_text)
        self._scrolled_panel.Layout()
        self._scrolled_panel.SetupScrolling(scroll_x=False, scrollIntoView=True, scrollToTop=False)
        #wx.CallAfter(self._scrolled_panel.ScrollChildIntoView, new_text)
        self._scrolled_panel.ScrollChildIntoView(new_text)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame().Show()
    app.MainLoop()
