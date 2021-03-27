import os
from typing import Dict

import wx
import wx.html

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex


class UploadDialog(wx.Dialog):

    def __init__(self, parent, articles: Dict[str, WhitebearDocumentArticle],
                 index: WhitebearDocumentIndex, css: WhitebearDocumentCSS):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE, title=Strings.label_upload,
                           size=(Numbers.upload_dialog_width, Numbers.upload_dialog_height))
        self.small_font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._articles = articles
        self._index = index
        self._css = css
        self._upload_dict: Dict[int, str] = {}
        self._counter = 0

        self._main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # File list sizer
        self._filelist_sizer = wx.BoxSizer(wx.VERTICAL)
        self._file_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self._file_list.SetFont(self.small_font)
        self._file_list.InsertColumn(0, Strings.label_files_to_upload, format=wx.LIST_FORMAT_LEFT)
        self._file_list.SetColumnWidth(0, Numbers.upload_filelist_width)
        self._file_list.EnableCheckBoxes()
        self._add_button = wx.Button(self, wx.ID_ADD, Strings.button_add)
        self._filelist_sizer.Add(self._file_list, flag=wx.EXPAND, border=Numbers.widget_border_size, proportion=1)
        self._filelist_sizer.Add(self._add_button, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP,
                                 border=Numbers.widget_border_size)

        self._main_horizontal_sizer.Add(self._filelist_sizer, flag=wx.EXPAND | wx.ALL,
                                        border=Numbers.widget_border_size)
        self.SetSizer(self._main_horizontal_sizer)

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self._check_handler, self._file_list)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._add_button)

        self._display_dialog_contents()
        
    def _get_id(self) -> int:
        """
        Return a new unique int id.
        :return: A new unique int id.
        """
        self._counter = self._counter + 1
        return self._counter

    def _handle_buttons(self, event: wx.ListEvent) -> None:
        """
        Handle button clicks.
        :param event: Used to identify the button.
        :return: None
        """
        if event.GetId() == wx.ID_ADD:
            path = self._ask_for_file()
            if path:
                if not self._config_manager.get_working_dir() in path:
                    wx.MessageBox(Strings.file + ':\n' + path + '\nNot in:\n' + self._config_manager.get_working_dir(),
                                  Strings.status_error, wx.OK | wx.ICON_WARNING)
                else:
                    file_id = self._get_id()
                    self._upload_dict[file_id] = path
                    self._append_into_list(file_id, path)

    def _ask_for_file(self) -> str:
        """
        Show a file picker dialog to get additional files from the user.
        :return: File path or empty string if canceled.
        """
        with wx.FileDialog(self, Strings.label_select_file, self._config_manager.get_working_dir(),
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                return dlg.GetPath()
            return ''

    def _check_handler(self, event: wx.ListEvent) -> None:
        """
        Handle list item check boxes.
        :param event: Used to identify which item is checked.
        :return: None
        """
        item_id = event.GetItem().GetData()
        path = self._upload_dict[item_id]
        if not os.access(path, os.R_OK) or not os.path.exists(path):
            wx.MessageBox(Strings.warning_file_inaccessible + ':\n' + path,
                          Strings.status_warning, wx.OK | wx.ICON_WARNING)
            self._file_list.CheckItem(event.GetIndex(), False)

    def _display_dialog_contents(self) -> None:
        """
        Display the contents of dialog.
        :return: None
        """
        # todo and add option to add custom. Only allow seo passed documents.
        for filename, document in self._articles.items():
            # Add article files
            if document.get_html_to_save() and document.is_seo_ok():
                # Add all that belongs to this document into the list and check it.
                # Add the menu of this document to the list too.
                self._upload_dict[self._get_id()] = document.get_menu_section().get_path()
                self._upload_dict[self._get_id()] = document.get_path()
                self._upload_dict[self._get_id()] = document.get_article_image().get_original_image_path()
                self._upload_dict[self._get_id()] = document.get_article_image().get_thumbnail_image_path()
                self._upload_dict[self._get_id()] = document.get_menu_item().get_image_path()
                for image in document.get_aside_images():
                    # Add all aside images and thumbnails
                    self._upload_dict[self._get_id()] = image.get_original_image_path()
                    self._upload_dict[self._get_id()] = image.get_thumbnail_image_path()
                for image in document.get_text_images():
                    self._upload_dict[self._get_id()] = image.get_original_image_path()
                    self._upload_dict[self._get_id()] = image.get_thumbnail_image_path()
                for link in document.get_links():
                    # Add all files and images that are linked from the article
                    if link.get_url()[0].startswith(Strings.folder_files):
                        self._upload_dict[self._get_id()] = os.path.join(self._config_manager.get_working_dir(),
                                                                         link.get_url()[0])

        if self._upload_dict:
            # If any files were changed, add index, robots and sitemap.
            self._upload_dict[self._get_id()] = self._index.get_path()
            self._upload_dict[self._get_id()] = os.path.join(self._config_manager.get_working_dir(),
                                                             Strings.robots_file)
            self._upload_dict[self._get_id()] = os.path.join(self._config_manager.get_working_dir(),
                                                             Strings.sitemap_file)

        for item_id, file in sorted(self._upload_dict.items()):
            self._append_into_list(item_id, file)

    def _append_into_list(self, item_id: int, path: str) -> None:
        """
        Append a file into the file list.
        :param item_id: Int id.
        :param path: Disk path.
        :return: None
        """
        index = self._file_list.InsertItem(self._file_list.GetItemCount(),
                                           os.path.join(os.path.basename(os.path.dirname(path)),
                                                        os.path.basename(path)))
        self._file_list.SetItemData(index, item_id)
        self._file_list.CheckItem(index, True)