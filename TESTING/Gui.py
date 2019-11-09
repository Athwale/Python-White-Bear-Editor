import wx
import os


class Gui(wx.Frame):
    """

    """

    def __init__(self, parent, title):
        """

        :param parent:
        :param title:
        """
        super(Gui, self).__init__(parent, title=title, size=(250, 400))
        self.Centre()
        self.Update()
        self.CreateStatusBar()

        # Create menu bar and the menu itself
        # All class instance variables have to be specified in the constructor
        self.menu_bar = wx.MenuBar()
        self.file_menu = wx.Menu()

        # Add the file menu into the menu bar. & Tells the program to create Ctrl+F shortcut to open menu.
        self.menu_bar.Append(self.file_menu, '&File')
        self.SetMenuBar(self.menu_bar)

        # Create a menu item for quit
        self.file_menu_item_quit = wx.MenuItem(self.file_menu, wx.ID_EXIT, '&Quit', 'Quit')
        self.file_menu.Append(self.file_menu_item_quit)

        # Create a menu item for about
        self.file_menu_item_about = wx.MenuItem(self.file_menu, wx.ID_ABOUT, '&About', 'About')
        self.file_menu.Append(self.file_menu_item_about)

        # Create a menu item for open
        self.file_menu_item_open = wx.MenuItem(self.file_menu, wx.ID_OPEN, '&Open', 'Open')
        self.file_menu.Append(self.file_menu_item_open)

        # Create sizers
        self.left_column_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.left_column_sizer)
        self.SetAutoLayout(1)
        self.left_column_sizer.Fit(self)

        # Create a list
        self.page_list = wx.ListBox(self, name="page list")
        # Add the list into the sizer, give it a sizing weight and let it expand
        self.left_column_sizer.Add(self.page_list, 2, wx.EXPAND)

        # Bind click handlers
        self.Bind(wx.EVT_MENU, self.quit_button_handler, self.file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self.about_button_handler, self.file_menu_item_about)
        self.Bind(wx.EVT_MENU, self.open_button_handler, self.file_menu_item_open)



    def quit_button_handler(self, event):
        """

        :param event:
        :return:
        """
        self.Close(True)

    def open_button_handler(self, event):
        """

        :param event:
        :return:
        """
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
        """

        :param event:
        :return:
        """
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
