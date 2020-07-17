import wx
import wx.richtext as rt
from wx.py import images

from ConfigManager import ConfigManager
from Constants.Numbers import Numbers
from Constants.Strings import Strings
from Constants.Constants import Constants
from FileParser import FileParser
from Gui.Dialogs.ModalDialog import ModalDialog
from Threads.Events.CarrierEvent import CarrierEvent
from Threads.FileListThread import FileListThread


class MainFrame(wx.Frame):
    """
    Main GUI controlling class. The Frame is actually the on screen window.
    """

    # Create a new unique id for our custom event.
    EVT_CARRIER_TYPE_ID: int = wx.NewEventType()

    def __init__(self):
        """
        Constructor for the GUI of the editor. This is the main frame so we pass None as the parent.
        """
        # -1 is a special ID which generates a random wx ID
        super(MainFrame, self).__init__(None, -1, title=Strings.editor_name, style=wx.DEFAULT_FRAME_STYLE)
        self.Centre()
        self.Update()
        self._init_status_bar()
        self._init_top_tool_bar()
        self._init_menu()

        # Create main panel
        self.main_panel = wx.Panel(self)

        # Sizer configuration
        # Main window - main horizontal sizer
        #  left vertical sizer = files
        #  middle vertical sizer = left static sizer (article image (name, alt, title)),
        #   right top static box sizer(article logo, logo name, alt, title)
        #  right sizer (date, article main title, keywords, description) text area
        #  right vertical sizer = aside images

        # Create sizers
        self.main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_column_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_top_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=Strings.label_menu_logo)

        self.right_main_row_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_left_static_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=Strings.label_article_image)
        self.top_right_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=Strings.label_article_info)

        self.right_bottom_row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The | is a bitwise or and flags is a bit mask of constants
        self.right_main_row_vertical_sizer.Add(self.right_top_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                               border=Numbers.control_border_size, proportion=0)
        self.right_main_row_vertical_sizer.Add(self.right_bottom_row_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                               border=Numbers.control_border_size, proportion=1)
        self.right_top_sizer.Add(self.top_left_static_sizer, flag=wx.ALIGN_LEFT | wx.RIGHT,
                                 border=0)
        self.right_top_sizer.Add(self.top_right_static_sizer, 1, flag=wx.ALIGN_LEFT | wx.EXPAND)
        self.right_top_sizer.Add(self.right_top_static_sizer, flag=wx.LEFT, border=Numbers.control_border_size)
        self.main_horizontal_sizer.Add(self.left_column_sizer, 0, wx.EXPAND)
        self.main_horizontal_sizer.Add(self.right_main_row_vertical_sizer, 1, wx.EXPAND)
        self.SetSizer(self.main_horizontal_sizer)

        # Create main font for text fields
        self.text_field_font: wx.Font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)

        # right column section -----------------------------------------------------------------------------------------
        # Create a placeholder image
        self.placeholder_logo_image = wx.Image(Numbers.logo_image_size, Numbers.logo_image_size)
        self.placeholder_logo_image.Replace(0, 0, 0, 245, 255, 255)
        self.menu_logo_image = wx.StaticBitmap(self, -1, wx.Bitmap(self.placeholder_logo_image))
        # Set border to the image
        self.right_top_static_sizer.Add(self.menu_logo_image, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT, border=1)
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

        self.right_top_static_sizer.Add(self.field_logo_name)
        self.right_top_static_sizer.Add(self.field_logo_alt)
        self.right_top_static_sizer.Add(self.field_logo_title)

        # File list
        self.page_list = wx.ListBox(self, wx.LB_SINGLE | wx.LB_SORT, name=Strings.label_page_list,
                                    size=wx.Size(210, 300))
        self.page_list.SetFont(self.text_field_font)

        # Middle section -----------------------------------------------------------------------------------------------
        # Add image placeholder into middle top left static sizer
        self.placeholder_main_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        self.placeholder_main_image.Replace(0, 0, 0, 245, 255, 255)
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

        self.SetAutoLayout(1)
        self.SetMinClientSize(wx.Size(Numbers.minimal_window_size_width, Numbers.minimal_window_size_height))

        # Bind click handlers
        # Bind window close events, X button and emergency quit
        # Binding an event to a handler function, the last parameter is the source of the event. In case of for
        # example buttons, all buttons will create EVT_BUTTON and we will not know which handler to use unless
        # the source is set.
        self.Bind(wx.EVT_CLOSE, self.close_button_handler, self)
        # This calls the quit method if the user logs off the computer
        self.Bind(wx.EVT_QUERY_END_SESSION, self.close_button_handler)

        self.Bind(wx.EVT_MENU, self.about_button_handler, self.help_menu_item_about)
        self.Bind(wx.EVT_MENU, self.open_button_handler, self.file_menu_item_open)
        self.Bind(wx.EVT_MENU, self.quit_button_handler, self.file_menu_item_quit)
        self.Bind(wx.EVT_LISTBOX, self.list_item_click_handler, self.page_list)

        # Bind custom event
        self.Bind(wx.PyEventBinder(self.EVT_CARRIER_TYPE_ID, 1), self.carrier_event_handler)

        # Prepare tools
        self.config_manager = ConfigManager()
        self.file_parser = FileParser()

        # Prepare window contents -------------------------------------------------------------------------------------
        # Load last working directory
        self._set_status_text(Strings.status_loading, 2)
        self._load_working_directory(self.config_manager.get_working_dir())

        # Load last window position and size
        self.SetPosition((self.config_manager.get_window_position()))
        size = self.config_manager.get_window_size()
        if size == (-1, -1):
            self.Maximize()
        else:
            self.SetSize(size)

    def _init_menu(self):
        """
        Set up menu bar for the frame.
        :return: None
        """
        # Create menu bar and the menu itself
        # All class instance variables have to be specified during the constructor
        self.menu_bar = wx.MenuBar()
        self.file_menu = wx.Menu()
        self.help_menu = wx.Menu()

        # Add the file menu into the menu bar. & Tells the program to create Ctrl+F shortcut to open menu.
        self.menu_bar.Append(self.file_menu, Strings.label_file)
        # Add the Help menu into the menu bar. & Tells the program to create Ctrl+F shortcut to open menu.
        self.menu_bar.Append(self.help_menu, Strings.label_help)

        # Create a menu item for open
        self.file_menu_item_open = wx.MenuItem(self.file_menu, wx.ID_OPEN, Strings.label_open, Strings.label_open_hint)
        # Create a menu item for about
        self.help_menu_item_about = wx.MenuItem(self.help_menu, wx.ID_ABOUT, Strings.label_about,
                                                Strings.label_about_hint)
        # Create a menu item for quit
        self.file_menu_item_quit = wx.MenuItem(self.file_menu, wx.ID_CLOSE, Strings.label_quit, Strings.label_quit_hint)

        # Put menu items into the menu buttons
        self.file_menu.Append(self.file_menu_item_open)
        self.file_menu.AppendSeparator()
        self.file_menu.Append(self.file_menu_item_quit)
        self.help_menu.Append(self.help_menu_item_about)

        self.SetMenuBar(self.menu_bar)

    def _init_top_tool_bar(self):
        """
        Set up top tool bar for the frame.
        :return: None
        """
        self.tool_bar = self.CreateToolBar()
        # Add toolbar tools
        self.tool_bar.AddTool(-1, Strings.toolbar_new_file, images.getPyBitmap(), Strings.toolbar_new_file)
        self.tool_bar.Realize()

    def _init_status_bar(self):
        """
        Set up status bar for the frame.
        :return: None
        """
        # Create a status bar with 3 fields
        self.status_bar = self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-3, -2, -1])
        # Initialize status bar
        self._set_status_text('', 0)
        self._set_status_text('', 1)

    def _set_status_text(self, text: str, position=0) -> None:
        """
        Set a text into a position in status bar and prepend a separator.
        :param text: Text to set.
        :param position: Where to set the text, 0 is default
        :return: None
        """
        to_set = '| ' + text
        self.status_bar.SetStatusText(to_set, position)

    def _load_working_directory(self, path: str) -> None:
        """
        Load a working directory into the editor.
        :param path: str, path to the working directory
        :return: None
        """
        # Disable the gui until load is done
        self.Disable()
        self._set_status_text(Strings.status_loading, 2)
        file_list_thread = FileListThread(self, self.EVT_CARRIER_TYPE_ID, str(path))
        file_list_thread.start()

    def _show_error_log(self):
        """

        :return:
        """
        self._set_status_text(Strings.status_error, 2)

    def carrier_event_handler(self, event: CarrierEvent):
        """

        :param event:
        :return:
        """
        if event.get_payload_type() == Constants.file_list_type:
            self.page_list.Clear()
            self.page_list.InsertItems(event.get_payload(), 0)
            # Select last used document
            self.page_list.SetStringSelection(self.config_manager.get_last_document())
            self.list_item_click_handler(wx.CommandEvent())
            # Enable GUI when the load is done
            self._set_status_text(Strings.status_ready, 2)
            self.Enable()
        if event.get_payload_type() == Constants.exception_type:
            # TODO open dialog and append the error to its log
            self._show_error_log()
            self.Enable()

    def quit_button_handler(self, event):
        """
        Handles clicks to the Quit button in File menu. Calls Close function which sends EVT_CLOSE and triggers
        close_button_handler() which does all the saving work.
        :param event: Not used
        :return: None
        """
        self.Close(True)

    def close_button_handler(self, event):
        """
        Handle user exit from the editor. Save last known window position, size and last opened document.
        :param event: CloseEvent, if CanVeto is False the window must be destroyed the system is forcing it.
        :return: None
        """
        if event.CanVeto():
            # Save window position
            self.config_manager.store_window_position(self.GetScreenPosition())
            # Save window size
            if self.IsMaximized():
                # Special value to indicate maximized window
                self.config_manager.store_window_size((-1, -1))
            else:
                self.config_manager.store_window_size(self.GetSize())
            # Store last selected document
            if self.page_list.GetSelection() != wx.NOT_FOUND:
                self.config_manager.store_last_open_document(self.page_list.GetString(self.page_list.GetSelection()))
            # TODO Save currently worked on document
        self.Destroy()

    def open_button_handler(self, event):
        """
        Handle opening a new working directory. Show a selection dialog, store the new directory and load it into
        editor.
        :param event: Not used.
        :return: None
        """
        dlg = wx.DirDialog(self, Strings.label_choose_dir, Strings.home_directory,
                           wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
        # Modal means the user is locked into this dialog an can not use the rest of the application
        if dlg.ShowModal() == wx.ID_OK:
            self.config_manager.store_working_dir(dlg.GetPath())
            self._load_working_directory(self.config_manager.get_working_dir())
        dlg.Destroy()

    def about_button_handler(self, event):
        """
        Handles clicks onto the About button. Displays a short message in another window.
        :param event: Not used.
        :return: None
        """
        ModalDialog(self, Strings.label_about_window_name, Strings.text_about_contents)

    def list_item_click_handler(self, event):
        """
        Handler function for clicking a page name in the web page list. Shows which website is selected in the status
        bar.
        :param event: wx event, brings the selected string from the menu.
        :return: None
        """
        selected_name = event.GetString()
        self._set_status_text(selected_name)
