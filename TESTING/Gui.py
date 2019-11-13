import wx
from Strings.Strings import Strings
from DirectoryLoader import DirectoryLoader


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
        self.menu_bar.Append(self.file_menu, Strings.label_file)
        self.SetMenuBar(self.menu_bar)

        # Create a menu item for quit
        self.file_menu_item_quit = wx.MenuItem(self.file_menu, wx.ID_EXIT, Strings.label_quit, Strings.label_quit_hint)
        self.file_menu.Append(self.file_menu_item_quit)

        # Create a menu item for about
        self.file_menu_item_about = wx.MenuItem(self.file_menu, wx.ID_ABOUT, Strings.label_about,
                                                Strings.label_about_hint)
        self.file_menu.Append(self.file_menu_item_about)

        # Create a menu item for open
        self.file_menu_item_open = wx.MenuItem(self.file_menu, wx.ID_OPEN, Strings.label_open, Strings.label_open_hint)
        self.file_menu.Append(self.file_menu_item_open)

        # Create sizers
        self.left_column_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.left_column_sizer)
        self.SetAutoLayout(1)
        # Resize to fit all components, makes the window as small as possible
        # self.left_column_sizer.Fit(self)

        # Create a list
        self.page_list = wx.ListBox(self, wx.LB_SINGLE | wx.LB_SORT, name=Strings.label_page_list)
        # Add the list into the sizer, give it a sizing weight and let it expand
        self.left_column_sizer.Add(self.page_list, 2, wx.EXPAND)

        # Bind click handlers
        self.Bind(wx.EVT_MENU, self.quit_button_handler, self.file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self.about_button_handler, self.file_menu_item_about)
        self.Bind(wx.EVT_MENU, self.open_button_handler, self.file_menu_item_open)
        self.Bind(wx.EVT_LISTBOX, self.list_item_click_handler, self.page_list)

        # Prepare tools
        self.directory_loader = None

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
        dlg = wx.DirDialog(self, Strings.label_choose_dir, "", wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
        dlg.SetPath(Strings.home_directory)
        # Modal means the user is locked into this dialog an can not use the rest of the application
        if dlg.ShowModal() == wx.ID_OK:
            self.directory_loader = DirectoryLoader(dlg.GetPath())
            self.page_list.InsertItems(list(self.directory_loader.get_file_dict().keys()), 0)

        dlg.Destroy()

    def about_button_handler(self, event):
        """

        :param event:
        :return:
        """
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        about_frame = wx.MessageDialog(self, Strings.text_about_contents, Strings.label_about_window_name, wx.OK)
        about_frame.ShowModal()
        about_frame.Destroy()

    def list_item_click_handler(self, event):
        print(self.page_list.GetStringSelection())


app = wx.App()
frame = Gui(None, Strings.editor_name)
frame.Show()
app.MainLoop()
