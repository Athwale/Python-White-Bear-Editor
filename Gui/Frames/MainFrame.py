import os
import threading
from datetime import datetime
from shutil import copyfile
from typing import Dict, List, Callable

import wx
import wx.richtext as rt
from wx.lib.agw.supertooltip import SuperToolTip

from Constants.Constants import Numbers, Events
from Constants.Constants import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Gui.Dialogs.AboutDialog import AboutDialog
from Gui.Dialogs.AddImageDialog import AddImageDialog
from Gui.Dialogs.AddLogoDialog import AddLogoDialog
from Gui.Dialogs.EditAsideImageDialog import EditAsideImageDialog
from Gui.Dialogs.EditDefaultValuesDialog import EditDefaultValuesDialog
from Gui.Dialogs.EditMenuDialog import EditMenuDialog
from Gui.Dialogs.EditMenuItemDialog import EditMenuItemDialog
from Gui.Dialogs.NewFileDialog import NewFileDialog
from Gui.Dialogs.RichTextSpellcheckerDialog import RichTextSpellCheckerDialog
from Gui.Dialogs.SpellCheckSetupDialog import SpellCheckSetupDialog
from Gui.Dialogs.SpellCheckerDialog import SpellCheckerDialog
from Gui.Dialogs.UploadDialog import UploadDialog
from Gui.Panels.AsideImagePanel import AsideImagePanel
from Gui.Panels.CustomRichText import CustomRichText
from Resources.Fetch import Fetch
from Threads.FileListThread import FileListThread
from Threads.SavingThread import SavingThread
from Threads.SitemapThread import SitemapThread
from Threads.WorkerThread import WorkerThread
from Tools.ConfigManager import ConfigManager
from Tools.Document.AsideImage import AsideImage
from Tools.Document.MenuItem import MenuItem
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu
from Tools.Tools import Tools


class MainFrame(wx.Frame):
    """
    Main GUI controlling class. The Frame is actually the on the screen window.
    """
    VIDEO_TOOL_ID: int = wx.NewId()
    IMAGE_TOOL_ID: int = wx.NewId()

    def __init__(self):
        """
        Constructor for the GUI of the editor. This is the main frame, so we pass None as the parent.
        """
        # -1 is a special ID which generates a random wx ID
        super(MainFrame, self).__init__(None, -1, title=Strings.editor_name + ' - ' + Strings.status_loading,
                                        style=wx.DEFAULT_FRAME_STYLE)

        self.SetIcon(wx.Icon(Fetch.get_resource_path('icon.ico')))
        # Create fonts for text fields
        self.small_font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        self.bold_small_font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)
        # Prepare data objects
        try:
            self._config_manager: ConfigManager = ConfigManager.get_instance()
        except PermissionError as e:
            self._show_error_dialog(Strings.exception_conf_inaccessible + '\n' + str(e))

        self._tool_ids = []
        self._disableable_menu_items = []
        self._articles = {}
        self._menus = {}
        self._index_document = None
        self._current_document_name = None
        self._current_document_instance = None
        self._css_document = None
        self._ignore_change = False
        self._no_save = False
        self._enabled = True
        self._saved_documents = []

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
        # Find the last opened whitebear directory, switch config manager to it and load it.
        if self._config_manager.set_active_dir(self._config_manager.get_last_directory()):
            self._load_working_directory(self._config_manager.get_working_dir())
            # Load online test state.
            self._file_menu.Check(wx.ID_NETWORK, self._config_manager.get_online_test())
        else:
            self._disable_editor(True)

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
        self._disableable_menu_items.append(self._file_menu_item_new)

        self._file_menu_item_new_dir = wx.MenuItem(self._file_menu, wx.ID_FILE7, Strings.label_menu_item_new_dir,
                                                   Strings.label_menu_item_new_dir_hint)

        self._file_menu_item_open = wx.MenuItem(self._file_menu, wx.ID_OPEN, Strings.label_menu_item_open,
                                                Strings.label_menu_item_open_hint)

        self._file_menu_item_save = wx.MenuItem(self._file_menu, wx.ID_SAVE, Strings.label_menu_item_save,
                                                Strings.label_menu_item_save_hint)
        self._disableable_menu_items.append(self._file_menu_item_save)

        self._file_menu_item_save_as = wx.MenuItem(self._file_menu, wx.ID_SAVEAS, Strings.label_menu_item_save_as,
                                                   Strings.label_menu_item_save_as_hint)
        self._disableable_menu_items.append(self._file_menu_item_save_as)

        self._file_menu_item_upload = wx.MenuItem(self._file_menu, wx.ID_EXECUTE, Strings.label_menu_item_upload,
                                                  Strings.label_menu_item_upload_hint)
        self._disableable_menu_items.append(self._file_menu_item_upload)

        self._file_menu_item_setup = wx.MenuItem(self._file_menu, wx.ID_SETUP, Strings.label_menu_item_page_setup,
                                                 Strings.label_menu_item_page_setup_hint)
        self._disableable_menu_items.append(self._file_menu_item_setup)

        self._file_menu_item_edit_menu = wx.MenuItem(self._file_menu, wx.ID_FILE9, Strings.label_menu_item_edit_menu,
                                                     Strings.label_menu_item_edit_menu_hint)
        self._disableable_menu_items.append(self._file_menu_item_edit_menu)

        self._file_menu_item_export_all = wx.MenuItem(self._file_menu, wx.ID_FILE8, Strings.label_menu_item_export_all,
                                                      Strings.label_menu_item_export_all_hint)
        self._disableable_menu_items.append(self._file_menu_item_export_all)

        self._file_menu_item_delete = wx.MenuItem(self._file_menu, wx.ID_DELETE, Strings.label_menu_item_delete,
                                                  Strings.label_menu_item_delete_hint)
        self._disableable_menu_items.append(self._file_menu_item_delete)

        # Put menu items into the menu buttons
        self._file_menu.Append(self._file_menu_item_open)
        self._file_menu.Append(self._file_menu_item_new_dir)
        self._file_menu.AppendSeparator()
        self._file_menu.Append(self._file_menu_item_new)
        self._file_menu.Append(self._file_menu_item_save)
        self._file_menu.Append(self._file_menu_item_save_as)
        self._file_menu.Append(self._file_menu_item_delete)
        self._file_menu.AppendSeparator()
        self._file_menu.Append(self._file_menu_item_edit_menu)
        self._file_menu.Append(self._file_menu_item_setup)
        self._file_menu.AppendSeparator()
        self._file_menu.Append(self._file_menu_item_upload)
        self._file_menu.Append(self._file_menu_item_export_all)
        self._file_menu.AppendSeparator()
        self._file_menu.AppendCheckItem(wx.ID_NETWORK, Strings.label_menu_item_online_test,
                                        Strings.label_menu_item_online_test_hint)

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
        self._edit_menu_item_spellcheck = wx.MenuItem(self._edit_menu, wx.ID_SPELL_CHECK,
                                                      Strings.label_menu_item_spellcheck,
                                                      Strings.label_menu_item_spellcheck_hint)
        self._disableable_menu_items.append(self._edit_menu_item_spellcheck)
        self._edit_menu_item_spellcheck_setup = wx.MenuItem(self._edit_menu, wx.ID_EDIT,
                                                            Strings.label_menu_item_spellcheck_setup,
                                                            Strings.label_menu_item_spellcheck_setup_hint)
        self._disableable_menu_items.append(self._edit_menu_item_spellcheck_setup)

        self._edit_menu.Append(self._edit_menu_item_undo)
        self._edit_menu.Append(self._edit_menu_item_redo)
        self._edit_menu.AppendSeparator()
        self._edit_menu.Append(self._edit_menu_item_copy)
        self._edit_menu.Append(self._edit_menu_item_cut)
        self._edit_menu.Append(self._edit_menu_item_paste)
        self._edit_menu.Append(self._edit_menu_item_select_all)
        self._edit_menu.AppendSeparator()
        self._edit_menu.AppendCheckItem(wx.ID_FILE6, Strings.label_menu_item_spelling_test,
                                        Strings.label_menu_item_spelling_test_hint)
        self._edit_menu.Append(self._edit_menu_item_spellcheck)
        self._edit_menu.Append(self._edit_menu_item_spellcheck_setup)

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
        Set up top toolbar for the frame.
        :return: None
        """
        self.tool_bar: wx.ToolBar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)
        # Add toolbar tools
        self._new_file_tool: wx.ToolBarToolBase = self.tool_bar.AddTool(wx.ID_NEW, Strings.toolbar_new_file,
                                                                        self._scale_icon('new-file.png'),
                                                                        Strings.toolbar_new_file)
        self._save_tool: wx.ToolBarToolBase = self.tool_bar.AddTool(self._add_tool_id(), Strings.toolbar_save,
                                                                    self._scale_icon('save.png'),
                                                                    Strings.toolbar_save)
        self._save_tool.SetLongHelp(Strings.toolbar_save)
        self.insert_img_tool: wx.ToolBarToolBase = self.tool_bar.AddTool(MainFrame.IMAGE_TOOL_ID,
                                                                         Strings.toolbar_insert_img,
                                                                         self._scale_icon('insert-image.png'),
                                                                         Strings.toolbar_insert_img)
        self.insert_img_tool.SetLongHelp(Strings.toolbar_insert_img)
        self._tool_ids.append(MainFrame.IMAGE_TOOL_ID)
        self.insert_video_tool: wx.ToolBarToolBase = self.tool_bar.AddTool(MainFrame.VIDEO_TOOL_ID,
                                                                           Strings.toolbar_insert_video,
                                                                           self._scale_icon('insert-video.png'),
                                                                           Strings.toolbar_insert_video)
        self.insert_video_tool.SetLongHelp(Strings.toolbar_insert_video)
        self._tool_ids.append(MainFrame.VIDEO_TOOL_ID)
        self.bold_tool: wx.ToolBarToolBase = self.tool_bar.AddTool(self._add_tool_id(), Strings.toolbar_bold,
                                                                   self._scale_icon('bold.png'),
                                                                   Strings.toolbar_bold)
        self.bold_tool.SetLongHelp(Strings.toolbar_bold)
        self.Bind(wx.EVT_MENU, self._forward_event, self.insert_img_tool)
        self.Bind(wx.EVT_MENU, self._forward_event, self.insert_video_tool)
        self.Bind(wx.EVT_MENU, self._forward_event, self.bold_tool)
        self.Bind(wx.EVT_MENU, self._save_document_handler, self._save_tool)

        self._search_box = wx.TextCtrl(self.tool_bar, wx.ID_FIND, style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self._search_box_handler, self._search_box)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_tools_handler, self._search_box)

        self._public_checkbox = wx.CheckBox(self.tool_bar, wx.ID_IGNORE, Strings.label_article_public)
        self.Bind(wx.EVT_CHECKBOX, self._public_checkbox_handler, self._public_checkbox)

        self.tool_bar.Realize()

    def _public_checkbox_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle enabling and disabling article publication.
        :param event: Used to get the checkbox state.
        :return: None
        """
        if event.IsChecked():
            self._current_document_instance.set_enabled(True)
            self._public_checkbox.SetForegroundColour(Numbers.DARK_GREEN_COLOR)
        else:
            self._current_document_instance.set_enabled(False)
            self._public_checkbox.SetForegroundColour(wx.RED)

    def _init_toolbar_controls(self) -> None:
        """
        Add search box into the top toolbar.
        :return: None
        """
        if not self.tool_bar.FindById(wx.ID_FIND):
            # Only add the search box once and not when a new directory is loaded again.
            self.tool_bar.AddSeparator()
            self.tool_bar.AddControl(self._search_box)
        if not self.tool_bar.FindById(wx.ID_IGNORE):
            self.tool_bar.AddSeparator()
            self.tool_bar.AddControl(self._public_checkbox)

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
        tool: wx.ToolBarToolBase = toolbar.AddTool(self._add_tool_id(), Strings.toolbar_color, bmp, name)
        tool.SetLongHelp(Strings.toolbar_color + ': ' + name)
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
        # Loading panel
        self._loading_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._loading_image = wx.Bitmap(Fetch.get_resource_path('splashscreen.png'), wx.BITMAP_TYPE_PNG)
        self._loading_bitmap = wx.StaticBitmap(self, -1, self._loading_image)
        self._loading_sizer.Add(self._loading_bitmap, 1, flag=wx.EXPAND)

        # Logo section -------------------------------------------------------------------------------------------------
        # Create a placeholder image
        placeholder_logo_image = wx.Image(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        placeholder_logo_image.Replace(0, 0, 0, 245, 255, 255)
        self._menu_logo_button = wx.Button(self._right_panel, -1, style=wx.BU_EXACTFIT | wx.BORDER_NONE)
        self._menu_logo_button.SetBitmap(wx.Bitmap(placeholder_logo_image))
        # Set border to the image
        self._menu_logo_static_sizer.Add(self._menu_logo_button, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT,
                                         border=Numbers.widget_border_size)
        # Create menu logo name text box
        self._text_menu_item_name = wx.StaticText(self._right_panel, -1,
                                                  Strings.label_article_menu_logo_name_placeholder,
                                                  style=wx.ALIGN_CENTRE_HORIZONTAL)
        self._text_menu_item_name.SetFont(self.small_font)
        self._text_menu_item_name.SetMaxSize((Numbers.menu_logo_image_size, 30))
        self._menu_logo_static_sizer.Add(self._text_menu_item_name, flag=wx.CENTER)
        # --------------------------------------------------------------------------------------------------------------

        # File list section --------------------------------------------------------------------------------------------
        self._style_picker = wx.ListBox(self._left_panel, -1, size=(-1, 127))
        self._style_sizer.Add(self._style_picker, 1, flag=wx.EXPAND)
        self._file_list = wx.ListCtrl(self._left_panel, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self._file_list.SetFont(self.small_font)
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
        self._side_photo_column_sizer.Add(self._side_photo_panel, 1, flag=wx.EXPAND | wx.ALIGN_LEFT)
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
        # Update file color on change.
        self.Bind(wx.EVT_TEXT, self._text_area_edit_handler, self._main_text_area)

    def _bind_handlers(self) -> None:
        """
        Bind event handlers.
        :return: None
        """
        # Binding an event to a handler function, the last parameter is the source of the event. In case of for
        # example buttons, all buttons will create EVT_BUTTON, and we will not know which handler to use unless
        # the source is set.
        # Bind window close events, X button and emergency quit
        self.Bind(wx.EVT_CLOSE, self._close_button_handler, self)
        # This calls the quit method if the user logs off the computer
        self.Bind(wx.EVT_QUERY_END_SESSION, self._close_button_handler)

        # Bind a handler that changes selected document color if an edit happens in other controls of the text area.
        self.Bind(Events.EVT_DOCUMENT_TEXT_CHANGED, self._text_area_edit_handler)
        # Bind color changing event to the side panel.
        self.Bind(Events.EVT_DOCUMENT_IMAGES_CHANGED, self._text_area_edit_handler)
        # Bind a handler to the spell check event to allow enabling editor without spellcheck being a modal dialog.
        self.Bind(Events.EVT_SPELLCHECK_DONE, self._spellcheck_done_handler)
        # Special event that signals that dictionary or ignore list changed and all spellchecks should rerun.
        self.Bind(Events.EVT_RECOLOR_ALL, self._recolor_handler)

        # Bind menu item clicks
        self.Bind(wx.EVT_MENU, self._about_button_handler, self._help_menu_item_about)
        self.Bind(wx.EVT_MENU, self._open_button_handler, self._file_menu_item_open)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_cut)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_copy)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_paste)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_undo)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_redo)
        self.Bind(wx.EVT_MENU, self._forward_event, self._edit_menu_item_select_all)
        self.Bind(wx.EVT_MENU, self._self_test_handler, self._edit_menu_item_spellcheck)
        self.Bind(wx.EVT_MENU, self._spellcheck_setup_handler, self._edit_menu_item_spellcheck_setup)
        self.Bind(wx.EVT_MENU, self._add_image_handler, self._add_menu_item_add_image)
        self.Bind(wx.EVT_MENU, self._insert_aside_image_handler, self._add_menu_item_side_image)
        self.Bind(wx.EVT_MENU, self._add_menu_logo_handler, self._add_menu_item_add_logo)
        self.Bind(wx.EVT_MENU, self._save_document_handler, self._file_menu_item_save)
        self.Bind(wx.EVT_MENU, self._save_document_handler, self._file_menu_item_save_as)
        self.Bind(wx.EVT_MENU, self._page_setup_handler, self._file_menu_item_setup)
        self.Bind(wx.EVT_MENU, self._new_file_handler, self._file_menu_item_new)
        self.Bind(wx.EVT_MENU, self._edit_menu_handler, self._file_menu_item_edit_menu)
        self.Bind(wx.EVT_MENU, self._export_all_handler, self._file_menu_item_export_all)
        self.Bind(wx.EVT_MENU, self._delete_article_handler, self._file_menu_item_delete)
        self.Bind(wx.EVT_MENU, self._new_dir_handler, self._file_menu_item_new_dir)
        self.Bind(wx.EVT_MENU, self._upload_handler, self._file_menu_item_upload)
        self.Bind(wx.EVT_MENU, self._online_test_handler, id=wx.ID_NETWORK)

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

    def _loading_screen_on(self, display: bool) -> None:
        """
        Display or not display the loading image.
        :param display: True to switch to loading panel, False to switch to editor.
        :return: None
        """
        if display:
            self.SetSizer(self._loading_sizer, deleteOld=False)
            self._loading_bitmap.Show()
            self._split_screen.Hide()
        else:
            self.SetSizer(self._main_horizontal_sizer, deleteOld=False)
            self._loading_bitmap.Hide()
            self._split_screen.Show()
        self.Layout()

    # noinspection PyUnusedLocal
    def _focus_to_search(self, event: wx.CommandEvent) -> None:
        """
        Handles Ctrl+F shortcut to set focus into the search box.
        :param event: Not used
        :return: None
        """
        self._search_box.SetFocus()

    def _set_status_text(self, text: str, position=0) -> None:
        """
        Set a text into a position in status bar and prepend a separator.
        :param text: Text to set.
        :param position: Where to set the text, 0 is default
        :return: None
        """
        to_set = '| ' + text
        self._status_bar.SetStatusText(to_set, position)

    def _disable_editor(self, state, leave_files: bool = False, all_menu: bool = False) -> None:
        """
        Disable all window controls except menu a title bar.
        :param state: True to disable, False to enable all GUI elements.
        :param leave_files: If True the file list will not be disabled.
        :param all_menu: Disable all menu items.
        :return: None
        """
        self._enabled = not state
        self.Enable()
        if state:
            # Disabling the editor (disable editor True)
            self._main_text_area.SetBackgroundColour(Numbers.LIGHT_GREY_COLOR)
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
            self._main_text_area.SetBackgroundColour(wx.WHITE)
            self._split_screen.Enable()
            self._left_panel.Enable()
            self._right_panel.Enable()
            self._file_list.SetBackgroundColour(wx.WHITE)
            self._file_list.SetForegroundColour(wx.BLACK)
        # Disable toolbar buttons
        self.tool_bar.Enable(not state)
        for tool_id in self._tool_ids:
            self.tool_bar.EnableTool(tool_id, (not state))
        self._main_text_area.enable_buttons()
        self.tool_bar.EnableTool(wx.ID_NEW, (not state))
        # Disable menu items
        self._public_checkbox.Enable(not state)
        self._file_menu.Enable(wx.ID_NETWORK, not state)
        menu_items_to_disable = []
        menu_items_to_disable.extend(self._disableable_menu_items)
        if all_menu:
            menu_items_to_disable.append(self._file_menu_item_open)
            menu_items_to_disable.append(self._file_menu_item_new_dir)
        else:
            self._file_menu_item_open.Enable()
            self._file_menu_item_new_dir.Enable()
        for menu_item in menu_items_to_disable:
            menu_item.Enable(not state)
        if leave_files:
            # Files are left enabled in white bear directories only.
            self._file_menu_item_new.Enable(True)
            self._file_menu_item_edit_menu.Enable(True)
            self.tool_bar.EnableTool(wx.ID_NEW, True)

    def _load_working_directory(self, path: str) -> None:
        """
        Load a working directory into the editor.
        :param path: str, path to the working directory
        :return: None
        """
        self._loading_screen_on(True)
        # Disable the gui until load is done
        self._disable_editor(True, leave_files=False, all_menu=True)
        self._set_status_text(Strings.status_loading, 3)
        self._set_status_text(('Work dir: ' + str(path)), 1)
        self._set_status_text(Strings.status_ready, 0)
        file_list_thread = FileListThread(self, str(path))
        file_list_thread.start()

    def on_filelist_load_fail(self, path: str, e: Exception) -> None:
        """
        If the loading of a supposed whitebear directory fails, this method is called, it shows the error and disables
        all editor functionality except the load new directory button.
        :param path: The failed path.
        :param e: Exception that caused the call of this method.
        :return: None
        """
        self._loading_screen_on(False)
        self._show_error_dialog(str(e))
        self._disable_editor(state=True, all_menu=False)
        self._side_photo_panel.reset()
        self._clear_editor(leave_files=False)
        # Only remove config if index is missing.
        if path:
            self._config_manager.remove_config_dir(path)

    def _show_error_dialog(self, error: str) -> None:
        """
        Display an error dialog with the error text. Set error state into the status bar.
        :param error: The error to display in the dialog.
        :return: None
        """
        wx.MessageBox(error, Strings.status_error, wx.OK | wx.ICON_ERROR)
        self._set_status_text(Strings.status_error, 2)

    def on_css_parsed(self, css: WhitebearDocumentCSS) -> None:
        """
        Generates text color tools in toolbar once css is parsed.
        :param css: The parsed css file.
        :return: None
        """
        self._css_document = css
        css_colors = css.get_colors()
        for name, color in css_colors.items():
            self._create_color_tool(name, self.tool_bar, color)
        self._init_toolbar_controls()

    def on_filelist_loaded(self, documents: Dict[str, WhitebearDocumentArticle],
                           menus: Dict[str, WhitebearDocumentMenu], index: WhitebearDocumentIndex) -> None:
        """
        This method fills up the left side page file list and is called when the FileListThread finishes.
        :param documents: Dictionary of file names and documents of article pages {file name, WhitebearDocument, ...}
        :param menus: Dictionary of file names and documents of article pages {file name, WhitebearDocumentMenu, ...}
        :param index: WhitebearDocumentIndex instance.
        :return: None
        """
        self._disable_editor(True, leave_files=True)
        self._articles = documents
        self._menus = menus
        if not menus:
            self._file_menu_item_new.Enable(False)
            self.tool_bar.EnableTool(wx.ID_NEW, False)
            self._file_menu_item_edit_menu.Enable(True)
        self._index_document = index
        self._clear_editor(leave_files=False)
        unuploaded = self._config_manager.get_not_uploaded()
        for document_name in sorted(list(self._articles.keys()), reverse=True):
            if document_name in unuploaded:
                # Set blue color to documents have been modified but not uploaded yet.
                self._articles[document_name].set_modified(True)
                self._articles[document_name].set_saved(True)
                self._articles[document_name].set_uploaded(False)
                # Set html code to something not False because at this point we have the final html on disk.
                self._articles[document_name].set_html('current html on disk')
                # Rerun self test because document attributes were changed.
                self._articles[document_name].test_self(self._config_manager.get_online_test())
            self._file_list.InsertItem(0, document_name)
            self._update_file_color(0)

        # Select last used document
        last_document = self._config_manager.get_last_document()
        if last_document:
            index = self._file_list.FindItem(0, last_document)
            if index > -1:
                self._file_list.Select(index)
            else:
                self._loading_screen_on(False)
                self._show_error_dialog(Strings.warning_last_document_not_found + ':' + '\n' + str(last_document))
                self._clear_editor(leave_files=True)

        os.chdir(self._config_manager.get_working_dir())
        # Enable GUI when the load is done
        self._set_status_text(Strings.status_ready, 3)
        self._set_status_text(Strings.status_articles + ' ' + str(len(self._articles)), 2)
        self._loading_screen_on(False)

        # Store this as last known open directory.
        self._config_manager.store_working_dir(self._index_document.get_working_directory())
        if not self._config_manager.check_set_config_values():
            # Check that no default values are missing.
            self._show_error_dialog(Strings.exception_default_value_not_set)
            # Open defaults dialog if anything is missing.
            dlg = EditDefaultValuesDialog(self, no_cancel=True)
            dlg.ShowModal()
            dlg.Destroy()

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
        self._main_text_area: CustomRichText
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
                # Get the attributes of the single char range and modify them in place. Otherwise, changing paragraph.
                # style is broken since the attributes are reset for the range.
                attr = rt.RichTextAttr()
                self._main_text_area.GetStyleForRange(single_range, attr)
                # Ignore links.
                if attr.HasURL():
                    continue
                attr.SetTextColour(color)
                self._main_text_area.SetStyleEx(single_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)
                self._current_document_instance.set_modified(True)
                self._update_file_color()
                self._main_text_area.SelectNone()
            self._main_text_area.EndBatchUndo()
        else:
            # Prevent beginning a new color inside urls and headings.
            position = self._main_text_area.GetAdjustedCaretPosition(self._main_text_area.GetCaretPosition())
            par_style, char_style = self._main_text_area.get_style_at_pos(self._main_text_area.GetBuffer(), position)
            if char_style == Strings.style_url:
                return
            elif par_style == Strings.style_heading_3 or par_style == Strings.style_heading_4:
                # Select current word and recursively call itself to color the whole heading.
                self._main_text_area.SelectWord(position)
                self._change_color(evt)
            else:
                self._main_text_area.BeginTextColour(color)

    def _save_current_doc(self, confirm: bool = False, save_as: bool = False, disable: bool = False) -> bool:
        """
        Save current document onto disk.
        :param confirm: Require user confirmation.
        :param disable: Leave the editor disabled after threads finish.
        :return: False if save canceled.
        """
        self._main_text_area.convert_document()
        if confirm:
            result = wx.MessageBox(Strings.label_menu_item_save_hint, Strings.toolbar_save, wx.YES_NO | wx.ICON_WARNING)
            if result == wx.NO:
                return False
        # Save article, corresponding menu and index.
        save_list = [self._current_document_instance, self._current_document_instance.get_menu_section(),
                     self._current_document_instance.get_index_document()]
        self._save(save_list, save_as, disable)
        return True

    def _save_all(self, disable: bool = False) -> None:
        """
        Save all articles, menus and index.
        :param disable: Leave the editor disabled after threads finish.
        :return: None
        """
        save_list = list(self._articles.values())
        save_list.extend(list(self._menus.values()))
        save_list.append(self._index_document)
        self._save(save_list, False, disable)

    def _save_sitemap(self, disable: bool) -> None:
        """
        Generate and save a sitemap of the current pages.
        :param disable: Leave the editor disabled after threads finish.
        :return: None
        """
        pages = [Strings.index + Strings.extension_html]
        pages.extend(list(self._articles.keys()))
        pages.extend(list(self._menus.keys()))
        sitemap_thread = SitemapThread(self, pages, self._config_manager.get_working_dir(), disable)
        sitemap_thread.start()

    def _save(self, save_list: List[WhitebearDocument], save_as: bool = False, disable: bool = False) -> None:
        """
        Save current document onto disk.
        :param save_list: List of documents to save.
        :param disable: Leave the editor disabled after threads finish.
        :return: None.
        """
        if self._enabled:
            # Editor will be enabled when all threads finish.
            self._disable_editor(True)

        self._save_sitemap(disable)
        saving_thread = SavingThread(self, save_list, save_as, disable)
        saving_thread.start()

    def on_conversion_done(self, doc, save_as: bool, disable: bool) -> None:
        """
        Called when ConvertorThread finishes converting documents to html.
        :param doc: The document that was processed by the thread.
        :param save_as: Open file dialog for the article and menu, otherwise save into the current filename.
        :param disable: Leave the editor disabled after threads finish.
        :return: None
        """
        last_save = datetime.now().strftime("%H:%M:%S")
        file_path = doc.get_path()
        file_name = doc.get_filename()
        if isinstance(doc, WhitebearDocumentArticle):
            suffix = Strings.article
        elif isinstance(doc, WhitebearDocumentMenu):
            suffix = Strings.menu
        else:
            suffix = Strings.index
        html_string = doc.get_html_to_save()

        if os.path.exists(file_path):
            if not os.access(file_path, os.R_OK) or not os.access(file_path, os.W_OK):
                self._show_error_dialog(Strings.warning_can_not_save + '\n' + Strings.exception_access_html + '\n' +
                                        file_path)
                self._disable_editor(False)
                return
        if save_as:
            file_path = self._get_new_file_path(suffix)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf8') as file:
                    file.write(html_string)
            except IOError:
                self._show_error_dialog(Strings.warning_can_not_save + '\n' + Strings.exception_access_html + '\n' +
                                        file_path)
            self._set_status_text(Strings.label_saving + ': ' + file_name, 3)
        # Clean thread list off stopped threads.
        if isinstance(doc, WhitebearDocumentArticle):
            # This is used after all threads are done to update the color of all saved documents.
            self._saved_documents.append(doc)
        # The last thread is the main thread.
        if threading.active_count() == 1:
            for doc in self._saved_documents:
                # Update file color on all saved once all threads are done. Menu saving thread runs self test on all
                # documents in that menu. Updating color while threads are still running sometimes breaks colors
                # because of concurrent run.
                self._update_file_color(self._file_list.FindItem(-1, doc.get_filename()))
            self._saved_documents.clear()
            if not disable:
                # Enable only when all threads have finished and enabling is allowed.
                self._disable_editor(False)
            if file_path:
                self._set_status_text(Strings.status_saved + ': ' + last_save, 3)

    def on_sitemap_done(self, sitemap: str, disable: bool) -> None:
        """
        :param sitemap: The sitemap xml as string.
        :param disable: Leave the editor disabled after threads finish.
        :return: None
        """
        sitemap_file = os.path.join(self._config_manager.get_working_dir(), Strings.sitemap_file)
        robots_txt = os.path.join(self._config_manager.get_working_dir(), Strings.robots_file)
        last_save = datetime.now().strftime("%H:%M:%S")
        try:
            # Save sitemap
            with open(sitemap_file, 'w', encoding='utf8') as file:
                file.write(sitemap)
                self._set_status_text(Strings.status_saved + ': ' + last_save, 3)
                self._set_status_text(Strings.label_saving + ': ' + Strings.sitemap_file, 3)
            # Save robots.txt if not present
            if not os.path.exists(robots_txt):
                with open(robots_txt, 'w', encoding='utf8') as file:
                    file.write(Strings.sitemap_keyword + ' ' + self._config_manager.get_url() + '/' +
                               Strings.sitemap_file)
                    self._set_status_text(Strings.label_saving + ': ' + Strings.robots_file, 3)
        except IOError:
            self._show_error_dialog(Strings.warning_can_not_save + '\n' + Strings.exception_access_html + '\n' +
                                    sitemap_file)
        # The last thread is the main thread.
        if threading.active_count() == 1 and not disable:
            # Enable only when all threads have finished.
            self._disable_editor(False)

    def _get_new_file_path(self, suffix: str) -> str:
        """
        Gets a new disk path from the user.
        :param suffix: A suffix to add after 'untitled' in default file name.
        :return: The path or None if the operation is canceled.
        """
        with wx.FileDialog(self, Strings.label_dialog_save_file, wildcard=Strings.html_wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           defaultDir=self._current_document_instance.get_working_directory(),
                           defaultFile=Strings.default_file + '-' + suffix) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                new_path = fileDialog.GetPath()
                # Add .html if necessary.
                if not new_path.endswith(Strings.extension_html):
                    new_path = new_path + Strings.extension_html
            else:
                # Signal we do not want to save.
                new_path = None
        return new_path

    def on_conversion_fail(self, e: Exception) -> None:
        """
        Shows an error message with the conversion problem.
        :return: None
        """
        self._show_error_dialog(Strings.warning_can_not_save + '\n\n' + str(e))
        self._disable_editor(False)

    # noinspection PyUnusedLocal
    def _main_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle click on the main image button,
        :param event: Not used
        :return: None
        """
        main_image: AsideImage = self._current_document_instance.get_article_image()
        edit_dialog = EditAsideImageDialog(self, main_image, self._current_document_instance.get_working_directory())
        edit_dialog.ShowModal()
        if edit_dialog.was_modified():
            self._current_document_instance.set_modified(True)
        self._update_seo_colors()
        edit_dialog.Destroy()

    # noinspection PyUnusedLocal
    def _menu_logo_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle click on the menu logo button,
        :param event: Not used
        :return: None
        """
        menu_item: MenuItem = self._current_document_instance.get_menu_item()
        edit_dialog = EditMenuItemDialog(self, menu_item, self._current_document_instance.get_working_directory())
        # We first need to show the dialog so that the name label can calculate it's size and then switch to modal.
        edit_dialog.Show()
        edit_dialog.display_dialog_contents()
        edit_dialog.ShowModal()
        if edit_dialog.was_modified():
            self._current_document_instance.set_modified(True)
        self._update_seo_colors()
        edit_dialog.Destroy()

    def _close_button_handler(self, event: wx.CloseEvent):
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
            for doc in self._articles.values():
                doc: WhitebearDocumentArticle
                if doc.is_modified() and not doc.is_saved():
                    result = wx.MessageBox(Strings.warning_unsaved, Strings.status_warning, wx.YES_NO | wx.ICON_WARNING)
                    if result == wx.YES:
                        self.Destroy()
                        break
                    else:
                        event.Veto()
                        return
            else:
                # If the built-in close function is not called, destroy must be called explicitly, calling Close runs
                # the close handler.
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
        # Modal means the user is locked into this dialog and can not use the rest of the application
        if dlg.ShowModal() == wx.ID_OK:
            if not self._config_manager.set_active_dir(dlg.GetPath()):
                self._config_manager.add_directory(dlg.GetPath())
                self._config_manager.set_active_dir(dlg.GetPath())
            self._current_document_instance = None
            self._load_working_directory(self._config_manager.get_working_dir())
        # This must be called, the dialog stays in memory, so you can retrieve data and would not be destroyed.
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

    def _clear_editor(self, leave_files: bool) -> None:
        """
        Clear all controls.
        :param leave_files: Leave the filelist uncleared.
        :return: None
        """
        # Ignore changes to article metadata, so it is not saved into the file.
        self._ignore_change = True
        self.SetTitle(Strings.editor_name)
        placeholder_logo_image = wx.Image(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        placeholder_logo_image.Replace(0, 0, 0, 245, 255, 255)
        self._menu_logo_button.SetBitmap(wx.Bitmap(placeholder_logo_image))
        placeholder_main_image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_main_image.Replace(0, 0, 0, 245, 255, 255)
        self._main_image_button.SetBitmap(wx.Bitmap(placeholder_main_image))
        if not leave_files:
            self._file_list.ClearAll()
            self._file_list.InsertColumn(0, Strings.label_filelist, format=wx.LIST_FORMAT_LEFT)
            self._file_list.SetColumnWidth(0, self._left_panel.GetSize()[0])
        self._side_photo_panel.clear_panel()
        self._main_text_area.clear_self()
        self._text_menu_item_name.SetLabelText('')
        self._text_main_image_caption.SetLabelText('')
        self._field_article_name.SetValue(Strings.label_article_title)
        self._field_article_date.SetValue(Strings.label_article_date)
        self._field_article_description.SetValue(Strings.label_article_description)
        self._field_article_keywords.SetValue(Strings.label_article_keywords)
        self._field_article_name.SetBackgroundColour(wx.WHITE)
        self._field_article_date.SetBackgroundColour(wx.WHITE)
        Tools.set_field_background(self._field_article_description, wx.WHITE)
        self._field_article_keywords.SetBackgroundColour(wx.WHITE)
        self._set_status_text(Strings.status_ready, 0)
        self._set_status_text(Strings.status_ready, 3)
        self._ignore_change = False

    def _list_item_click_handler(self, event):
        """
        Handler for clicking a page name in the web page list. Revalidates the document against schema. If errors are
        discovered, disables editor and shows a message.
        :param event: wx event, brings the selected string from the menu.
        :return: None
        """
        if self._current_document_instance and not self._current_document_instance.is_saved():
            # Only ask to save if there is a document already opened in the editor and saving is allowed.
            self._save_current_doc(confirm=True)

        self._disable_editor(True)
        self._current_document_name = event.GetText()
        self._current_document_instance: WhitebearDocumentArticle = self._articles[
            self._current_document_name]
        try:
            result = self._current_document_instance.validate_self()
            if not result[0]:
                self._set_status_text(Strings.status_invalid + ' ' + self._current_document_name)
                # Prepare error string from all validation errors
                error_string = Strings.exception_html_syntax_error + ': ' + self._current_document_name + '\n'
                for message in result[1]:
                    error_string = error_string + message + '\n'
                self._show_error_dialog(error_string)
                self._disable_editor(True)
                self._clear_editor(leave_files=False)
                return
        except UnrecognizedFileException as e:
            self._show_error_dialog(str(e))
            self._disable_editor(True)
            self._clear_editor(leave_files=False)
            return
        except KeyError as _:
            self._show_error_dialog(Strings.exception_last_document_missing)
            self._clear_editor(leave_files=False)
            return
        self._file_menu_item_delete.Enable(True)
        # If the document is correct, now we can show it.
        # Do not do online test, this slows down load.
        self._current_document_instance.test_self()
        self._fill_editor(self._current_document_instance)

    def _fill_editor(self, doc: WhitebearDocumentArticle) -> None:
        """
        Display document contents in the GUI along with error messages.
        :param doc:
        :return: None
        """
        self._ignore_change = True
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
                if value[0][1] == Strings.status_ok:
                    Tools.set_field_background(field, Numbers.GREEN_COLOR)
                else:
                    Tools.set_field_background(field, Numbers.RED_COLOR)
                tip.SetMessage(Strings.seo_check + '\n' + value[0][1])
                tip.EnableTip(True)
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
        self._main_text_area.set_content(doc)

        # Set main image caption.
        self._text_main_image_caption.SetLabelText(doc.get_article_image().get_caption()[0])

        # Set menu item name.
        self._update_menu_sizer(doc.get_menu_item())

        # Set publication check box.
        if not doc.is_enabled():
            self._public_checkbox.SetValue(False)
            self._public_checkbox.SetForegroundColour(wx.RED)
        else:
            self._public_checkbox.SetValue(True)
            self._public_checkbox.SetForegroundColour(Numbers.DARK_GREEN_COLOR)

        # Clear any search terms.
        self._text_changed = True
        self._search_index = 0
        self._search_results.clear()
        self._file_list.EnsureVisible(self._file_list.GetFirstSelected())

        self._ignore_change = False
        self._disable_editor(False, all_menu=True)

    # noinspection PyUnusedLocal
    def _handle_name_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article name field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            self._update_field_color(self._field_article_name, self._field_article_name_tip,
                                     self._current_document_instance.seo_test_name)
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
            self._update_field_color(self._field_article_date, self._field_article_date_tip,
                                     self._current_document_instance.seo_test_date)
            self._current_document_instance.set_date(self._field_article_date.GetValue())
            self._update_seo_colors()

    # noinspection PyUnusedLocal
    def _handle_keywords_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article keywords field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            self._update_field_color(self._field_article_keywords, self._field_article_keywords_tip,
                                     self._current_document_instance.seo_test_keywords)
            keywords_list = [word.strip() for word in self._field_article_keywords.GetValue().split(',')]
            self._current_document_instance.set_keywords(keywords_list)
            self._update_seo_colors()

    # noinspection PyUnusedLocal
    def _handle_description_change(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the article description field real time.
        :param event: Not used
        :return: None
        """
        if not self._ignore_change:
            self._update_description_color()
            self._current_document_instance.set_description(self._field_article_description.GetValue())
            self._update_seo_colors()

    @staticmethod
    def _update_field_color(field: wx.TextCtrl, tip: SuperToolTip, seo_test: Callable) -> None:
        """
        Set field color and tip based on the result of it's seo test.
        :param field: The field to work with.
        :param tip: The corresponding tip.
        :param seo_test: The seo method to run.
        :return: None
        """
        correct, message, color = seo_test(field.GetValue())
        field.SetBackgroundColour(color)
        tip.SetMessage(Strings.seo_check + '\n' + message)

    def _update_description_color(self) -> None:
        """
        Set meta description field color and tip based on the result of it's seo test.
        :return: None
        """
        correct, message, color = self._current_document_instance.seo_test_description(
            self._field_article_description.GetValue())

        # Set color
        self._field_article_description.SetBackgroundColour(color)
        # Set color for the current text separately, it does not work with just background color
        Tools.set_field_background(self._field_article_description, color)

        self._field_article_description_tip.SetMessage(Strings.seo_check + '\n' + message)

    # noinspection PyUnusedLocal
    def _text_area_edit_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle special events that signal that the color of the selected item in the filelist should be updated.
        This happens when an edit has been made to the document main text within dialogs like link, image and video
        edit and style/font weight which do not add any text that otherwise fires TEXT_CHANGE events. Also
        happens when an edit has been made to the side images.
        :param event: Not used.
        :return: None
        """
        # Force repeating search because the text has changed and indexes would no longer match.
        self._text_changed = True
        if not self._ignore_change:
            if event.GetInt():
                # The event will have int 1 set if change has occurred
                self._current_document_instance.set_modified(True)
            self._update_seo_colors()

    def _update_file_color(self, index: int = -1) -> None:
        """
        Change the color of the currently selected file in the filelist according to the document's state.
        :param index: The index of the file in the list that should be updated, -1 if current file.
        :return: None
        """
        if index == -1:
            index = self._file_list.GetFirstSelected()
        if index == -1:
            # Nothing is selected nor given an index to update.
            return
        doc = self._articles[self._file_list.GetItemText(index)]
        new_color = doc.get_status_color()
        if doc.is_modified and not doc.is_saved():
            self._file_list.SetItemFont(index, self.bold_small_font)
        else:
            self._file_list.SetItemFont(index, self.small_font)
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
    def _add_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle adding a new image into the image folder structure.
        :param event: Not used
        :return: None
        """
        dlg = AddImageDialog(self, self._current_document_instance.get_working_directory())
        dlg.ShowModal()
        dlg.Destroy()

    def _insert_aside_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle adding a new image into the document's aside images.
        :param event: Not used
        :return: None
        """
        # Create a new placeholder text image or video
        new_image = AsideImage('', '', '', '', '', Strings.label_none, Strings.label_none)
        # This will set the image internal state to missing image placeholder.
        new_image.test_self()
        # Open edit dialog.
        edit_dialog = EditAsideImageDialog(self, new_image, self._current_document_instance.get_working_directory())
        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            self._current_document_instance.add_aside_image(new_image)
            self._side_photo_panel.load_document_images(self._current_document_instance)
        self._update_seo_colors()
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
        dlg = AddLogoDialog(self, self._current_document_instance.get_working_directory())
        dlg.ShowModal()
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def _save_document_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles save button clicks.
        :param event: Not used.
        :return: None
        """
        if event.GetId() == wx.ID_SAVEAS:
            self._save_current_doc(save_as=True)
        else:
            self._save_current_doc()

    def _search_box_handler(self, event: wx.CommandEvent) -> None:
        """
        Forward the string we are searching for into the search method. Fires as text is being typed.
        :param event: Carries the string from search box.
        :return: None
        """
        self._search_string(event.GetString().lower())

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

        text_content: str = self._main_text_area.get_text().lower()
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
        # Scroll found text to view.
        self._main_text_area.ShowPosition(self._search_results[0])
        self._main_text_area.LayoutContent()
        return True

    # noinspection PyUnusedLocal
    def _search_tools_handler(self, event: wx.CommandEvent) -> None:
        """
        Fires on pressing the enter key inside the search box.
        :param event: Used to get the tool id.
        :return: None
        """
        if self._text_changed:
            # Repeat search when the text has changed. Indicate that text is now stable.
            # When the text changes, restart search from beginning.
            self._text_changed = False
            self._search_index = 0
            if not self._search_string(self._search_box.GetValue().lower()):
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
        # Scroll found text to view.
        self._main_text_area.ShowPosition(position)
        self._main_text_area.LayoutContent()

    # noinspection PyUnusedLocal
    def _new_file_handler(self, event: wx.CommandEvent) -> None:
        """
        Open new file dialog.
        :param event: Not used.
        :return: None
        """
        dlg = NewFileDialog(self, self._menus, self._articles, self._css_document, self._index_document)
        if dlg.ShowModal() == wx.ID_OK:
            new_document = dlg.get_new_document()
            self._articles[new_document.get_filename()] = new_document
            new_document.convert_to_html()
            if self._file_list.GetFirstSelected() == -1:
                # When no document is selected leave editor disabled after save.
                save_list = [new_document, new_document.get_menu_section(), new_document.get_index_document()]
                self._save(save_list, save_as=False, disable=True)
            else:
                save_list = [new_document, new_document.get_menu_section(), new_document.get_index_document()]
                self._save(save_list, save_as=False)
            # Add to list
            self._file_list.InsertItem(0, new_document.get_filename())
            self._set_status_text(Strings.status_articles + ' ' + str(len(self._articles)), 2)
        self._update_seo_colors()
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def _export_all_handler(self, event: wx.CommandEvent) -> None:
        """
        Export all documents to html regardless of their state.
        :param event: Not used
        :return: None
        """
        result = wx.MessageBox(Strings.label_export_all, Strings.toolbar_save, wx.YES_NO | wx.ICON_WARNING)
        if result == wx.YES:
            self._save_all()

    # noinspection PyUnusedLocal
    def _edit_menu_handler(self, event: wx.CommandEvent) -> None:
        """
        Open new file dialog.
        :param event: Not used.
        :return: None
        """
        # Save current document because menu change might require re-saving all documents.
        if self._current_document_instance:
            self._save_current_doc()
        dlg = EditMenuDialog(self, self._menus, self._config_manager.get_working_dir())
        dlg.ShowModal()
        if dlg.save_all():
            self._save_all(disable=(not bool(self._current_document_instance)))
            self._file_menu_item_new.Enable(True)
            self.tool_bar.EnableTool(wx.ID_NEW, True)
        else:
            # In case just menu description or keywords were changed, the rest of the documents do not need to be
            # saved again.
            self._save(list(self._menus.values()), save_as=False, disable=(not bool(self._current_document_instance)))
        self._update_seo_colors()
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def _page_setup_handler(self, event: wx.CommandEvent) -> None:
        """
        Open page setup dialog.
        :param event: Not used.
        :return: None
        """
        dlg = EditDefaultValuesDialog(self)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            if dlg.save_all():
                self._save_all()
            else:
                # Index might have changed so re-export it.
                self._save([self._index_document])
        self._update_seo_colors()
        dlg.Destroy()

    # noinspection PyUnusedLocal
    def _delete_article_handler(self, event: wx.CommandEvent) -> None:
        """
        Delete currently opened article html file from the drive and re-save all documents to reflect the change.
        :param event: Not used.
        :return: None
        """
        # TODO editor is not disabled immediately, same as with menu edit.
        result = wx.MessageBox(Strings.warning_delete_document + '\n' + self._current_document_name + '?',
                               Strings.status_delete, wx.YES_NO | wx.ICON_WARNING)
        if result == wx.YES:
            path = self._current_document_instance.get_path()
            if os.path.exists(path) and os.access(path, os.R_OK) and os.access(path, os.W_OK):
                os.remove(path)
                # Remove from unuploaded list if it is there.
                self._config_manager.remove_uploaded(self._current_document_name)
                self._articles.pop(self._current_document_name)
                self._file_list.DeleteItem(self._file_list.FindItem(-1, self._current_document_instance.get_filename()))
                self._save_all(disable=True)
                if self._file_list.GetItemCount() == 0:
                    self._current_document_instance = None
                    self._current_document_name = ''
                    self._clear_editor(leave_files=False)
                    self._file_menu_item_delete.Enable(False)
                    # If nothing is left there will be no threads, and so we can enable the files and new file here.
                    self._disable_editor(True, True)
                    return
                # If there are any other documents enable the editor and continue with the next document.
                self._file_list.Select(0)
                self._disable_editor(False)
                self._set_status_text(Strings.status_articles + ' ' + str(len(self._articles)), 2)
            else:
                self._show_error_dialog(Strings.warning_can_not_delete + ':\n' + path)

    # noinspection PyUnusedLocal
    def _new_dir_handler(self, event: wx.CommandEvent) -> None:
        """
        Create a new minimal whitebear directory.
        :param event: Not used.
        :return: None
        """
        dlg = wx.DirDialog(self, Strings.label_dialog_choose_wb_dir, Strings.home_directory, wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.listdir(path):
                # Directory must be empty.
                # Create new config block in yaml.
                self._config_manager.add_directory(path)
                # Populate the directory with minimal files and folder structure.
                os.makedirs(os.path.join(path, Strings.folder_images, Strings.folder_thumbnails))
                os.mkdir(os.path.join(path, Strings.folder_images, Strings.folder_originals))
                os.mkdir(os.path.join(path, Strings.folder_images, Strings.folder_logos))
                os.mkdir(os.path.join(path, Strings.folder_files))
                # Create sample background image.
                image: wx.Bitmap = Tools.create_image('')
                image_path = os.path.join(path, Strings.folder_images, Strings.file_background)
                image.SaveFile(image_path, wx.BITMAP_TYPE_JPEG)
                # Create sample header image.
                image: wx.Bitmap = Tools.create_image(Strings.page_name)
                image_path = os.path.join(path, Strings.folder_images, Strings.file_header)
                image.SaveFile(image_path, wx.BITMAP_TYPE_PNG)
                # Copy over sample styles.
                copyfile(Fetch.get_resource_path('styles.css'), os.path.join(path, 'styles.css'))
                # Save index into it.
                new_index = WhitebearDocumentIndex(os.path.join(path, 'index.html'), {}, {})
                new_index.set_page_name(Strings.home_page)
                # Disable only if editor empty.
                self._save([new_index], disable=(not bool(self._current_document_instance)))
                wx.MessageBox(Strings.warning_new_dir_created, Strings.status_warning, wx.OK | wx.ICON_WARNING)
            else:
                wx.MessageBox(Strings.warning_must_be_empty, Strings.status_error, wx.OK | wx.ICON_ERROR)

    # noinspection PyUnusedLocal
    def _upload_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle uploading dialog,
        :param event: Not used.
        :return: None
        """
        dlg = UploadDialog(self, self._articles, self._index_document, self._css_document)
        dlg.ShowModal()
        for file in dlg.get_uploaded():
            self._update_file_color(self._file_list.FindItem(-1, file))
        dlg.Destroy()

    def _online_test_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to the check menu item for online url test. Store the value in config manager.
        :param event: Used to get value.
        :return: None
        """
        if event.IsChecked():
            self._config_manager.store_online_test(True)
        else:
            self._config_manager.store_online_test(False)

    # noinspection PyUnusedLocal
    def _spellcheck_setup_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle spellcheck setup dialog.
        :param event: Not used.
        :return: None
        """
        dlg = SpellCheckSetupDialog(self)
        dlg.ShowModal()
        if dlg.rerun_spellchecks():
            self._recolor_all_documents()
            self._update_seo_colors()
        dlg.Destroy()

    def _recolor_all_documents(self) -> None:
        """
        Run self test on all documents and update their color in the file list. Including menus and index.
        :return: None
        """
        def retest_all(documents: List) -> None:
            """
            Special function that runs self test on all documents inside a thread while the editor is disabled.
            :param documents: Documents to test.
            :return: None
            """
            for doc in documents:
                doc.test_self()

        self._disable_editor(True, all_menu=True)
        document_list = list(self._articles.values())
        document_list.extend(list(self._menus.values()))
        document_list.append(self._index_document)
        thread = WorkerThread(self, function=retest_all, args=(document_list,),
                              callback=self.on_recolor_done, passing_arg=None)
        thread.start()

    # noinspection PyUnusedLocal
    def _recolor_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles callbacks from edit dialogs that require all documents to be retested because spellchecker learned new
        words.
        :param event: Not used.
        :return: None
        """
        self._recolor_all_documents()

    # noinspection PyUnusedLocal
    def on_recolor_done(self, result, return_value) -> None:
        """
        Receive the result of the link's SEO test. This is used when closing the dialog.
        :param result: None, not used
        :param return_value: None, not used.
        :return: None
        """
        for i in range(0, self._file_list.GetItemCount()):
            self._update_file_color(i)
        self._disable_editor(False)

    def _update_seo_colors(self) -> None:
        """
        Run self test on currently shown document and update the background color of all items in the loaded document.
        :return: None
        """
        # Replace the plain text version of the page in the document first from the edited but not yet saved text field.
        # Reset status color and calculate it again.
        self._current_document_instance.set_plain_text(self._main_text_area.get_text())
        # Do not run online test which is slow.
        self._current_document_instance.test_self()
        self._current_document_instance.get_index_document().test_self()
        self._current_document_instance.get_menu_section().test_self()

        self._update_article_image_sizer(self._current_document_instance.get_article_image())
        self._side_photo_panel.update_image_backgrounds()
        self._update_menu_sizer(self._current_document_instance.get_menu_item())
        self._main_text_area.update_seo_colors()
        self._update_field_color(self._field_article_date, self._field_article_date_tip,
                                 self._current_document_instance.seo_test_date)
        self._update_field_color(self._field_article_name, self._field_article_name_tip,
                                 self._current_document_instance.seo_test_name)
        self._update_field_color(self._field_article_keywords, self._field_article_keywords_tip,
                                 self._current_document_instance.seo_test_keywords)
        self._update_description_color()
        self._update_file_color()

    # noinspection PyUnusedLocal
    def _self_test_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle spellcheck dialog.
        :param event: Not used.
        :return: None
        """
        # We must run this at least once to find errors.
        self._update_seo_colors()
        # First run spellcheck dialog on metadata and article name if needed.
        for field, name in ((self._field_article_keywords, Strings.label_article_keywords),
                            (self._field_article_description, Strings.label_article_description),
                            (self._field_article_name, Strings.label_article_title)):
            dlg = SpellCheckerDialog(self, Strings.label_dialog_spellcheck + ': ' + name, field.GetValue())
            dlg.run()
            if dlg.found_mistake():
                mistakes_found = True
                if dlg.ShowModal() == wx.ID_OK:
                    # Replace text in field and recheck all seo again as a result of it. The spellchecker may have
                    # learned some new words.
                    if field.GetValue() != dlg.get_fixed_text():
                        field.SetValue(dlg.get_fixed_text())
                    self._update_seo_colors()
                    dlg.Destroy()
        # Run main text spellcheck.
        dlg = RichTextSpellCheckerDialog(self, self._main_text_area)
        dlg.run()
        if dlg.found_mistake():
            self._disable_editor(True, all_menu=True)
            dlg.Show()
        else:
            self._show_test_report()

    def _show_test_report(self) -> None:
        """
        Show an error list of red items in the document.
        :return: None
        """
        error_report = ''
        if self._current_document_instance.get_status_color() == Numbers.RED_COLOR:
            error_report += Strings.warning_errors_in_document + ':\n\n'
            # Keywords, date, description, title
            for field, name in ((self._field_article_keywords, Strings.label_article_keywords),
                                (self._field_article_description, Strings.label_article_description),
                                (self._field_article_date, Strings.label_article_date),
                                (self._field_article_name, Strings.label_article_title)):
                if field.GetBackgroundColour() == Numbers.RED_COLOR:
                    error_report += name + '\n'
            # Menu item
            if self._current_document_instance.get_menu_item().get_status_color() == wx.RED:
                error_report += Strings.warning_menu_item + '\n'
            # Main image
            if self._current_document_instance.get_article_image().get_status_color() == wx.RED:
                error_report += Strings.warning_main_image + '\n'
            # Aside images
            for img in self._current_document_instance.get_aside_images():
                if img.get_status_color() == wx.RED:
                    error_report += Strings.warning_aside_image + ': ' + img.get_caption()[0] + '\n'
            # Text images
            for img in self._current_document_instance.get_text_images():
                if img.get_status_color() == wx.RED:
                    error_report += Strings.warning_text_image + ': ' + img.get_link_title()[0] + '\n'
            # Text videos
            for vid in self._current_document_instance.get_videos():
                if vid.get_status_color() == wx.RED:
                    error_report += Strings.warning_text_video + ': ' + vid.get_title()[0] + '\n'
            # Text links
            for link in self._current_document_instance.get_links():
                if link.get_status_color() == wx.RED:
                    error_report += Strings.warning_text_link + ': ' + link.get_text()[0] + '\n'
            # Main text spellcheck
            if not self._current_document_instance.is_spellcheck_ok():
                error_report += Strings.warning_text_spelling + '\n'
            # Menu page
            if self._current_document_instance.get_menu_section().get_status_color() == Numbers.RED_COLOR:
                error_report += Strings.warning_menu_page + '\n'
            # Index page
            if self._current_document_instance.get_index_document().get_status_color() == Numbers.RED_COLOR:
                error_report += Strings.warning_index + '\n'

        if not error_report:
            wx.MessageBox(Strings.warning_no_mistake, Strings.label_dialog_self_test, wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(error_report, Strings.label_dialog_self_test, wx.OK | wx.ICON_INFORMATION)

    def _spellcheck_done_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle enabling the editor when spell checking dialog is closed.
        :param event: Used to recolor all documents if the word lists changed in the dialog.
        :return: None
        """
        self._main_text_area.SelectNone()
        if event.GetInt() == 1:
            self._recolor_all_documents()
        else:
            self._disable_editor(False)
        self._update_seo_colors()
        self._show_test_report()
