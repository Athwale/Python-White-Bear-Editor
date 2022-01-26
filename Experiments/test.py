import wx


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'List ctrl example', size=(200, 200))
        self._list_ctrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self._list_ctrl.InsertColumn(0, 'Data', format=wx.LIST_FORMAT_LEFT)
        self._list_ctrl.SetColumnWidth(0, 200)
        self._list_ctrl.EnableCheckBoxes()

        for i in range(0, 200):
            self._list_ctrl.InsertItem(0, 'item: ' + str(i))
            # Scrolling is slow because of checked checkboxes, unchecked boxes are ok.
            self._list_ctrl.CheckItem(0, True)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show(True)
        return True


if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
