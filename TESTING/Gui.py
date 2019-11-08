import wx
import os


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

        # Create a menu item for quit
        file_menu_item_quit = wx.MenuItem(file_menu, wx.ID_EXIT, '&Quit', 'Quit')
        file_menu.Append(file_menu_item_quit)

        # Create a menu item for about
        file_menu_item_about = wx.MenuItem(file_menu, wx.ID_ABOUT, '&About', 'About')
        file_menu.Append(file_menu_item_about)

        # Create a menu item for open
        file_menu_item_open = wx.MenuItem(file_menu, wx.ID_OPEN, '&Open', 'Open')
        file_menu.Append(file_menu_item_open)

        # Create a list view


        # Bind click handlers
        self.Bind(wx.EVT_MENU, self.quit_button_handler, file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self.about_button_handler, file_menu_item_about)
        self.Bind(wx.EVT_MENU, self.open_button_handler, file_menu_item_open)

        self.CreateStatusBar()

    def quit_button_handler(self, event):
        self.Close(True)

    def open_button_handler(self, event):
        dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", dirname, "", "*.*", wx.FD_OPEN)
        # Modal means the user is locked into this dialog an can not use the rest of the application
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            f = open(os.path.join(dirname, filename), 'r')

            f.close()
        dlg.Destroy()

    def about_button_handler(self, event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        about_frame = wx.MessageDialog(self, "A small text editor", "About Sample Editor", wx.OK)
        about_frame.ShowModal()
        about_frame.Destroy()

    def OnEvent(self, event):
        """
        Handles otherwise unhandled events
        :param event:
        :return:
        """
        print('Unknown event occurred')

app = wx.App()
frame = Gui(None, 'Okno')
frame.Show()
app.MainLoop()
