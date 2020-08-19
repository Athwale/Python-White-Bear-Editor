import os
from typing import Dict

import wx
import wx.richtext as rt
from wx.py import images

from Constants.Numbers import Numbers
from Constants.Strings import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Gui.Dialogs.AboutDialog import AboutDialog
from Threads.FileListThread import FileListThread
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentArticle import WhitebearDocument


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
        # Create font for text fields
        self.text_field_font: wx.Font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        # Prepare data objects
        self.config_manager = ConfigManager()
        self.tool_ids = []
        self.disableable_menu_items = []
        self.document_dictionary = {}

        self._init_status_bar()
        self._init_top_tool_bar()
        self._init_menu()
        self._init_sizers_panels()
        self._inflate_sizers()
        self._bind_handlers()

        # Set minimal size of the frame on screen, smaller frame would squish GUI too much.
        self.SetMinClientSize(wx.Size(Numbers.minimal_window_size_width, Numbers.minimal_window_size_height))

        # Prepare frame contents
        # Load last working directory
        self._set_status_text(Strings.status_loading, 3)
        self._load_working_directory(self.config_manager.get_working_dir())

        # Load last window position and size
        self.SetPosition((self.config_manager.get_window_position()))
        size = self.config_manager.get_window_size()
        if size == (-1, -1):
            self.Maximize()
        else:
            self.SetSize(size)

    def _init_menu(self) -> None:
        """
        Set up menu bar for the frame.
        :return: None
        """
        # Create menu bar and the menu itself
        # All class instance variables have to be specified during the constructor
        self.menu_bar = wx.MenuBar()
        self.file_menu = wx.Menu(style=wx.MENU_TEAROFF)
        self.help_menu = wx.Menu(style=wx.MENU_TEAROFF)

        # Add the file menu into the menu bar. & Tells the program to create Ctrl+F shortcut to open menu.
        self.menu_bar.Append(self.file_menu, Strings.label_menu_file)
        # Add the Help menu into the menu bar. & Tells the program to create Ctrl+F shortcut to open menu.
        self.menu_bar.Append(self.help_menu, Strings.label_menu_help)

        # Create a menu item for open
        self.file_menu_item_open = wx.MenuItem(self.file_menu, wx.ID_OPEN, Strings.label_menu_item_open,
                                               Strings.label_menu_item_open_hint)
        # Create a menu item for about
        self.help_menu_item_about = wx.MenuItem(self.help_menu, wx.ID_ABOUT, Strings.label_menu_item_about,
                                                Strings.label_menu_item_about_hint)
        self.disableable_menu_items.append(self.help_menu_item_about)

        # Create a menu item for quit
        self.file_menu_item_quit = wx.MenuItem(self.file_menu, wx.ID_CLOSE, Strings.label_menu_item_quit,
                                               Strings.label_menu_item_quit_hint)

        # Put menu items into the menu buttons
        self.file_menu.Append(self.file_menu_item_open)
        self.file_menu.AppendSeparator()
        self.file_menu.Append(self.file_menu_item_quit)
        self.help_menu.Append(self.help_menu_item_about)

        self.SetMenuBar(self.menu_bar)

    def _add_tool_id(self) -> wx.NewId():
        """
        Create and return a new wx ID for a tool in the toolbar, at the same time save the id in a list that is used
        to keep tract of all toolbar tools.
        :return: New wx ID.
        """
        new_id = wx.NewId()
        self.tool_ids.append(new_id)
        return new_id

    def _init_top_tool_bar(self) -> None:
        """
        Set up top tool bar for the frame.
        :return: None
        """
        self.tool_bar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)
        # Add toolbar tools
        self._add_tool_id()
        self.tool_bar.AddTool(self._add_tool_id(), Strings.toolbar_new_file, images.getPyBitmap(),
                              Strings.toolbar_new_file)
        self.tool_bar.Realize()

    def _init_status_bar(self) -> None:
        """
        Set up status bar for the frame.
        :return: None
        """
        # Create a status bar with 3 fields
        self.status_bar = self.CreateStatusBar(4)
        self.status_bar.SetStatusWidths([-6, -7, -2, -2])
        # Initialize status bar
        self._set_status_text('', 0)
        self._set_status_text('', 1)

    def _init_sizers_panels(self) -> None:
        """
        Set up sizers for the frame
        :return: None
        """
        # Create splitter window, This allows the file list to expand left.
        self.split_screen = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_NOBORDER)
        self.split_screen.SetMinimumPaneSize(Numbers.minimal_panel_size)
        # Create panels that go into the splitter window
        self.left_panel = wx.Panel(self.split_screen, style=wx.SUNKEN_BORDER)
        self.right_panel = wx.Panel(self.split_screen, style=wx.SUNKEN_BORDER)
        # Limit how far the file list can expand to prevent GUI from being squished too much.
        self.right_panel.SetMinSize((600, -1))
        self.split_screen.SplitVertically(self.left_panel, self.right_panel, 210)

        # Create a global sizer that contains the splitter window which contains the rest.
        self.main_horizontal_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_horizontal_sizer.Add(self.split_screen, 1, wx.EXPAND)

        # Create sizers that go into the panels.
        # Contains file list of pages
        self.filelist_column_sizer = wx.BoxSizer(wx.VERTICAL)
        # Contains right top sizer, right bottom sizer
        self.right_main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        # Contains article image sizer, article data sizer, menu logo static sizer
        self.right_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Contains main article image
        self.article_image_static_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self.right_panel,
                                                            label=Strings.label_article_image)
        # Contains article metadata controls
        self.article_data_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.right_panel,
                                                           label=Strings.label_article_info)
        # Contains menu logo controls
        self.menu_logo_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.right_panel,
                                                        label=Strings.label_article_menu_logo)
        # Contains main text area, photo column sizer
        self.right_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Contains article photos
        self.side_photo_column_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.right_panel,
                                                         label=Strings.label_article_photo_column)
        self.side_photo_column_sizer.SetMinSize((211, -1))

        # The | is a bitwise or and flags is a bit mask of constants
        self.right_main_vertical_sizer.Add(self.right_top_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                           border=Numbers.widget_border_size, proportion=0)
        self.right_main_vertical_sizer.Add(self.right_bottom_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                           border=Numbers.widget_border_size, proportion=1)
        self.right_top_sizer.Add(self.article_image_static_sizer, flag=wx.ALIGN_LEFT | wx.RIGHT,
                                 border=0)
        self.right_top_sizer.Add(self.article_data_static_sizer, 1, flag=wx.ALIGN_LEFT | wx.EXPAND)
        self.right_top_sizer.Add(self.menu_logo_static_sizer, flag=wx.LEFT, border=Numbers.widget_border_size)
        # Insert sizers with GUI into the respective panels, these are inserted into the splitter windows.s
        self.left_panel.SetSizer(self.filelist_column_sizer)
        self.right_panel.SetSizer(self.right_main_vertical_sizer)
        self.SetSizer(self.main_horizontal_sizer)

    def _inflate_sizers(self) -> None:
        """
        Insert GUI elements (wx windows) into prepared sizers.
        :return: None
        """
        # Insert GUI widgets into the sizers created above.
        # Logo section -------------------------------------------------------------------------------------------------
        # Create a placeholder image
        self.placeholder_logo_image = wx.Image(Numbers.logo_image_size, Numbers.logo_image_size)
        self.placeholder_logo_image.Replace(0, 0, 0, 245, 255, 255)
        self.menu_logo_image = wx.StaticBitmap(self.right_panel, -1, wx.Bitmap(self.placeholder_logo_image))
        # Set border to the image
        self.menu_logo_static_sizer.Add(self.menu_logo_image, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT, border=1)
        # Create menu logo name text box
        self.field_logo_name = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_menu_logo_name_placeholder,
                                           size=wx.Size(98, 35),
                                           style=wx.TE_MULTILINE | wx.TE_CENTRE | wx.TE_NO_VSCROLL)
        self.field_logo_name.SetFont(self.text_field_font)

        self.field_logo_alt = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_menu_logo_alt_placeholder,
                                          size=wx.Size(98, 45),
                                          style=wx.TE_MULTILINE)
        self.field_logo_name.SetFont(self.text_field_font)
        self.field_logo_title = wx.TextCtrl(self.right_panel, -1,
                                            value=Strings.label_article_menu_logo_title_placeholder,
                                            size=wx.Size(98, 49), style=wx.TE_MULTILINE)
        self.field_logo_name.SetFont(self.text_field_font)
        self.field_logo_alt.SetFont(self.text_field_font)
        self.field_logo_title.SetFont(self.text_field_font)

        self.menu_logo_static_sizer.Add(self.field_logo_name)
        self.menu_logo_static_sizer.Add(self.field_logo_alt)
        self.menu_logo_static_sizer.Add(self.field_logo_title)
        # --------------------------------------------------------------------------------------------------------------

        # File list section --------------------------------------------------------------------------------------------
        self.page_list = wx.ListBox(self.left_panel, wx.LB_SINGLE | wx.LB_SORT)
        self.page_list.SetFont(self.text_field_font)
        # Add the list into the bottom sizer, give it a sizing weight and let it expand vertically
        self.filelist_column_sizer.Add(self.page_list, flag=wx.EXPAND, border=Numbers.widget_border_size, proportion=1)
        # --------------------------------------------------------------------------------------------------------------

        # Article metadata section -------------------------------------------------------------------------------------
        # Add image placeholder into middle top left static sizer
        self.placeholder_main_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        self.placeholder_main_image.Replace(0, 0, 0, 245, 255, 255)
        self.main_image = wx.StaticBitmap(self.right_panel, -1, wx.Bitmap(self.placeholder_main_image))
        self.article_image_static_sizer.Add(self.main_image, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT, border=1)

        # Add text boxes
        self.field_main_image_alt = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_image_alt,
                                                size=wx.Size(160, 30))
        self.field_main_image_title = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_image_title,
                                                  size=wx.Size(160, 30))
        self.field_main_image_name = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_image_name,
                                                 size=wx.Size(160, 30))

        self.field_article_date = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_date,
                                              size=wx.Size(160, 30))
        self.field_article_title = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_title,
                                               size=wx.Size(250, 30))
        self.field_article_keywords = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_keywords,
                                                  size=wx.Size(250, 30))
        self.field_article_description = wx.TextCtrl(self.right_panel, -1, value=Strings.label_article_description,
                                                     size=wx.Size(250, 30))

        self.article_data_static_sizer.Add(self.field_article_date)
        self.article_data_static_sizer.Add(self.field_main_image_name, flag=wx.EXPAND)
        self.article_data_static_sizer.Add(self.field_main_image_title, flag=wx.EXPAND)
        self.article_data_static_sizer.Add(self.field_main_image_alt, flag=wx.EXPAND)
        self.article_data_static_sizer.Add(self.field_article_title, flag=wx.TOP | wx.EXPAND, border=16)
        self.article_data_static_sizer.Add(self.field_article_keywords, flag=wx.EXPAND)
        self.article_data_static_sizer.Add(self.field_article_description, flag=wx.EXPAND)
        # --------------------------------------------------------------------------------------------------------------

        # Main text area section ---------------------------------------------------------------------------------------
        self.main_text_area = rt.RichTextCtrl(self.right_panel, style=wx.VSCROLL)
        self.right_bottom_sizer.Add(self.main_text_area, flag=wx.EXPAND | wx.LEFT | wx.TOP, proportion=1, border=2)
        self.right_bottom_sizer.Add(self.side_photo_column_sizer, flag=wx.EXPAND | wx.LEFT,
                                    border=Numbers.widget_border_size)
        # --------------------------------------------------------------------------------------------------------------
        self.Fit()

    def _bind_handlers(self) -> None:
        """
        Bind event handlers.
        :return: None
        """
        # Binding an event to a handler function, the last parameter is the source of the event. In case of for
        # example buttons, all buttons will create EVT_BUTTON and we will not know which handler to use unless
        # the source is set.
        # Bind window close events, X button and emergency quit
        self.Bind(wx.EVT_CLOSE, self.close_button_handler, self)
        # This calls the quit method if the user logs off the computer
        self.Bind(wx.EVT_QUERY_END_SESSION, self.close_button_handler)

        # Bind menu item clicks
        self.Bind(wx.EVT_MENU, self.about_button_handler, self.help_menu_item_about)
        self.Bind(wx.EVT_MENU, self.open_button_handler, self.file_menu_item_open)
        self.Bind(wx.EVT_MENU, self.quit_button_handler, self.file_menu_item_quit)

        # Bind other controls clicks
        self.Bind(wx.EVT_LISTBOX, self.list_item_click_handler, self.page_list)

    def _set_status_text(self, text: str, position=0) -> None:
        """
        Set a text into a position in status bar and prepend a separator.
        :param text: Text to set.
        :param position: Where to set the text, 0 is default
        :return: None
        """
        to_set = '| ' + text
        self.status_bar.SetStatusText(to_set, position)

    def _disable_editor(self, state) -> None:
        """
        Disable all window controls except menu a title bar.
        :param state: True to disable, False to enable all GUI elements.
        :return: None
        """
        # TODO disable menus except File open directory and quit
        self.Enable()
        if state:
            self.split_screen.Disable()
            self.page_list.Clear()
        else:
            self.split_screen.Enable()
        # Disable toolbar buttons
        for tool_id in self.tool_ids:
            self.tool_bar.EnableTool(tool_id, (not state))
        # Disable menu items
        for menu_item in self.disableable_menu_items:
            menu_item.Enable(not state)

    def _load_working_directory(self, path: str) -> None:
        """
        Load a working directory into the editor.
        :param path: str, path to the working directory
        :return: None
        """
        # Disable the gui until load is done
        self.Disable()
        self._set_status_text(Strings.status_loading, 3)
        self._set_status_text(('Work dir: ' + str(path)), 1)
        file_list_thread = FileListThread(self, self.EVT_CARRIER_TYPE_ID, str(path))
        file_list_thread.start()

    def _show_error_dialog(self, error: str) -> None:
        """
        Display an error dialog with the error text. Set error state into the status bar.
        :param error: The error to display in the dialog.
        :return: None
        """
        wx.MessageBox(error, Strings.status_error, wx.OK | wx.ICON_ERROR)
        self._set_status_text(Strings.status_error, 2)

    def on_filelist_load_fail(self, e: Exception) -> None:
        """
        If the loading of a supposed whitebear directory fails, this method is called, it shows the error and disables
        all editor functionality except the load new directory button.
        :param e: Exception that caused the call of this method.
        :return: None
        """
        # TODO open dialog and append the error to its log
        self._show_error_dialog(str(e))
        self._disable_editor(True)

    def on_filelist_loaded(self, documents: Dict[str, WhitebearDocument]) -> None:
        """
        This method fills up the left side page file list and is called when the FileListThread finishes.
        :param documents: Dictionary of file names and documents of article pages {file name, WhitebearDocument, ...}
        :return: None
        """
        self.document_dictionary = documents
        self.page_list.Clear()
        self.page_list.InsertItems(sorted(list(self.document_dictionary.keys())), 0)
        # Select last used document
        last_document = self.config_manager.get_last_document()
        if last_document:
            self.page_list.SetStringSelection(last_document)
            list_event = wx.CommandEvent()
            list_event.SetString(last_document)
            self.list_item_click_handler(list_event)

        os.chdir(self.config_manager.get_working_dir())
        # Enable GUI when the load is done
        self._set_status_text(Strings.status_ready, 3)
        self._set_status_text(Strings.status_articles + ' ' + str(len(self.document_dictionary)), 2)
        self._disable_editor(False)

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
        # If the built in close function is not called, destroy must be called explicitly, calling Close runs the close
        # handler.
        self.Destroy()

    def open_button_handler(self, event):
        """
        Handle opening a new working directory. Show a selection dialog, store the new directory and load it into
        editor.
        :param event: Not used.
        :return: None
        """
        dlg = wx.DirDialog(self, Strings.label_dialog_choose_wb_dir, Strings.home_directory,
                           wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
        # Modal means the user is locked into this dialog an can not use the rest of the application
        if dlg.ShowModal() == wx.ID_OK:
            self.config_manager.store_working_dir(dlg.GetPath())
            self._load_working_directory(self.config_manager.get_working_dir())
        # This must be called, the dialog stays in memory so you can retrieve data and would not be destroyed.
        dlg.Destroy()

    def about_button_handler(self, event):
        """
        Handles clicks onto the About button. Displays a short message in another window.
        :param event: Not used.
        :return: None
        """
        AboutDialog(self)

    def list_item_click_handler(self, event):
        """
        Handler function for clicking a page name in the web page list. Shows which website is selected in the status
        bar.
        :param event: wx event, brings the selected string from the menu.
        :return: None
        """
        selected_name = event.GetString()
        # Validate the selected document
        # TODO do this in a separate thread
        try:
            result = self.document_dictionary[selected_name].validate_self()
            if result[0]:
                self._set_status_text(Strings.status_valid + ' ' + selected_name)
                # Parse the document, this must be done after self validation.
                self.document_dictionary[selected_name].parse_self()

                self.SetTitle(selected_name)
            else:
                self._set_status_text(Strings.status_invalid + ' ' + selected_name)
                # Prepare error string from all validation errors
                error_string = Strings.exception_html_syntax_error + ': ' + selected_name + '\n'
                for message in result[1]:
                    error_string = error_string + message + '\n'
                self._show_error_dialog(error_string)
                self._disable_editor(True)
                return
        except UnrecognizedFileException as e:
            self._show_error_dialog(str(e))
            self._disable_editor(True)
