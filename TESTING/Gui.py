import wx


class Gui(wx.Frame):

    def __init__(self, parent, title):
        super(Gui, self).__init__(parent, title=title, size=(250, 400))
        self.init_ui()

    def init_ui(self):
        self.Centre()
        self.Update()

        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit')
        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.quit_button_handler, file_menu_item)

    def quit_button_handler(self, event):
        self.Close()


app = wx.App()
frame = Gui(None, 'Okno')
frame.Show()
app.MainLoop()
