import wx
import wx.richtext as rt

from ConfigManager import ConfigManager
from Constants.Numbers import Numbers
from Constants.Strings import Strings
from DirectoryLoader import DirectoryLoader
from FileParser import FileParser


class Gui(wx.Frame):
    """

    """

    def __init__(self, parent, title):
        """

        :param parent:
        :param title:
        """
        super(Gui, self).__init__(parent, title=title)
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

        # Sizer configuration
        # Main window - main horizontal sizer
        #  left vertical sizer = top static box sizer(article menu logo, logo name, alt, title), files
        #  middle vertical sizer = left static sizer (article image (name, alt, title)) right sizer (date, article main title, keywords, description) text area
        #  right vertical sizer = aside images

        # Create sizers
        self.main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_column_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_top_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=Strings.label_menu_logo)

        self.right_main_row_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_left_static_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=Strings.label_article_image)
        self.top_right_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=Strings.label_article_info)

        self.right_bottom_row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.left_column_sizer.Add(self.left_top_static_sizer, flag=wx.LEFT, border=Numbers.control_border_size)

        self.right_main_row_vertical_sizer.Add(self.right_top_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                               border=Numbers.control_border_size, proportion=0)
        self.right_main_row_vertical_sizer.Add(self.right_bottom_row_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                               border=Numbers.control_border_size, proportion=1)
        self.right_top_sizer.Add(self.top_left_static_sizer, flag=wx.ALIGN_LEFT | wx.RIGHT,
                                 border=0)

        self.right_top_sizer.Add(self.top_right_static_sizer, 1, flag=wx.ALIGN_LEFT | wx.EXPAND)
        self.main_horizontal_sizer.Add(self.left_column_sizer, 0, wx.EXPAND)
        self.main_horizontal_sizer.Add(self.right_main_row_vertical_sizer, 1, wx.EXPAND)

        # Set layout into the window
        self.SetSizer(self.main_horizontal_sizer)
        self.SetAutoLayout(1)
        # Resize to fit all components, makes the window as small as possible
        # self.left_column_sizer.Fit(self)

        # Create main font for text fields
        self.text_field_font: wx.Font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)

        # Left column section ------------------------------------------------------------------------------------------
        # Create a placeholder image
        self.placeholder_logo_image = wx.Image(Numbers.logo_image_size, Numbers.logo_image_size)
        self.placeholder_logo_image.Replace(0, 0, 0, 255, 255, 255)
        self.menu_logo_image = wx.StaticBitmap(self, -1, wx.Bitmap(self.placeholder_logo_image))
        # Set border to the image
        self.left_top_static_sizer.Add(self.menu_logo_image, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT, border=1)
        # Create menu logo name text box
        self.field_logo_name = wx.TextCtrl(self, -1, value=Strings.label_menu_logo_name_placeholder,
                                           size=wx.Size(98, 35),
                                           style=wx.TE_MULTILINE | wx.TE_CENTRE | wx.TE_NO_VSCROLL)
        self.field_logo_name.SetFont(self.text_field_font)

        self.field_logo_alt = wx.TextCtrl(self, -1, value=Strings.label_menu_logo_alt_placeholder, size=wx.Size(98, 45),
                                          style=wx.TE_MULTILINE)
        self.field_logo_name.SetFont(self.text_field_font)
        self.field_logo_title = wx.TextCtrl(self, -1, value=Strings.label_menu_logo_title_placeholder,
                                            size=wx.Size(98, 49), style=wx.TE_MULTILINE)
        self.field_logo_name.SetFont(self.text_field_font)
        self.field_logo_alt.SetFont(self.text_field_font)
        self.field_logo_title.SetFont(self.text_field_font)

        self.left_top_static_sizer.Add(self.field_logo_name)
        self.left_top_static_sizer.Add(self.field_logo_alt)
        self.left_top_static_sizer.Add(self.field_logo_title)

        # File list
        # Create a list
        self.page_list = wx.ListBox(self, wx.LB_SINGLE | wx.LB_SORT, name=Strings.label_page_list,
                                    size=wx.Size(98, 300))
        self.page_list.SetFont(self.text_field_font)

        # Middle section -----------------------------------------------------------------------------------------------
        # Add image placeholder into middle top left static sizer
        self.placeholder_main_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        self.placeholder_main_image.Replace(0, 0, 0, 255, 255, 255)
        self.main_image = wx.StaticBitmap(self, -1, wx.Bitmap(self.placeholder_main_image))
        self.top_left_static_sizer.Add(self.main_image, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT, border=1)

        # Add text controls
        self.field_main_image_alt = wx.TextCtrl(self, -1, value=Strings.label_article_image_alt, size=wx.Size(160, 30))
        self.field_main_image_title = wx.TextCtrl(self, -1, value=Strings.label_article_image_title,
                                                  size=wx.Size(160, 30))
        self.field_main_image_name = wx.TextCtrl(self, -1, value=Strings.label_article_image_name,
                                                 size=wx.Size(160, 30))

        self.field_article_date = wx.TextCtrl(self, -1, value=Strings.label_article_date, size=wx.Size(160, 30))
        self.field_article_title = wx.TextCtrl(self, -1, value=Strings.label_article_title, size=wx.Size(250, 30))
        self.field_article_keywords = wx.TextCtrl(self, -1, value=Strings.label_article_keywords, size=wx.Size(250, 30))
        self.field_article_description = wx.TextCtrl(self, -1, value=Strings.label_article_description,
                                                     size=wx.Size(250, 30))

        self.top_right_static_sizer.Add(self.field_article_date)
        self.top_right_static_sizer.Add(self.field_main_image_name, flag=wx.EXPAND)
        self.top_right_static_sizer.Add(self.field_main_image_title, flag=wx.EXPAND)
        self.top_right_static_sizer.Add(self.field_main_image_alt, flag=wx.EXPAND)
        self.top_right_static_sizer.Add(self.field_article_title, flag=wx.TOP | wx.EXPAND, border=16)
        self.top_right_static_sizer.Add(self.field_article_keywords, flag=wx.EXPAND)
        self.top_right_static_sizer.Add(self.field_article_description, flag=wx.EXPAND)

        # Add the list into the bottom sizer, give it a sizing weight and let it expand vertically
        self.left_column_sizer.Add(self.page_list, flag=wx.LEFT, border=Numbers.control_border_size, proportion=1)

        # Add main text area
        self.main_text_area = rt.RichTextCtrl(self, style=wx.VSCROLL)
        self.right_bottom_row_sizer.Add(self.main_text_area, flag=wx.EXPAND | wx.LEFT | wx.TOP, proportion=1, border=2)

        # Add right aside photo column
        self.right_photo_column_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=Strings.label_photo_column)
        self.right_photo_column_sizer.SetMinSize((211, -1))
        self.right_bottom_row_sizer.Add(self.right_photo_column_sizer, flag=wx.EXPAND | wx.LEFT,
                                        border=Numbers.control_border_size)

        # After all is added, let the window know how big it should be
        self.main_horizontal_sizer.SetSizeHints(self)

        # Bind click handlers
        self.Bind(wx.EVT_MENU, self.quit_button_handler, self.file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self.about_button_handler, self.file_menu_item_about)
        self.Bind(wx.EVT_MENU, self.open_button_handler, self.file_menu_item_open)
        self.Bind(wx.EVT_LISTBOX, self.list_item_click_handler, self.page_list)

        # Prepare tools
        self.config_manager = ConfigManager()
        self.directory_loader = None
        self.file_parser = FileParser()
        self.page_dictionary = None
        # Load last working directory
        self.__fill_page_list()

    def __fill_page_list(self):
        """

        :return:
        """
        try:
            self.directory_loader = DirectoryLoader()
            self.page_dictionary = self.directory_loader.get_file_dict(self.config_manager.get_working_dir())
            self.page_list.InsertItems(sorted(self.page_dictionary.keys()), 0)
        except IndexError:
            print('Select a whitebear directory')

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
        dlg = wx.DirDialog(self, Strings.label_choose_dir, Strings.home_directory,
                           wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
        # Modal means the user is locked into this dialog an can not use the rest of the application
        if dlg.ShowModal() == wx.ID_OK:
            self.config_manager.store_working_dir(dlg.GetPath())
            self.__fill_page_list()
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
        selected_name = self.page_list.GetStringSelection()
        output = self.file_parser.create((selected_name, self.page_dictionary[selected_name]))
        print(output)


app = wx.App()
frame = Gui(None, Strings.editor_name)
frame.Show()
app.MainLoop()
