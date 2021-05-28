import os
import stat
from typing import Dict, List, Tuple

import wx

from Constants.Constants import Strings, Numbers
from Resources.Fetch import Fetch
from Threads.SftpThread import SftpThread
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
        self.bold_small_font = wx.Font(Numbers.text_field_font_size, wx.FONTFAMILY_DEFAULT,
                                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._articles = articles
        self._index = index
        self._css = css
        # Contains unique id and disk path for each file in the file list even those unchecked.
        self._upload_dict: Dict[int, str] = {}
        self._counter = 0
        self._sftp_thread = None

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
        self._field_ip_port = wx.TextCtrl(self, -1)
        self._ip_sub_sizer.Add(self._label_ip_port, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._ip_sub_sizer.Add(4, -1)
        self._ip_sub_sizer.Add(self._field_ip_port, proportion=1)
        self._config_sizer.Add(self._ip_sub_sizer, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                               border=Numbers.widget_border_size)
        self._field_ip_port_tip = Tools.get_warning_tip(self._field_ip_port, Strings.label_ip_port)
        self._field_ip_port_tip.SetMessage(Strings.label_ip_port_tip)

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
        self._field_user_tip.SetMessage(Strings.label_user_tip)

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
        self._field_keyfile_tip.SetMessage(Strings.label_key_file_tip)

        # Upload bar
        self._gauge_sizer = wx.BoxSizer(wx.VERTICAL)
        self._upload_gauge = wx.Gauge(self, -1, style=wx.GA_VERTICAL)
        self._upload_gauge.SetRange(100)
        self._upload_gauge.SetValue(1)
        self._gauge_sizer.Add(self._upload_gauge, 1, flag=wx.EXPAND)

        # Upload statistics
        self._info_left_sizer = wx.BoxSizer(wx.VERTICAL)
        self._info_right_sizer = wx.BoxSizer(wx.VERTICAL)

        self._label_connection = wx.StaticText(self, -1, Strings.label_connection + ':')
        self._content_connection = wx.StaticText(self, -1, Strings.status_none)
        self._info_left_sizer.Add(self._label_connection, flag=wx.BOTTOM | wx.LEFT, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_connection, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_num_files = wx.StaticText(self, -1, Strings.label_files_to_upload + ':')
        self._content_num_files = wx.StaticText(self, -1, '0')
        self._info_left_sizer.Add(self._label_num_files, flag=wx.BOTTOM | wx.LEFT, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_num_files, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_successful = wx.StaticText(self, -1, Strings.label_successful_uploads + ':')
        self._content_successful = wx.StaticText(self, -1, '0')
        self._content_successful.SetForegroundColour(Numbers.DARK_GREEN_COLOR)
        self._info_left_sizer.Add(self._label_successful, flag=wx.BOTTOM | wx.LEFT, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_successful, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_failed = wx.StaticText(self, -1, Strings.label_failed_uploads + ':')
        self._content_failed = wx.StaticText(self, -1, '0')
        self._content_failed.SetForegroundColour(wx.RED)
        self._info_left_sizer.Add(self._label_failed, flag=wx.BOTTOM | wx.LEFT, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_failed, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._label_current_file = wx.StaticText(self, -1, Strings.label_uploading_file + ':')
        self._content_current_file = wx.StaticText(self, -1, Strings.label_none,
                                                   style=wx.ST_ELLIPSIZE_MIDDLE)
        self._info_left_sizer.Add(self._label_current_file, flag=wx.BOTTOM | wx.LEFT, border=Numbers.widget_border_size)
        self._info_right_sizer.Add(self._content_current_file, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._content_percentage = wx.StaticText(self, -1, '0 %')
        self._info_right_sizer.Add(self._content_percentage, flag=wx.BOTTOM, border=Numbers.widget_border_size)

        self._upload_info_sizer.Add(self._info_left_sizer, 1, flag=wx.EXPAND)
        self._upload_info_sizer.Add(self._info_right_sizer, 2, flag=wx.EXPAND)

        self._structure_message = wx.StaticText(self, -1, Strings.label_server_structure)
        self._overwrite_message = wx.StaticText(self, -1, Strings.label_server_overwrite)

        # Upload button
        self._upload_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._upload_button = wx.Button(self, wx.ID_FILE, Strings.button_upload, style=wx.BU_EXACTFIT)
        self._button_to_upload()
        self._upload_button_sizer.AddStretchSpacer()
        self._upload_button_sizer.Add(self._upload_button, flag=wx.ALIGN_CENTER)
        self._upload_button_sizer.AddStretchSpacer()

        # Put it all together
        self._right_vertical_sizer.Add(self._config_sizer, flag=wx.RIGHT | wx.EXPAND,
                                       border=Numbers.widget_border_size)
        self._right_vertical_sizer.Add(self._upload_info_sizer, flag=wx.RIGHT | wx.EXPAND,
                                       border=Numbers.widget_border_size)
        self._right_vertical_sizer.Add(self._structure_message)
        self._right_vertical_sizer.Add(self._overwrite_message)
        self._right_vertical_sizer.Add(self._upload_button_sizer, 1, flag=wx.EXPAND)
        self._main_horizontal_sizer.Add(self._filelist_sizer, flag=wx.EXPAND | wx.ALL,
                                        border=Numbers.widget_border_size)
        self._main_horizontal_sizer.Add(self._right_vertical_sizer, 1, flag=wx.EXPAND)
        self._main_horizontal_sizer.Add(self._gauge_sizer, flag=wx.EXPAND)

        self.SetSizer(self._main_horizontal_sizer)

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self._check_handler, self._file_list)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self._check_handler, self._file_list)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._add_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._keyfile_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._upload_button)
        self.Bind(wx.EVT_TEXT, self._handle_fields, self._field_ip_port)
        self.Bind(wx.EVT_TEXT, self._handle_fields, self._field_user)
        self.Bind(wx.EVT_TEXT, self._handle_fields, self._field_keyfile)
        self.Bind(wx.EVT_CLOSE, self._close_button_handler, self)

        self._display_dialog_contents()

    def on_key_password_required(self) -> None:
        """
        Ask the user for private key passphrase and restart the connection.
        :return: None
        """
        dlg = wx.PasswordEntryDialog(self, Strings.label_rsa_passphrase + ':', Strings.warning_rsa_passphrase)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            self._upload_files(dlg.GetValue())
        dlg.Destroy()

    def _button_to_upload(self) -> None:
        """
        Change the upload button to the default upload state.
        :return: None
        """
        self._upload_button.SetBitmap(wx.Bitmap(Fetch.get_resource_path('upload.png'), wx.BITMAP_TYPE_PNG))
        self._upload_button.SetBitmapPosition(wx.TOP)
        self._upload_button.SetLabelText(Strings.button_upload)

    def _button_to_cancel(self) -> None:
        """
        Change the upload button to the cancel upload state.
        :return: None
        """
        self._upload_button.SetBitmap(wx.Bitmap(Fetch.get_resource_path('upload_cancel.png'), wx.BITMAP_TYPE_PNG))
        self._upload_button.SetBitmapPosition(wx.TOP)
        self._upload_button.SetLabelText(Strings.button_cancel)

    def on_key_password_wrong(self) -> None:
        """
        Display an error message saying the passphrase was wrong.
        :return: None
        """
        wx.MessageBox(Strings.warning_rsa_passphrase_wrong, Strings.status_error, wx.OK | wx.ICON_ERROR)
        self._button_to_upload()
        self._content_connection.SetLabelText(Strings.status_failed)
        # Enable the upload button again if possible.
        self._validate_fields()

    def on_connection_closed(self, status: str) -> None:
        """
        Change the connection label in GUI to a new message and reset gui.
        :param status: The status of the connection.
        :return: None
        """
        self._content_connection.SetLabelText(status)
        self._button_to_upload()
        # Enable the upload button again if possible.
        self._validate_fields()
        self._disable_controls(True)

    def on_connection_established(self, status: str) -> None:
        """
        Change the connection label in GUI to a new message.
        :param status: The status of the connection.
        :return: None
        """
        self._content_connection.SetLabelText(status)
        # Enable the upload button again if possible.
        self._validate_fields()

    @staticmethod
    def on_structure_repair() -> None:
        """
        Display a message that the folder structure on server was repaired.
        :return: None
        """
        wx.MessageBox(Strings.warning_server_folders_repaired, Strings.status_warning, wx.OK | wx.ICON_WARNING)

    def on_file_upload_start(self, file: str) -> None:
        """
        Update the uploading file label.
        :param file: The file.
        :return: None
        """
        self._content_current_file.SetLabelText(os.path.relpath(file, start=self._config_manager.get_working_dir()))

    def on_file_upload_finished(self, file: str, fail: bool) -> None:
        """
        Called when SFTP put finishes uploading a file or finishes with fail. Updates the file list to indicate finished
        upload and updates finished upload counters.
        :param file: The local file path.
        :param fail: True if transfer failed.
        :return: None
        """
        if fail:
            color = Numbers.RED_COLOR
        else:
            color = Numbers.GREEN_COLOR
            # Remove successful uploads from the list of unuploaded files.
            self._config_manager.remove_uploaded(os.path.basename(file))
        index = self._file_list.FindItem(0, os.path.relpath(file, start=self._config_manager.get_working_dir()))
        if index > -1:
            self._file_list.SetItemBackgroundColour(index, color)
        # Update the transfers counters to the number of red/green files.
        item = -1
        counter_red = 0
        counter_green = 0
        while 1:
            item = self._file_list.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
            if item == -1:
                break
            elif self._file_list.GetItemBackgroundColour(item) == Numbers.GREEN_COLOR:
                counter_green = counter_green + 1
            elif self._file_list.GetItemBackgroundColour(item) == Numbers.RED_COLOR:
                counter_red = counter_red + 1
        self._content_successful.SetLabelText(str(counter_green))
        self._content_failed.SetLabelText(str(counter_red))
        self._upload_gauge.SetValue(counter_green)

    def on_percentage_update(self, percentage: float) -> None:
        """
        Update the percentage of file upload.
        :param percentage: The new value.
        :return: None
        """
        formatted = "{:4.1f}".format(percentage)
        self._content_percentage.SetLabelText(formatted + ' %')

    def _upload_files(self, password=None) -> None:
        """
        Run a SFTP thread to upload the files.
        :param password: RSA private key password.
        :return: None
        """
        ip, port = self._field_ip_port.GetValue().split(':', 2)
        # Contains tuples (full disk path, relative path on server)
        files_to_upload: List[Tuple[str, str]] = []
        self._content_connection.SetLabelText(Strings.status_connecting)
        self._button_to_cancel()
        self._upload_button.Disable()
        self._disable_controls(False)
        item = -1
        while 1:
            item = self._file_list.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
            if item == -1:
                break
            elif self._file_list.IsItemChecked(item):
                # Item data carries a key into the dictionary of all files in the list.
                local_path = self._upload_dict[self._file_list.GetItem(item).GetData()]
                ftp_path = os.path.join('.', os.path.relpath(local_path, start=self._config_manager.get_working_dir()))
                files_to_upload.append((local_path, ftp_path))
            # Reset item background color
            self._file_list.SetItemBackgroundColour(item, wx.WHITE)

        self._sftp_thread = SftpThread(self, ip, int(port), self._field_user.GetValue(), self._field_keyfile.GetValue(),
                                       password, files_to_upload)
        self._upload_gauge.SetRange(len(files_to_upload))
        self._upload_gauge.SetValue(0)
        if files_to_upload:
            self._sftp_thread.start()

    def _disable_controls(self, enable: bool) -> None:
        """
        Disable all controls except the upload button.
        :param enable: True to disable.
        :return: None
        """
        self._add_button.Enable(enable)
        self._keyfile_button.Enable(enable)
        self._field_ip_port.Enable(enable)
        self._field_user.Enable(enable)
        self._field_keyfile.Enable(enable)

    def _get_id(self) -> int:
        """
        Return a new unique int id.
        :return: A new unique int id.
        """
        self._counter = self._counter + 1
        return self._counter

    # noinspection PyUnusedLocal
    def _handle_fields(self, event: wx.ListEvent) -> None:
        """
        Handle fields edits.
        :param event: Not used.
        :return: None
        """
        self._validate_fields()

    def _handle_buttons(self, event: wx.ListEvent) -> None:
        """
        Handle button clicks.
        :param event: Used to identify the button.
        :return: None
        """
        if event.GetId() == wx.ID_ADD:
            path = self._ask_for_file(self._config_manager.get_working_dir())
            if path:
                if not path.startswith(self._config_manager.get_working_dir()):
                    wx.MessageBox(Strings.file + ':\n' + path + '\nNot in:\n' + self._config_manager.get_working_dir(),
                                  Strings.status_error, wx.OK | wx.ICON_WARNING)
                else:
                    if path not in self._upload_dict.values():
                        file_id = self._get_id()
                        self._upload_dict[file_id] = path
                        self._append_into_list(file_id, path)
        elif event.GetId() == wx.ID_OPEN:
            path = self._ask_for_file(Strings.home_directory)
            if path:
                self._field_keyfile.SetValue(path)
        elif event.GetId() == wx.ID_FILE:
            if self._upload_button.GetLabel() == Strings.button_upload:
                self._upload_files()
            elif self._sftp_thread.is_alive():
                self._sftp_thread.stop()

    def _close_button_handler(self, event: wx.CloseEvent) -> None:
        """
        Handle closing of the dialog. If the upload thread is running warn the user and offer unsafe force stop.
        :param event: Not used
        :return: None
        """
        if event.CanVeto():
            if self._sftp_thread and self._sftp_thread.is_alive():
                # There may be no thread if the upload was not even started.
                result = wx.MessageBox(Strings.warning_upload_unfinished, Strings.status_warning,
                                       wx.YES_NO | wx.ICON_WARNING)
                if result == wx.YES:
                    self._sftp_thread.stop(force=True)
                    self._sftp_thread.join()
                    event.Skip()
                else:
                    event.Veto()
                    return
            else:
                event.Skip()

    def _ask_for_file(self, path: str) -> str:
        """
        Show a file picker dialog to get additional files from the user.
        :param path: The directory which the file picker opens.
        :return: File path or empty string if canceled.
        """
        with wx.FileDialog(self, Strings.label_select_file, path, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST |
                           wx.FD_PREVIEW) as dlg:
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
        if self._file_list.IsItemChecked(event.GetIndex()):
            item_id = event.GetItem().GetData()
            path = self._upload_dict[item_id]
            if not os.access(path, os.R_OK) or not os.path.exists(path):
                wx.MessageBox(Strings.warning_file_inaccessible + ':\n' + path,
                              Strings.status_warning, wx.OK | wx.ICON_WARNING)
                self._file_list.CheckItem(event.GetIndex(), False)
        self._content_num_files.SetLabelText(str(self._count_checked_files()))
        self._validate_fields()

    def _count_checked_files(self) -> int:
        """
        Return the number of files currently checked in the file list.
        :return: The number of files currently checked in the file list.
        """
        counter: int = 0
        item = -1
        while 1:
            item = self._file_list.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
            if item == -1:
                break
            elif self._file_list.IsItemChecked(item):
                counter = counter + 1
        return counter

    def _display_dialog_contents(self) -> None:
        """
        Display the contents of dialog.
        :return: None
        """
        self.Disable()
        for filename, document in self._articles.items():
            # Add article files
            if document.get_html_to_save() and document.is_seo_ok():
                # Add all that belongs to this document into the list and check it.
                # Add the menu of this document to the list too.
                self._add_if_not_in(document.get_menu_section().get_path())
                self._add_if_not_in(document.get_path())
                self._add_if_not_in(document.get_article_image().get_original_image_path())
                self._add_if_not_in(document.get_article_image().get_thumbnail_image_path())
                self._add_if_not_in(document.get_menu_item().get_image_path())
                for image in document.get_aside_images():
                    # Add all aside images and thumbnails
                    self._add_if_not_in(image.get_original_image_path())
                    self._add_if_not_in(image.get_thumbnail_image_path())
                for image in document.get_text_images():
                    self._add_if_not_in(image.get_original_image_path())
                    self._add_if_not_in(image.get_thumbnail_image_path())
                for link in document.get_links():
                    # Add all files and images that are linked from the article
                    if link.get_url()[0].startswith(Strings.folder_files):
                        self._add_if_not_in(os.path.join(self._config_manager.get_working_dir(), link.get_url()[0]))

        if self._upload_dict:
            # If any files were changed, add index, robots and sitemap.
            self._add_if_not_in(self._index.get_path())
            self._add_if_not_in(self._css.get_path())
            self._add_if_not_in(os.path.join(self._config_manager.get_working_dir(), Strings.robots_file))
            self._add_if_not_in(os.path.join(self._config_manager.get_working_dir(), Strings.sitemap_file))

        for item_id, file in sorted(self._upload_dict.items()):
            self._append_into_list(item_id, file)

        # Fill SFTP config
        self._field_ip_port.SetValue(self._config_manager.get_ip_port())
        self._field_user.SetValue(self._config_manager.get_user())
        self._field_keyfile.SetValue(self._config_manager.get_keyfile())
        self.Enable()

    def _add_if_not_in(self, new_path: str) -> None:
        """
        Add file_id and file path to upload dict if it is not there already.
        :param new_path: The file path
        :return: None
        """
        for _, file_path in sorted(self._upload_dict.items()):
            if file_path == new_path:
                return
        # Add the new file with a new id.
        self._upload_dict[self._get_id()] = new_path

    def _validate_fields(self) -> bool:
        """
        Validate configuration fields.
        :return: True if validation passed
        """
        result = True
        # Check IP:port
        ip_port = self._field_ip_port.GetValue().split(':', 2)
        try:
            if not self._field_ip_port.GetValue():
                self._field_ip_port_tip.SetMessage(Strings.label_ip_port_tip)
                Tools.set_field_background(self._field_ip_port, Numbers.RED_COLOR)
            elif len(ip_port) > 2 or len(ip_port) < 2 or not ip_port[0] or not ip_port[1]:
                self._field_ip_port_tip.SetMessage(Strings.warning_incorrect_format)
                Tools.set_field_background(self._field_ip_port, Numbers.RED_COLOR)
                result = False
            elif int(ip_port[1]) < 1 or int(ip_port[1]) > 65535:
                self._field_ip_port_tip.SetMessage(Strings.warning_incorrect_port)
                Tools.set_field_background(self._field_ip_port, Numbers.RED_COLOR)
                result = False
            ip = ip_port[0].split('.', 4)
            if len(ip) < 4 or len(ip) > 4 or not ip:
                self._field_ip_port_tip.SetMessage(Strings.warning_incorrect_ip_format)
                Tools.set_field_background(self._field_ip_port, Numbers.RED_COLOR)
                result = False
            for num in ip:
                if int(num) < 0 or int(num) > 255:
                    self._field_ip_port_tip.SetMessage(Strings.warning_incorrect_ip_format)
                    Tools.set_field_background(self._field_ip_port, Numbers.RED_COLOR)
                    result = False
        except ValueError as _:
            self._field_ip_port_tip.SetMessage(Strings.warning_incorrect_format)
            Tools.set_field_background(self._field_ip_port, Numbers.RED_COLOR)
            result = False
        if result:
            self._field_ip_port_tip.SetMessage(Strings.label_ip_port_tip)
            Tools.set_field_background(self._field_ip_port, Numbers.GREEN_COLOR)
            self._config_manager.store_ip_port(self._field_ip_port.GetValue())

        # Check username
        username = self._field_user.GetValue()
        if len(username) > Numbers.default_max_length or len(username) < 1:
            self._field_user_tip.SetMessage(Strings.seo_error_length + ': 1-' + str(Numbers.default_max_length))
            Tools.set_field_background(self._field_user, Numbers.RED_COLOR)
            result = False
        else:
            self._field_user_tip.SetMessage(Strings.label_user_tip)
            Tools.set_field_background(self._field_user, Numbers.GREEN_COLOR)
            self._config_manager.store_user(self._field_user.GetValue())

        # Check keyfile existence
        key_path = self._field_keyfile.GetValue()
        if not os.path.exists(key_path) or not os.access(key_path, os.R_OK):
            self._field_keyfile_tip.SetMessage(Strings.warning_keyfile_inaccessible)
            Tools.set_field_background(self._field_keyfile, Numbers.RED_COLOR)
            result = False
        elif oct(stat.S_IMODE(os.stat(key_path).st_mode)) != oct(Numbers.private_key_permissions):
            self._field_keyfile_tip.SetMessage(Strings.warning_keyfile_permissions)
            Tools.set_field_background(self._field_keyfile, Numbers.RED_COLOR)
            result = False
        else:
            self._field_keyfile_tip.SetMessage(Strings.label_key_file_tip)
            Tools.set_field_background(self._field_keyfile, Numbers.GREEN_COLOR)
            self._config_manager.store_keyfile(self._field_keyfile.GetValue())

        if not result or self._count_checked_files() == 0:
            self._upload_button.Disable()
        else:
            self._upload_button.Enable()
        return result

    def _append_into_list(self, item_id: int, path: str) -> None:
        """
        Append a file into the file list.
        :param item_id: Int id.
        :param path: Disk path.
        :return: None
        """
        index = self._file_list.InsertItem(self._file_list.GetItemCount(),
                                           os.path.relpath(path, start=self._config_manager.get_working_dir()))
        self._file_list.SetItemData(index, item_id)

        if not path.startswith(os.path.join(self._config_manager.get_working_dir(), Strings.folder_images)):
            self._file_list.SetItemFont(index, self.bold_small_font)
        self._file_list.CheckItem(index, True)
