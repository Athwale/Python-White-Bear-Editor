import wx


class Gui(wx.Frame):

    def __init__(self, parent, title):
        super(Gui, self).__init__(parent, title=title, size=(250, 400))
        self.init_ui()

    def init_ui(self):
        self.Centre()
        self.Update()

        # Create menu bar and the menu itself
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        # Add the file menu into the menu bar. & Tells the program to create Ctrl+F shortcut to open menu.
        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)

        # Create a menu item
        file_menu_item_quit = wx.MenuItem(file_menu, wx.ID_EXIT, '&Quit', 'Any item help')
        file_menu.Append(file_menu_item_quit)

        # Create a base panel
        main_panel = wx.Panel(self)


        # Create a list view


        # Bind click handlers
        self.Bind(wx.EVT_MENU, self.quit_button_handler, file_menu_item_quit)

    def quit_button_handler(self, event):
        self.Close()


app = wx.App()
frame = Gui(None, 'Okno')
frame.Show()
app.MainLoop()
