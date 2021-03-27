import os
from typing import Dict

import wx

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex
from Tools.Tools import Tools


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
        self._right_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._config_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, Strings.label_sftp)
        self._upload_info_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, Strings.label_upload_information)

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

        # IP, port sizer
        self._ip_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_ip_port = wx.StaticText(self, -1, Strings.label_ip_port + ': ')
        self._field_ip = wx.TextCtrl(self, -1)
        self._ip_sub_sizer.Add(self._label_ip_port, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._ip_sub_sizer.Add(4, -1)
        self._ip_sub_sizer.Add(self._field_ip, proportion=1)
        self._config_sizer.Add(self._ip_sub_sizer, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                               border=Numbers.widget_border_size)
        self._field_ip_port_tip = Tools.get_warning_tip(self._field_ip, Strings.label_ip_port)
        self._field_ip_port_tip.SetMessage('')

        # User
        self._user_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_user = wx.StaticText(self, -1, Strings.label_user + ': ')
        self._field_user = wx.TextCtrl(self, -1)
        self._user_sub_sizer.Add(self._label_user, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._user_sub_sizer.Add(17, -1)
        self._user_sub_sizer.Add(self._field_user, proportion=1)
        self._config_sizer.Add(self._user_sub_sizer, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                               border=Numbers.widget_border_size)
        self._field_user_tip = Tools.get_warning_tip(self._field_user, Strings.label_user)
        self._field_user_tip.SetMessage('')

        # Key file
        self._keyfile_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_keyfile = wx.StaticText(self, -1, Strings.label_key_file + ': ')
        self._field_keyfile = wx.TextCtrl(self, -1)
        self._keyfile_button = wx.Button(self, wx.ID_OPEN, Strings.button_browse)
        self._keyfile_sub_sizer.Add(self._label_keyfile, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._keyfile_sub_sizer.Add(self._field_keyfile, proportion=1)
        self._keyfile_sub_sizer.Add(self._keyfile_button, flag=wx.LEFT, border=Numbers.widget_border_size)
        self._config_sizer.Add(self._keyfile_sub_sizer, flag=wx.EXPAND | wx.ALL,
                               border=Numbers.widget_border_size)
        self._field_keyfile_tip = Tools.get_warning_tip(self._field_keyfile, Strings.label_key_file)
        self._field_keyfile_tip.SetMessage('')

        # Upload bar
        self._gauge_sizer = wx.BoxSizer(wx.VERTICAL)
        self._upload_gauge = wx.Gauge(self, -1, style=wx.GA_VERTICAL)
        self._upload_gauge.SetRange(100)
        self._upload_gauge.SetValue(1)
        self._gauge_sizer.Add(self._upload_gauge, 1, flag=wx.EXPAND)

        # Upload statistics
        self._info_left_sizer = wx.BoxSizer(wx.VERTICAL)
        self._info_right_sizer = wx.BoxSizer(wx.VERTICAL)

        self._label_num_files = wx.StaticText(self, -1, Strings.label_files_to_upload + ':')
        self._content_num_files = wx.StaticText(self, -1, '0')
        self._info_left_sizer.Add(self._label_num_files, flag=wx.BOTTOM, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_num_files, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_successful = wx.StaticText(self, -1, Strings.label_successful_uploads + ':')
        self._content_successful = wx.StaticText(self, -1, '0')
        self._info_left_sizer.Add(self._label_successful, flag=wx.BOTTOM, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_successful, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_failed = wx.StaticText(self, -1, Strings.label_failed_uploads + ':')
        self._content_failed = wx.StaticText(self, -1, '0')
        self._info_left_sizer.Add(self._label_failed, flag=wx.BOTTOM, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_failed, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_current_file = wx.StaticText(self, -1, Strings.label_uploading_file + ':')
        self._content_current_file = wx.StaticText(self, -1, Strings.label_none)
        self._info_left_sizer.Add(self._label_current_file, flag=wx.BOTTOM, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_current_file, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._upload_info_sizer.Add(self._info_left_sizer, 1, flag=wx.EXPAND)
        self._upload_info_sizer.Add(self._info_right_sizer, 2, flag=wx.EXPAND)

        # Put it all together
        self._right_vertical_sizer.Add(self._config_sizer, flag=wx.RIGHT | wx.EXPAND,
                                       border=Numbers.widget_border_size)
        self._right_vertical_sizer.Add(self._upload_info_sizer, flag=wx.RIGHT | wx.EXPAND,
                                       border=Numbers.widget_border_size)
        self._main_horizontal_sizer.Add(self._filelist_sizer, flag=wx.EXPAND | wx.ALL,
                                        border=Numbers.widget_border_size)
        self._main_horizontal_sizer.Add(self._right_vertical_sizer, 1, flag=wx.EXPAND)
        self._main_horizontal_sizer.Add(self._gauge_sizer, flag=wx.EXPAND)

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
                if not path.startswith(self._config_manager.get_working_dir()):
                    wx.MessageBox(Strings.file + ':\n' + path + '\nNot in:\n' + self._config_manager.get_working_dir(),
                                  Strings.status_error, wx.OK | wx.ICON_WARNING)
                else:
                    if path not in self._upload_dict.values():
                        file_id = self._get_id()
                        self._upload_dict[file_id] = path
                        self._append_into_list(file_id, path)
        '''
        # todo do this on upload
        # Set the gauge to the amount of checked items
        counter = 0
        item = -1
        while 1:
            item = self._file_list.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
            if item == -1:
                break
            elif self._file_list.IsItemChecked(item):
                counter = counter + 1
        print(counter)
        '''

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
