import os
from typing import Dict, List

import wx
import wx.richtext as rt

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Gui.Dialogs.AboutDialog import AboutDialog
from Gui.Dialogs.AddImageDialog import AddImageDialog
from Gui.Dialogs.AddLogoDialog import AddLogoDialog
from Gui.Dialogs.EditAsideImageDialog import EditAsideImageDialog
from Gui.Dialogs.EditMenuItemDialog import EditMenuItemDialog
from Gui.Dialogs.LoadingDialog import LoadingDialog
from Gui.Panels.AsideImagePanel import AsideImagePanel
from Gui.Panels.CustomRichText import CustomRichText
from Resources.Fetch import Fetch
from Threads.FileListThread import FileListThread
from Tools.ConfigManager import ConfigManager
from Tools.Document.AsideImage import AsideImage
from Tools.Document.MenuItem import MenuItem
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Tools import Tools


class MainFrame(wx.Frame):
    """
    Main GUI controlling class. The Frame is actually the on screen window.
    """
    VIDEO_TOOL_ID: int = wx.NewId()
    IMAGE_TOOL_ID: int = wx.NewId()

    def __init__(self):
        """
        Constructor for the GUI of the editor. This is the main frame so we pass None as the parent.
        """
        # -1 is a special ID which generates a random wx ID
        super(MainFrame, self).__init__(None, -1, title=Strings.editor_name, style=wx.DEFAULT_FRAME_STYLE)

        # Create font for text fields
        self.menu_text_field_font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        # Prepare data objects
        self._config_manager = ConfigManager()
        self._tool_ids = []
        self._disableable_menu_items = []
        self._document_dictionary = {}
        self._current_document_name = None
        self._current_document_instance = None
        self._css_document = None
        self._loading_dlg = None
        self._ignore_change = False
        self._no_save = False

        self._search_term = None
        self._search_results: List[int] = []
        self._search_index: int = 0
        self._text_changed: bool = False

        self._init_status_bar()
        self._init_menu()
        self._init_sizers_panels()
        self._inflate_sizers()
        self._bind_handlers()
        self._init_top_tool_bar()
        self._setup_main_text_area()

        # Set minimal size of the frame on screen, smaller frame would squish GUI too much.
        self.SetMinClientSize(wx.Size(Numbers.minimal_window_size_width, Numbers.minimal_window_size_height))

        # Prepare frame contents
        # Load last working directory
        self._set_status_text(Strings.status_loading, 3)
        self._load_working_directory(self._config_manager.get_working_dir())

        # Load last window position and size
        self.SetPosition((self._config_manager.get_window_position()))
        size = self._config_manager.get_window_size()
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
        self._menu_bar = wx.MenuBar()
        self._file_menu = wx.Menu(style=wx.MENU_TEAROFF)
        self._help_menu = wx.Menu(style=wx.MENU_TEAROFF)
        self._edit_menu = wx.Menu(style=wx.MENU_TEAROFF)
        self._add_menu = wx.Menu(style=wx.MENU_TEAROFF)

        # Add the file menu into the menu bar.
        self._menu_bar.Append(self._file_menu, Strings.label_menu_file)
        self._menu_bar.Append(self._edit_menu, Strings.label_menu_edit)
        self._menu_bar.Append(self._add_menu, Strings.label_menu_add)
        self._menu_bar.Append(self._help_menu, Strings.label_menu_help)

        # File menu ----------------------------------------------------------------------------------------------------
        # Create a menu item for open
        self._file_menu_item_new = wx.MenuItem(self._file_menu, wx.ID_NEW, Strings.label_menu_item_new,
                                               Strings.label_menu_item_new_hint)

        self._file_menu_item_open = wx.MenuItem(self._file_menu, wx.ID_OPEN, Strings.label_menu_item_open,
                                                Strings.label_menu_item_open_hint)

        self._file_menu_item_save = wx.MenuItem(self._file_menu, wx.ID_SAVE, Strings.label_menu_item_save,
                                                Strings.label_menu_item_save_hint)
        self._disableable_menu_items.append(self._file_menu_item_save)

        self._file_menu_item_reload = wx.MenuItem(self._file_menu, wx.ID_REFRESH, Strings.label_menu_item_reload,
                                                  Strings.label_menu_item_reload_hint)
        self._disableable_menu_items.append(self._file_menu_item_reload)

        self._file_menu_item_quit = wx.MenuItem(self._file_menu, wx.ID_CLOSE, Strings.label_menu_item_quit,
                                                Strings.label_menu_item_quit_hint)

        self._file_menu_item_upload = wx.MenuItem(self._file_menu, wx.ID_EXECUTE, Strings.label_menu_item_upload,
                                                  Strings.label_menu_item_upload_hint)
        self._disableable_menu_items.append(self._file_menu_item_upload)

        # Put menu items into the menu buttons
        self._file_menu.Append(self._file_menu_item_new)
        self._file_menu.Append(self._file_menu_item_open)
        self._file_menu.Append(self._file_menu_item_save)
        self._file_menu.AppendSeparator()
        self._file_menu.Append(self._file_menu_item_reload)
        self._file_menu.Append(self._file_menu_item_upload)
        self._file_menu.Append(self._file_menu_item_quit)

        # Edit menu ----------------------------------------------------------------------------------------------------
        self._edit_menu_item_undo = wx.MenuItem(self._edit_menu, wx.ID_UNDO, Strings.label_menu_item_undo,
                                                Strings.label_menu_item_undo_hint)
        self._disableable_menu_items.append(self._edit_menu_item_undo)
        self._edit_menu_item_redo = wx.MenuItem(self._edit_menu, wx.ID_REDO, Strings.label_menu_item_redo,
                                                Strings.label_menu_item_redo_hint)
        self._disableable_menu_items.append(self._edit_menu_item_redo)
        self._edit_menu_item_paste = wx.MenuItem(self._edit_menu, wx.ID_PASTE, Strings.label_menu_item_paste,
                                                 Strings.label_menu_item_paste_hint)
        self._disableable_menu_items.append(self._edit_menu_item_paste)
        self._edit_menu_item_copy = wx.MenuItem(self._edit_menu, wx.ID_COPY, Strings.label_menu_item_copy,
                                                Strings.label_menu_item_copy_hint)
        self._disableable_menu_items.append(self._edit_menu_item_copy)
        self._edit_menu_item_cut = wx.MenuItem(self._edit_menu, wx.ID_CUT, Strings.label_menu_item_cut,
                                               Strings.label_menu_item_cut_hint)
        self._disableable_menu_items.append(self._edit_menu_item_cut)
        self._edit_menu_item_select_all = wx.MenuItem(self._edit_menu, wx.ID_SELECTALL,
                                                      Strings.label_menu_item_select_all,
                                                      Strings.label_menu_item_select_all_hint)
        self._disableable_menu_items.append(self._edit_menu_item_select_all)

        self._edit_menu.Append(self._edit_menu_item_undo)
        self._edit_menu.Append(self._edit_menu_item_redo)
        self._edit_menu.Append(self._edit_menu_item_copy)
        self._edit_menu.Append(self._edit_menu_item_cut)
        self._edit_menu.Append(self._edit_menu_item_paste)
        self._edit_menu.Append(self._edit_menu_item_select_all)

        # Add menu ---------------------------------------------------------------------------------------------------
        self._add_menu_item_add_image = wx.MenuItem(self._add_menu, wx.ID_ADD, Strings.label_menu_item_add_text_image,
                                                    Strings.label_menu_item_add_text_image_hint)
        self._disableable_menu_items.append(self._add_menu_item_add_image)
        self._add_menu_item_add_logo = wx.MenuItem(self._add_menu, wx.ID_FILE1, Strings.label_menu_item_add_logo,
                                                   Strings.label_menu_item_add_logo_hint)
        self._disableable_menu_items.append(self._add_menu_item_add_logo)
        self._add_menu_item_side_image = wx.MenuItem(self._add_menu, wx.ID_FILE2,
                                                     Strings.label_menu_item_add_side_image,
                                                     Strings.label_menu_item_add_side_image_hint)
        self._disableable_menu_items.append(self._add_menu_item_side_image)

        self._add_menu.Append(self._add_menu_item_side_image)
        self._add_menu.AppendSeparator()
        self._add_menu.Append(self._add_menu_item_add_image)
        self._add_menu.Append(self._add_menu_item_add_logo)

        # About menu ---------------------------------------------------------------------------------------------------
        self._help_menu_item_about = wx.MenuItem(self._help_menu, wx.ID_ABOUT, Strings.label_menu_item_about,
                                                 Strings.label_menu_item_about_hint)
        self._disableable_menu_items.append(self._help_menu_item_about)
        self._help_menu.Append(self._help_menu_item_about)

        self.SetMenuBar(self._menu_bar)

    def _add_tool_id(self) -> wx.NewId():
        """
        Create and return a new wx ID for a tool in the toolbar, at the same time save the id in a list that is used
        to keep tract of all toolbar tools.
        :return: New wx ID.
        """
        new_id = wx.NewId()
        self._tool_ids.append(new_id)
        return new_id

    @staticmethod
    def _scale_icon(name: str) -> wx.Bitmap:
        """
        Helper method to prepare icons for toolbar.
        :return: The icon bitmap
        """
        path = Fetch.get_resource_path(name)
        image = wx.Image(path, wx.BITMAP_TYPE_ANY)
        image = image.Scale(Numbers.icon_width, Numbers.icon_height, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image)

    def _init_top_tool_bar(self) -> None:
        """
        Set up top tool bar for the frame.
        :return: None
        """
        self.tool_bar: wx.ToolBar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)
        # Add toolbar tools
        self._new_file_tool = self.tool_bar.AddTool(self._add_tool_id(), Strings.toolbar_new_file,
                                                    self._scale_icon('new-file.png'),
                                                    Strings.toolbar_new_file)
        self._save_tool = self.tool_bar.AddTool(self._add_tool_id(), Strings.toolbar_save,
                                                self._scale_icon('save.png'),
                                                Strings.toolbar_save)
        self.insert_img_tool = self.tool_bar.AddTool(MainFrame.IMAGE_TOOL_ID, Strings.toolbar_insert_img,
                                                     self._scale_icon('insert-image.png'),
                                                     Strings.toolbar_insert_img)
        self.insert_video_tool = self.tool_bar.AddTool(MainFrame.VIDEO_TOOL_ID, Strings.toolbar_insert_video,
                                                       self._scale_icon('insert-video.png'),
                                                       Strings.toolbar_insert_video)
        self.bold_tool = self.tool_bar.AddTool(self._add_tool_id(), Strings.toolbar_bold,
                                               self._scale_icon('bold.png'),
                                               Strings.toolbar_bold)
        self.Bind(wx.EVT_MENU, self._forward_event, self.insert_img_tool)
        self.Bind(wx.EVT_MENU, self._forward_event, self.insert_video_tool)
        self.Bind(wx.EVT_MENU, self._forward_event, self.bold_tool)
        self.Bind(wx.EVT_MENU, self._save_document_handler, self._save_tool)

        self._search_box = wx.TextCtrl(self.tool_bar, wx.ID_FIND, style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self._search_box_handler, self._search_box)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_tools_handler, self._search_box)

        self.tool_bar.Realize()

    def _init_search_box(self) -> None:
        """
        Add search box into the top tool bar.
        :return: None
        """
        if not self.tool_bar.FindById(wx.ID_FIND):
            # Only add the search box once and not when a new directory is loaded again.
            self.tool_bar.AddSeparator()
            self.tool_bar.AddControl(self._search_box)

    def _create_color_tool(self, name: str, toolbar: wx.ToolBar, color: wx.Colour) -> None:
        """
        Create a tool for the toolbar with  a colored square button only if the tool does not exist already.
        :param name: Name of the color
        :param toolbar: Application's toolbar
        :param color: The color to use.
        :return: None
        """
        for tool_id in self._tool_ids:
            tool: wx.ToolBarToolBase = self.tool_bar.FindById(tool_id)
            if tool.GetShortHelp() == name:
                # Do not recreate tools on working directory reload, only create potential new color tools.
                return
        bmp = self._make_bitmap(color)
        tool = toolbar.AddTool(self._add_tool_id(), Strings.toolbar_color, bmp, name)
        self.Bind(wx.EVT_MENU, self._change_color, tool)

    @staticmethod
    def _make_bitmap(color: wx.Colour) -> wx.Bitmap:
        """
        Create a colored bitmap for a toolbar button
        :param color: The color to use.
        :return: wx.Bitmap
        """
        bmp = wx.Bitmap(Numbers.color_icon_height, Numbers.color_icon_width)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(color))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def _init_status_bar(self) -> None:
        """
        Set up status bar for the frame.
        :return: None
        """
        # Create a status bar with 3 fields
        self._status_bar = self.CreateStatusBar(4)
        self._status_bar.SetStatusWidths([-6, -7, -2, -2])
        # Initialize status bar
        self._set_status_text('', 0)
        self._set_status_text('', 1)

    def _init_sizers_panels(self) -> None:
        """
        Set up sizers for the frame
        :return: None
        """
        # Create splitter window, This allows the file list to expand left.
        self._split_screen = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_NOBORDER)
        self._split_screen.SetMinimumPaneSize(Numbers.minimal_panel_size)
        # Create panels that go into the splitter window
        self._left_panel = wx.Panel(self._split_screen, style=wx.SUNKEN_BORDER)
        self._right_panel = wx.Panel(self._split_screen, style=wx.SUNKEN_BORDER)
        # Limit how far the file list can expand to prevent GUI from being squished too much.
        self._right_panel.SetMinSize((600, -1))
        self._split_screen.SplitVertically(self._left_panel, self._right_panel, Numbers.initial_panel_size)

        # Create a global sizer that contains the splitter window which contains the rest.
        self._main_horizontal_sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_horizontal_sizer.Add(self._split_screen, 1, wx.EXPAND)

        # Create sizers that go into the panels.
        # Contains file list of pages
        self._filelist_column_sizer = wx.BoxSizer(wx.VERTICAL)
        self._style_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._left_panel, label=Strings.label_styles)

        self._right_main_vertical_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._middle_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._right_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        # Contains main article image
        self._article_image_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._right_panel,
                                                             label=Strings.label_article_image)
        # Contains article metadata controls
        self._article_data_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._right_panel,
                                                            label=Strings.label_article_info)
        # Contains menu logo controls
        self._menu_logo_static_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._right_panel,
                                                         label=Strings.label_article_menu_logo)
        # Contains main text area, middle top sizer
        self._middle_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        # Contains article photos
        self._side_photo_column_sizer = wx.StaticBoxSizer(wx.VERTICAL, self._right_panel,
                                                          label=Strings.label_article_photo_column)
        self._side_photo_column_sizer.SetMinSize((Numbers.photo_column_width, -1))
        self._right_vertical_sizer.Add(self._article_image_static_sizer, flag=wx.ALIGN_LEFT | wx.RIGHT, border=0)
        self._right_vertical_sizer.Add(self._side_photo_column_sizer, flag=wx.EXPAND, proportion=1,
                                       border=Numbers.widget_border_size)
        # The | is a bitwise or and flags is a bit mask of constants
        self._middle_vertical_sizer.Add(self._middle_top_sizer, flag=wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND,
                                        border=Numbers.widget_border_size, proportion=0)
        self._right_main_vertical_sizer.Add(self._middle_vertical_sizer, border=Numbers.widget_border_size,
                                            proportion=1,
                                            flag=wx.RIGHT | wx.LEFT | wx.ALIGN_LEFT | wx.EXPAND)
        self._right_main_vertical_sizer.Add(self._right_vertical_sizer, flag=wx.EXPAND | wx.RIGHT, proportion=0,
                                            border=Numbers.widget_border_size)
        self._middle_top_sizer.Add(self._menu_logo_static_sizer, 0, flag=wx.EXPAND, border=Numbers.widget_border_size)
        self._middle_top_sizer.Add(self._article_data_static_sizer, 1, flag=wx.EXPAND | wx.LEFT,
                                   border=Numbers.widget_border_size)
        # Insert sizers with GUI into the respective panels, these are inserted into the splitter windows.s
        self._left_panel.SetSizer(self._filelist_column_sizer)
        self._right_panel.SetSizer(self._right_main_vertical_sizer)
        self.SetSizer(self._main_horizontal_sizer)

    def _inflate_sizers(self) -> None:
        """
        Insert GUI elements (wx windows) into prepared sizers.
        :return: None
        """
        # Insert GUI widgets into the sizers created above.
        # Logo section -------------------------------------------------------------------------------------------------
        # Create a placeholder image
        placeholder_logo_image = wx.Image(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        placeholder_logo_image.Replace(0, 0, 0, 245, 255, 255)
        self._menu_logo_button = wx.Button(self._right_panel, -1, style=wx.BU_EXACTFIT | wx.BORDER_NONE)
        self._menu_logo_button.SetBitmap(wx.Bitmap(placeholder_logo_image))
        # self._menu_logo_name = wx.StaticText(self.right_panel, -1, Strings.label_article_image_caption)
        # Set border to the image
        self._menu_logo_static_sizer.Add(self._menu_logo_button, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT,
                                         border=Numbers.widget_border_size)
        # Create menu logo name text box
        self._text_menu_item_name = wx.StaticText(self._right_panel, -1,
                                                  Strings.label_article_menu_logo_name_placeholder,
                                                  style=wx.ALIGN_CENTRE_HORIZONTAL)
        self._text_menu_item_name.SetFont(self.menu_text_field_font)
        self._text_menu_item_name.SetMaxSize((Numbers.menu_logo_image_size, 30))
        self._menu_logo_static_sizer.Add(self._text_menu_item_name, flag=wx.CENTER)
        # --------------------------------------------------------------------------------------------------------------

        # File list section --------------------------------------------------------------------------------------------
        self._style_picker = wx.ListBox(self._left_panel, -1, size=(-1, 160))
        self._style_sizer.Add(self._style_picker, 1, flag=wx.EXPAND)
        self._file_list = wx.ListCtrl(self._left_panel, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self._file_list.SetFont(self.menu_text_field_font)
        self._filelist_column_sizer.Add(self._style_sizer, flag=wx.EXPAND, border=Numbers.widget_border_size)
        # Add the list into the bottom sizer, give it a sizing weight and let it expand vertically
        self._filelist_column_sizer.Add(self._file_list, flag=wx.EXPAND, border=Numbers.widget_border_size,
                                        proportion=1)
        # --------------------------------------------------------------------------------------------------------------

        # Article metadata section -------------------------------------------------------------------------------------
        # Add image placeholder into middle top left static sizer
        placeholder_main_image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_main_image.Replace(0, 0, 0, 245, 255, 255)
        self._main_image_button = wx.Button(self._right_panel, -1, style=wx.BU_EXACTFIT | wx.BORDER_NONE)
        self._main_image_button.SetBitmap(wx.Bitmap(placeholder_main_image))
        self._text_main_image_caption = wx.StaticText(self._right_panel, -1, Strings.label_article_image_caption,
                                                      style=wx.ST_ELLIPSIZE_END)
        self._text_main_image_caption.SetMaxSize((Numbers.main_image_width - 5, -1))
        self._article_image_static_sizer.Add(self._main_image_button, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT,
                                             border=Numbers.widget_border_size)
        self._article_image_static_sizer.Add(self._text_main_image_caption, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT,
                                             border=Numbers.widget_border_size)

        # Add text boxes
        self._field_article_date = wx.TextCtrl(self._right_panel, -1, value=Strings.label_article_date,
                                               size=wx.Size(160, 30))
        self._field_article_date_tip = Tools.get_warning_tip(self._field_article_date, Strings.label_article_date)

        self._field_article_name = wx.TextCtrl(self._right_panel, -1, value=Strings.label_article_title,
                                               size=wx.Size(-1, 43))
        font: wx.Font = self._field_article_name.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(Numbers.main_heading_size)
        self._field_article_name.SetFont(font)
        self._field_article_name_tip = Tools.get_warning_tip(self._field_article_name, Strings.label_article_title)

        self._field_article_keywords = wx.TextCtrl(self._right_panel, -1, value=Strings.label_article_keywords,
                                                   size=wx.Size(-1, 30))
        self._field_article_keywords_tip = Tools.get_warning_tip(self._field_article_keywords,
                                                                 Strings.label_article_keywords)

        self._field_article_description = wx.TextCtrl(self._right_panel, -1, value=Strings.label_article_description,
                                                      size=wx.Size(-1, 60), style=wx.TE_MULTILINE)
        self._field_article_description_tip = Tools.get_warning_tip(self._field_article_description,
                                                                    Strings.label_article_description)

        date_keywords_sizer = wx.BoxSizer(wx.HORIZONTAL)
        date_keywords_sizer.Add(self._field_article_keywords, 1, flag=wx.EXPAND)
        date_keywords_sizer.Add(self._field_article_date)
        self._article_data_static_sizer.Add(date_keywords_sizer, flag=wx.EXPAND)
        self._article_data_static_sizer.Add(self._field_article_description, flag=wx.EXPAND)
        self._article_data_static_sizer.Add(self._field_article_name, 1, flag=wx.EXPAND)
        # --------------------------------------------------------------------------------------------------------------

        # Aside images section -----------------------------------------------------------------------------------------
        self._side_photo_panel = AsideImagePanel(self._right_panel)
        self._side_photo_column_sizer.Add(self._side_photo_panel, 1, flag=wx.EXPAND)
        self.Fit()

    def _setup_main_text_area(self) -> None:
        """
        This is in separate method because it has to be run once other object are created.
        :return: None
        """
        # Main text area section ---------------------------------------------------------------------------------------
        self._main_text_area = CustomRichText(MainFrame.IMAGE_TOOL_ID, MainFrame.VIDEO_TOOL_ID, self._style_picker,
                                              self._right_panel, style=wx.VSCROLL)
        self._middle_vertical_sizer.Add(self._main_text_area, flag=wx.EXPAND | wx.TOP, proportion=1,
                                        border=Numbers.widget_border_size)
        self.Bind(wx.EVT_TEXT, self._repeat_search, self._main_text_area)
        # --------------------------------------------------------------------------------------------------------------

    def _bind_handlers(self) -> None:
        """
        Bind event handlers.
        :return: None
        """
        # Binding an event to a handler function, the last parameter is the source of the event. In case of for
        # example buttons, all buttons will create EVT_BUTTON and we will not know which handler to use unless
        # the source is set.
        # Bind window close events, X button and emergency quit
        self.Bind(wx.EVT_CLOSE, self._close_button_handler, self)
        # This calls the quit method if the user logs off the computer
        self.Bind(wx.EVT_QUERY_END_SESSION, self._close_button_handler)
        self.Bind(wx.EVT_ACTIVATE, self._refresh_aside_images)

        # Bind a handler that changes selected document color if an edit happens in other controls.
        self.Bind(wx.EVT_COLOUR_CHANGED, self._text_area_edit_handler)

        # Bind menu item clicks
        self.Bind(wx.EVT_MENU, self._about_button_handler, self._help_menu_item_about)
        self.Bind(wx.EVT_MENU, self._open_button_handler, self._file_menu_item_open)
        self.Bind(wx.EVT_MENU, self._quit_button_handler, self._file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self._reload_button_handler, self._file_menu_item_reload)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_cut)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_copy)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_paste)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_undo)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_redo)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_select_all)
        self.Bind(wx.EVT_MENU, self._add_image_handler, self._add_menu_item_add_image)
        self.Bind(wx.EVT_MENU, self._insert_aside_image_handler, self._add_menu_item_side_image)
        self.Bind(wx.EVT_MENU, self._add_menu_logo_handler, self._add_menu_item_add_logo)

        # Bind other controls clicks
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._list_item_click_handler, self._file_list)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self._splitter_size_change_handler, self._split_screen)
        self.Bind(wx.EVT_BUTTON, self._main_image_handler, self._main_image_button)
        self.Bind(wx.EVT_BUTTON, self._menu_logo_handler, self._menu_logo_button)
        self.Bind(wx.EVT_TEXT, self._handle_name_change, self._field_article_name)
        self.Bind(wx.EVT_TEXT, self._handle_date_change, self._field_article_date)
        self.Bind(wx.EVT_TEXT, self._handle_keywords_change, self._field_article_keywords)
        self.Bind(wx.EVT_TEXT, self._handle_description_change, self._field_article_description)
        self.Bind(wx.EVT_LISTBOX, self._forward_event, self._style_picker)

        # Initialize search shortcut into accelerator table
        new_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self._focus_to_search, id=new_id)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), new_id)])
        self.SetAcceleratorTable(accel_tbl)

    # noinspection PyUnusedLocal
    def _focus_to_search(self, event: wx.CommandEvent) -> None:
        """
        Handles Ctrl+F shortcut to set focus into the search box.
        :param event: Not used
        :return: None
        """
        self._search_box.SetFocus()

    def _refresh_aside_images(self, event: wx.ActivateEvent) -> None:
        """
        Refresh the side image panel to fix wrong borders if the window started minimized.
        :param event: Used to detect when the window is being activated.
        :return: None
        """
        if self._side_photo_panel:
            if event.GetActive():
                self._side_photo_panel.show_images()

    def _set_status_text(self, text: str, position=0) -> None:
        """
        Set a text into a position in status bar and prepend a separator.
        :param text: Text to set.
        :param position: Where to set the text, 0 is default
        :return: None
        """
        to_set = '| ' + text
        self._status_bar.SetStatusText(to_set, position)

    def _disable_editor(self, state, leave_files: bool = False) -> None:
        """
        Disable all window controls except menu a title bar.
        :param state: True to disable, False to enable all GUI elements.
        :param leave_files: If True the file list will not be disabled.
        :return: None
        """
        self.Enable()
        if state:
            if not leave_files:
                self._split_screen.Disable()
                self._file_list.SetBackgroundColour(wx.LIGHT_GREY)
                self._file_list.SetForegroundColour(wx.LIGHT_GREY)
            else:
                self._split_screen.Enable()
                self._right_panel.Disable()
                self._style_picker.Disable()
                self._file_list.SetBackgroundColour(wx.WHITE)
                self._file_list.SetForegroundColour(wx.BLACK)
        else:
            self._split_screen.Enable()
            self._left_panel.Enable()
            self._right_panel.Enable()
            self._file_list.SetBackgroundColour(wx.WHITE)
            self._file_list.SetForegroundColour(wx.BLACK)
        # Disable toolbar buttons
        for tool_id in self._tool_ids:
            self.tool_bar.EnableTool(tool_id, (not state))
        self.tool_bar.EnableTool(MainFrame.IMAGE_TOOL_ID, (not state))
        self.tool_bar.EnableTool(MainFrame.VIDEO_TOOL_ID, (not state))
        # Disable menu items
        for menu_item in self._disableable_menu_items:
            menu_item.Enable(not state)

    def _load_working_directory(self, path: str) -> None:
        """
        Load a working directory into the editor.
        :param path: str, path to the working directory
        :return: None
        """
        self._loading_dlg = LoadingDialog(None)
        self._loading_dlg.Show()
        # Disable the gui until load is done
        self.Disable()
        self._set_status_text(Strings.status_loading, 3)
        self._set_status_text(('Work dir: ' + str(path)), 1)
        self._set_status_text(Strings.status_ready, 0)
        file_list_thread = FileListThread(self, str(path))
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
        self._loading_dlg.Destroy()
        self._show_error_dialog(str(e))
        self._disable_editor(True)
        self._side_photo_panel.reset()
        self._clear_editor()

    def on_css_parsed(self, css: WhitebearDocumentCSS) -> None:
        """
        Generates text color tools in tool bar once css is parsed.
        :param css: The parsed css file.
        :return: None
        """
        self._css_document = css
        css_colors = css.get_colors()
        for name, color in css_colors.items():
            self._create_color_tool(name, self.tool_bar, color)
        self._init_search_box()

    def on_filelist_loaded(self, documents: Dict[str, WhitebearDocumentArticle]) -> None:
        """
        This method fills up the left side page file list and is called when the FileListThread finishes.
        :param documents: Dictionary of file names and documents of article pages {file name, WhitebearDocument, ...}
        :return: None
        """
        self._disable_editor(True, leave_files=True)
        self._document_dictionary = documents
        MainFrame.LOADED_PAGES = list(documents.keys())
        self._file_list.ClearAll()
        self._file_list.InsertColumn(0, Strings.label_filelist, format=wx.LIST_FORMAT_LEFT)
        self._file_list.SetColumnWidth(0, self._left_panel.GetSize()[0])
        for document_name in sorted(list(self._document_dictionary.keys()), reverse=True):
            status_color = self._document_dictionary[document_name].get_status_color()
            self._file_list.InsertItem(0, document_name)
            self._file_list.SetItemBackgroundColour(0, status_color)

        # Select last used document
        last_document = self._config_manager.get_last_document()
        if last_document:
            self._file_list.Select(self._file_list.FindItem(0, last_document))

        os.chdir(self._config_manager.get_working_dir())
        # Enable GUI when the load is done
        self._set_status_text(Strings.status_ready, 3)
        self._set_status_text(Strings.status_articles + ' ' + str(len(self._document_dictionary)), 2)
        self._loading_dlg.Destroy()

    def _forward_event(self, evt) -> None:
        """
        The RichTextCtrl can handle menu and update events for undo, redo, cut, copy, paste, delete, and select all,
        so just forward the event to it.
        :param evt: Event to forward
        :return: None
        """
        self._main_text_area.ProcessEvent(evt)

    def _change_color(self, evt: wx.CommandEvent) -> None:
        """
        Color text based on which button was clicked.
        :param evt: Used to get which color to use.
        :return:
        """
        tool: wx.ToolBarToolBase = self.tool_bar.FindById(evt.GetId())
        color = self._css_document.translate_str_color(tool.GetShortHelp())
        if self._main_text_area.HasSelection():
            self._main_text_area.BeginBatchUndo(Strings.undo_last_action)
            color_range: rt.RichTextRange = self._main_text_area.GetSelectionRange()
            p1: rt.RichTextParagraph = self._main_text_area.GetFocusObject().GetParagraphAtPosition(color_range[0])
            p2: rt.RichTextParagraph = self._main_text_area.GetFocusObject().GetParagraphAtPosition(color_range[1])

            # Check the beginning of the selection.
            if p1.GetAttributes().GetFontFaceName() == Strings.style_heading_3 or \
                    p1.GetAttributes().GetFontFaceName() == Strings.style_heading_4:
                p_range: rt.RichTextRange = p1.GetRange()
                # Extend the beginning of the selected range.
                color_range.SetStart(p_range.GetStart())

            # Check the end of the selection.
            if p2.GetAttributes().GetFontFaceName() == Strings.style_heading_3 or \
                    p2.GetAttributes().GetFontFaceName() == Strings.style_heading_4:
                p_range: rt.RichTextRange = p2.GetRange()
                # Extend the beginning of the selected range.
                color_range.SetEnd(p_range.GetEnd())

            # Change the color of the complete selection.
            for char in range(color_range[0], color_range[1]):
                if char + 1 > color_range[1] + 1:
                    break
                single_range = rt.RichTextRange(char, char + 1)
                # Get the attributes of the single char range and modify them in place. Otherwise changing paragraph.
                # style is broken since the attributes are reset for the range.
                attr = rt.RichTextAttr()
                self._main_text_area.GetStyleForRange(single_range, attr)
                # Ignore links.
                if attr.HasURL():
                    continue
                attr.SetTextColour(color)
                self._main_text_area.SetStyleEx(single_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)
            self._main_text_area.EndBatchUndo()
        else:
            self._main_text_area.BeginTextColour(color)

    def _save(self, confirm=False) -> bool:
        """
        Save current document onto disk.
        :param confirm: Require user confirmation.
        :return: True if saved successfully.
        """
        # todo Save as
        # Force save current document.
        if confirm:
            result = wx.MessageBox(Strings.label_menu_item_save_hint, Strings.toolbar_save, wx.YES_NO | wx.ICON_WARNING)
            if result == wx.NO:
                return False
        self._disable_editor(True)
        self._main_text_area.convert_document()
        # We know here that the document is modified because we are saving it.
        self._current_document_instance.set_status_color(Numbers.BLUE_COLOR)
        self._current_document_instance.seo_test_self()
        self._update_file_color(self._file_list.FindItem(-1, self._current_document_instance.get_filename()))
        # TODO convert document into html. Do this in a separate thread.
        self._current_document_instance.convert_to_html()
        self._current_document_instance.get_menu_section().convert_to_html()
        # TODO convert corresponding menu page.
        self._disable_editor(False)
        return True

    # noinspection PyUnusedLocal
    def _main_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle click on the main image button,
        :param event: Not used
        :return: None
        """
        main_image: AsideImage = self._current_document_instance.get_article_image()
        edit_dialog = EditAsideImageDialog(self, main_image, self._config_manager.get_working_dir())
        edit_dialog.ShowModal()
        self._update_article_image_sizer(main_image)
        self._update_file_color()
        edit_dialog.Destroy()

    # noinspection PyUnusedLocal
    def _menu_logo_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle click on the menu logo button,
        :param event: Not used
        :return: None
        """
        menu_item: MenuItem = self._current_document_instance.get_menu_item()
        edit_dialog = EditMenuItemDialog(self, menu_item, self._config_manager.get_working_dir())
        # We first need to show the dialog so that the name label can calculate it's size and then switch to modal.
        edit_dialog.Show()
        edit_dialog.display_dialog_contents()
        edit_dialog.ShowModal()
        self._update_menu_sizer(menu_item)
        self._update_file_color()
        edit_dialog.Destroy()

    # noinspection PyUnusedLocal
    def _quit_button_handler(self, event) -> None:
        """
        Handles clicks to the Quit button in File menu. Calls Close function which sends EVT_CLOSE and triggers
        close_button_handler() which does all the saving work.
        :param event: Not used
        :return: None
        """
        self.Close(True)

    def _close_button_handler(self, event):
        """
        Handle user exit from the editor. Save last known window position, size and last opened document.
        :param event: CloseEvent, if CanVeto is False the window must be destroyed the system is forcing it.
        :return: None
        """
        if event.CanVeto():
            # Save window position
            self._config_manager.store_window_position(self.GetScreenPosition())
            # Save window size
            if self.IsMaximized():
                # Special value to indicate maximized window
                self._config_manager.store_window_size((-1, -1))
            else:
                self._config_manager.store_window_size(self.GetSize())
            # Store last selected document
            selected_page = self._file_list.GetFirstSelected()
            if selected_page != wx.NOT_FOUND:
                self._config_manager.store_last_open_document(self._file_list.GetItemText(selected_page, 0))
            if self._current_document_instance:
                self._save(confirm=True)
        # If the built in close function is not called, destroy must be called explicitly, calling Close runs the close
        # handler.
        self.Destroy()

    # noinspection PyUnusedLocal
    def _open_button_handler(self, event):
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
            self._config_manager.store_working_dir(dlg.GetPath())
            self._current_document_instance = None
            self._load_working_directory(self._config_manager.get_working_dir())
        # This must be called, the dialog stays in memory so you can retrieve data and would not be destroyed.
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def _about_button_handler(self, event):
        """
        Handles clicks onto the About button. Displays a short message in another window.
        :param event: Not used.
        :return: None
        """
        AboutDialog(self)

    # noinspection PyUnusedLocal
    def _splitter_size_change_handler(self, event):
        """
        Triggered when the splitter window is being resized. This is used to change column size of the page list.
        :param event: Not used
        :return: None
        """
        new_size = self._left_panel.GetSize()[0]
        self._file_list.SetColumnWidth(0, new_size)

    def _clear_editor(self) -> None:
        """
        Clear all controls.
        :return: None
        """
        # Ignore changes to article metadata so it is not saved into the file.
        self._ignore_change = True
        self.SetTitle(Strings.editor_name)
        placeholder_logo_image = wx.Image(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        placeholder_logo_image.Replace(0, 0, 0, 245, 255, 255)
        self._menu_logo_button.SetBitmap(wx.Bitmap(placeholder_logo_image))
        placeholder_main_image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_main_image.Replace(0, 0, 0, 245, 255, 255)
        self._main_image_button.SetBitmap(wx.Bitmap(placeholder_main_image))
        self._file_list.ClearAll()
        self._side_photo_panel.clear_panel()
        self._main_text_area.clear_self()
        self._text_menu_item_name.SetLabelText('')
        self._text_main_image_caption.SetLabelText('')
        self._field_article_name.SetValue(Strings.label_article_title)
        self._field_article_date.SetValue(Strings.label_article_date)
        self._field_article_description.SetValue(Strings.label_article_description)
        self._field_article_keywords.SetValue(Strings.label_article_keywords)
        self._set_status_text(Strings.status_error, 0)
        self._set_status_text(Strings.status_error, 3)
        self._ignore_change = False
        pass

    def _list_item_click_handler(self, event):
        """
        Handler function for clicking a page name in the web page list. Revalidates the document against schema. If
        errors are discovered, disables editor and shows a message.
        :param event: wx event, brings the selected string from the menu.
        :return: None
        """
        if self._current_document_instance and event.GetClientData() != Strings.flag_no_save:
            # Only ask to save if there is a document already opened in the editor and saving is allowed.
            # TODO save into current file, do not show file dialog
            # TODO save a backup copy
            self._save(confirm=True)

        self._disable_editor(True)
        self._current_document_name = event.GetText()
        self._current_document_instance: WhitebearDocumentArticle = self._document_dictionary[
            self._current_document_name]
        try:
            # TODO use this for convert schema validation
            result = self._current_document_instance.validate_self()
            if not result[0]:
                self._set_status_text(Strings.status_invalid + ' ' + self._current_document_name)
                # Prepare error string from all validation errors
                error_string = Strings.exception_html_syntax_error + ': ' + self._current_document_name + '\n'
                for message in result[1]:
                    error_string = error_string + message + '\n'
                self._show_error_dialog(error_string)
                self._disable_editor(True)
                self._clear_editor()
                return
        except UnrecognizedFileException as e:
            self._show_error_dialog(str(e))
            self._disable_editor(True)
            self._clear_editor()
            return
        except KeyError as _:
            self._show_error_dialog(Strings.exception_last_document_missing)
            self._clear_editor()
            return
        # If the document is correct, now we can show it.
        self._fill_editor(self._current_document_instance)

    # noinspection PyUnusedLocal
    def _reload_button_handler(self, event):
        """
        Reparse the selected file from disk. Used in case the user has to fix something in html or images.
        :param event: wx event, not used.
        :return: None
        """
        reload_dialog = wx.MessageDialog(self, Strings.text_reload_from_disk, Strings.status_warning,
                                         wx.YES_NO | wx.ICON_WARNING)
        result = reload_dialog.ShowModal()
        if result == wx.ID_YES:
            reload_dialog.Destroy()
            self._save(confirm=True)
            selected_item = self._file_list.GetItem(self._file_list.GetFirstSelected())
            self._current_document_instance.get_menu_section().parse_self()
            self._current_document_instance.parse_self()
            event = wx.ListEvent()
            event.SetItem(selected_item)
            event.SetClientData(Strings.flag_no_save)
            self._list_item_click_handler(event)
        reload_dialog.Destroy()

    def _fill_editor(self, doc: WhitebearDocumentArticle) -> None:
        """
        Display document contents in the GUI along with error messages.
        :param doc:
        :return: None
        """
        self._disable_editor(True)
        self._update_file_color()
        if doc.get_status_color() == Numbers.RED_COLOR:
            self._set_status_text(
                Strings.status_invalid + ' ' + doc.get_filename() + ' - ' + doc.get_menu_section().get_page_name()[0])
        else:
            self._set_status_text(
                Strings.status_valid + ' ' + doc.get_filename() + ' - ' + doc.get_menu_section().get_page_name()[0])

        self.SetTitle(doc.get_filename())
        # Set article data
        field_to_value = {self._field_article_date: (doc.get_date(), self._field_article_date_tip),
                          self._field_article_name: (doc.get_page_name(), self._field_article_name_tip),
                          self._field_article_keywords: (doc.get_keywords_string(), self._field_article_keywords_tip),
                          self._field_article_description: (doc.get_description(), self._field_article_description_tip)}
        for field, value in field_to_value.items():
            tip = value[1]
            if value[0][1]:
                tip.SetMessage(Strings.seo_check + '\n' + value[0][1])
                tip.EnableTip(True)
                tip.DoShowNow()
            else:
                tip.DoHideNow()
            field.SetValue(value[0][0])

        # Set main image
        self._main_image_button.SetBitmap(wx.Bitmap(doc.get_article_image().get_image()))
        self._menu_logo_button.SetBitmap(wx.Bitmap(doc.get_menu_item().get_image()))

        # Set aside images
        self._side_photo_panel.load_document_images(doc)
        while not self._css_document:
            # Busy wait for css, should not take more than a second in fact this should never run because css method is
            # set to run before loading documents.
            pass
        self._main_text_area.set_content(doc, self._css_document)

        # Set main image caption
        self._text_main_image_caption.SetLabelText(doc.get_article_image().get_caption()[0])

        # Set menu item name
        self._update_menu_sizer(doc.get_menu_item())

        self._disable_editor(False)

    # noinspection PyUnusedLocal
    def _handle_name_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article name field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            correct, message, color = self._current_document_instance.seo_test_name(self._field_article_name.GetValue())
            self._field_article_name.SetBackgroundColour(color)
            self._field_article_name_tip.SetMessage(Strings.seo_check + '\n' + message)
            self._current_document_instance.set_page_name(self._field_article_name.GetValue())
            self._update_file_color()

    # noinspection PyUnusedLocal
    def _handle_date_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article date field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            correct, message, color = self._current_document_instance.seo_test_date(self._field_article_date.GetValue())
            self._field_article_date.SetBackgroundColour(color)
            self._field_article_date_tip.SetMessage(Strings.seo_check + '\n' + message)
            self._current_document_instance.set_date(self._field_article_date.GetValue())
            self._update_file_color()

    # noinspection PyUnusedLocal
    def _handle_keywords_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article keywords field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            keyword_list = [word.strip() for word in self._field_article_keywords.GetValue().split(',')]
            correct, message, color = self._current_document_instance.seo_test_keywords(keyword_list)
            self._field_article_keywords.SetBackgroundColour(color)
            self._field_article_keywords_tip.SetMessage(Strings.seo_check + '\n' + message)
            self._current_document_instance.set_keywords(keyword_list)
            self._update_file_color()

    # noinspection PyUnusedLocal
    def _handle_description_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article description field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            correct, message, color = self._current_document_instance.seo_test_description(
                self._field_article_description.GetValue())

            # Set color
            self._field_article_description.SetBackgroundColour(color)
            style_carrier = wx.TextAttr()

            # Set color for the current text separately, it does not work with just background color
            self._field_article_description.GetStyle(0, style_carrier)
            style_carrier.SetBackgroundColour(color)
            self._field_article_description.SetStyle(0, len(self._field_article_description.GetValue()), style_carrier)

            self._field_article_description_tip.SetMessage(Strings.seo_check + '\n' + message)
            self._current_document_instance.set_description(self._field_article_description.GetValue())
            self._update_file_color()

    def _update_file_color(self, index: int = -1) -> None:
        """
        Change the color of the currently selected file in the filelist according to the document's state.
        :param index: The index of the file in the list that should be updated, -1 if current file.
        :return: None
        """
        self._current_document_instance.is_modified()
        new_color = self._current_document_instance.get_status_color()
        if index == -1:
            index = self._file_list.GetFirstSelected()
        self._file_list.SetItemBackgroundColour(index, new_color)

    def _update_menu_sizer(self, menu_item: MenuItem) -> None:
        """
        Update the menu logo sizer with new content from the edited menu item and realign the label.
        :param menu_item: The modified menu item
        :return: None
        """
        self._menu_logo_button.SetBitmap(wx.Bitmap(menu_item.get_image()))
        self._text_menu_item_name.SetLabelText(menu_item.get_article_name()[0])
        self._text_menu_item_name.Wrap(Numbers.menu_logo_image_size)
        self._menu_logo_static_sizer.Layout()

    def _update_article_image_sizer(self, image: AsideImage) -> None:
        """
        Update the article image sizer with new content from the edited image.
        :param image: The modified image
        :return: None
        """
        self._main_image_button.SetBitmap(wx.Bitmap(image.get_image()))
        self._text_main_image_caption.SetLabelText(image.get_caption()[0])

    # noinspection PyUnusedLocal
    def _text_area_edit_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle special events that signal that the color of the selected item in the filelist should be updated.
        This happens when an edit has been made to the document.
        :param event: Not used.
        :return: None
        """
        self._update_file_color()

    # noinspection PyUnusedLocal
    def _add_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle adding a new image into the image folder structure.
        :param event: Not used
        :return: None
        """
        dlg = AddImageDialog(self, self._current_document_instance)
        dlg.ShowModal()
        dlg.Destroy()

    def _insert_aside_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle adding a new image into the document's aside images.
        :param event: Not used
        :return: None
        """
        # Create a new placeholder text image or video
        new_image = AsideImage(self._current_document_instance.get_menu_section().get_section_name(), '', '', '', '',
                               '',
                               Strings.status_none, Strings.status_none)
        # This will set the image internal state to missing image placeholder.
        new_image.seo_test_self()
        # Open edit dialog.
        edit_dialog = EditAsideImageDialog(self, new_image, self._current_document_instance.get_working_directory())
        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            self._current_document_instance.add_aside_image(new_image)
            self._side_photo_panel.load_document_images(self._current_document_instance)
            self._update_file_color()
        edit_dialog.Destroy()
        event.Skip()
        # Return focus to the text area.
        wx.CallLater(100, self.SetFocus)

    # noinspection PyUnusedLocal
    def _add_menu_logo_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle adding a new image into the image folder structure.
        :param event: Not used
        :return: None
        """
        dlg = AddLogoDialog(self, self._current_document_instance)
        dlg.ShowModal()
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def _save_document_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles save button clicks.
        :param event: Not used.
        :return: None
        """
        self._save()

    # noinspection PyUnusedLocal
    def _repeat_search(self, event: wx.CommandEvent) -> None:
        """
        Force repeating search on arrow press because the text has changed and indexes would no longer match.
        :param event: Not used.
        :return: None
        """
        self._text_changed = True

    def _search_box_handler(self, event: wx.CommandEvent) -> None:
        """
        Forward the string we are searching for into the search method. Fires as text is being typed.
        :param event: Carries the string from search box.
        :return: None
        """
        self._search_string(event.GetString())

    def _search_string(self, text: str) -> bool:
        """
        Find all occurrences of a string typed in the search box and store the starting positions in internal list.
        Select the first found string in the text area.
        :param text: The string to search for.
        :return: True if something was found.
        """
        self._search_term = text
        self._search_results.clear()
        if not self._search_term:
            # Searching for an empty line.
            self._main_text_area.SelectNone()
            self._search_term = None
            self._set_status_text(Strings.status_ready, 3)
            return False

        text_content: str = self._main_text_area.GetValue()
        start_index: int = text_content.find(self._search_term, 0)
        while start_index != -1:
            # At least one was found
            self._search_results.append(start_index)
            # Find the next one after the current match.
            start_index = text_content.find(self._search_term, start_index + len(self._search_term))
        self._set_status_text(Strings.status_found + ': ' + str(len(self._search_results)), 3)

        if len(self._search_results) == 0:
            # Nothing has been found
            self._main_text_area.SelectNone()
            return False

        # Select first found string.
        self._main_text_area.SetSelection(self._search_results[0], (self._search_results[0] + len(self._search_term)))
        return True

    # noinspection PyUnusedLocal
    def _search_tools_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles the arrows that switch between found strings. Fires on pressing the enter key.
        :param event: Used to get the tool id.
        :return: None
        """
        if self._text_changed:
            # Repeat search when the text has changed.
            # Back up current selected position for later comparison.
            self._text_changed = False
            # When the text changes, restart search from beginning.
            self._search_index = 0
            if not self._search_string(self._search_box.GetValue()):
                # If there are no results then, do nothing.
                return

        if not self._search_results:
            return

        # Cycle over the results.
        if self._search_index == len(self._search_results) - 1:
            self._search_index = 0
        else:
            self._search_index = self._search_index + 1

        position: int = self._search_results[self._search_index]
        self._main_text_area.SetSelection(position, (position + len(self._search_term)))
