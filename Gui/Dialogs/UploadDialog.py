import os
from typing import Dict, List

import wx
import wx.html

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu


class UploadDialog(wx.Dialog):

    def __init__(self, parent, articles: Dict[str, WhitebearDocumentArticle],
                 menus: Dict[str, WhitebearDocumentMenu], index: WhitebearDocumentIndex, css: WhitebearDocumentCSS):
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
        self._menus = menus
        self._index = index
        self._css = css
        self._upload_list: List[str] = []

        self._main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._filelist_sizer = wx.BoxSizer(wx.VERTICAL)
        self._file_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self._file_list.SetFont(self.small_font)
        self._file_list.InsertColumn(0, Strings.label_files_to_upload, format=wx.LIST_FORMAT_LEFT)
        self._file_list.SetColumnWidth(0, Numbers.initial_panel_size)
        self._file_list.EnableCheckBoxes()

        self._filelist_sizer.Add(self._file_list, flag=wx.EXPAND, border=Numbers.widget_border_size, proportion=1)
        self._main_horizontal_sizer.Add(self._filelist_sizer, flag=wx.EXPAND)
        self.SetSizer(self._main_horizontal_sizer)
        self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the contents of dialog.
        :return: None
        """
        # todo List all changed files and their images or files they point to + sitemap, robots,
        # todo and add option to add custom. Only allow seo passed documents.
        for filename, document in self._articles.items():
            # Add article files
            if document.get_html_to_save() and document.is_seo_ok():
                # Add all that belongs to this document into the list and check it.
                self._upload_list.append(document.get_path())
                self._upload_list.append(document.get_article_image().get_original_image_path())
                self._upload_list.append(document.get_article_image().get_thumbnail_image_path())
                self._upload_list.append(document.get_menu_item().get_image_path())
                for image in document.get_aside_images():
                    # Add all aside images and thumbnails
                    self._upload_list.append(image.get_original_image_path())
                    self._upload_list.append(image.get_thumbnail_image_path())
                for link in document.get_links():
                    # Add all files and images that are linked from the article
                    print(link)

        for filename, document in self._menus.items():
            # Add menu files
            if document.get_html_to_save() and document.is_seo_ok():
                self._upload_list.append(document.get_path())

        if self._upload_list:
            # If any files were changed, add index, robots and sitemap.
            self._upload_list.append(self._index.get_path())
            self._upload_list.append(os.path.join(self._config_manager.get_working_dir(), Strings.robots_file))
            self._upload_list.append(os.path.join(self._config_manager.get_working_dir(), Strings.sitemap_file))
        for file in sorted(self._upload_list):
            # todo show last folder and filename
            self._file_list.InsertItem(self._file_list.GetItemCount(), os.path.basename(file))
