import os

import wx

from Constants.Constants import Strings, Numbers
from Resources.Fetch import Fetch
from Tools.Tools import Tools


class AddLogoDialog(wx.Dialog):

    def __init__(self, parent, work_dir: str):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param work_dir: The working directory of the editor.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_add_logo,
                           size=(Numbers.add_logo_dialog_width, Numbers.add_logo_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_path = None
        self._image_name = None
        self._menu_image = None
        self._logos_path = None
        self._working_directory = work_dir

        # Disk location
        self._original_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_original_path = wx.StaticText(self, -1, Strings.label_image + ': ')
        self._content_image_original_path = wx.StaticText(self, -1, Strings.label_none,
                                                          style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._original_disk_location_sub_sizer.Add(self._label_image_original_path,
                                                   flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._original_disk_location_sub_sizer.Add((7, -1))
        self._original_disk_location_sub_sizer.Add(self._content_image_original_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._original_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Original size
        self._image_original_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_size = wx.StaticText(self, -1, Strings.label_size + ': ')
        self._content_image_size = wx.StaticText(self, -1, Strings.label_none,
                                                 style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._image_original_size_sub_sizer.Add(self._label_image_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_original_size_sub_sizer.Add((1, -1))
        self._image_original_size_sub_sizer.Add(self._content_image_size, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_original_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image name sub sizer
        self._name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_name = wx.StaticText(self, -1, Strings.label_name + ': ')
        self._field_image_name = wx.TextCtrl(self, -1)
        self._field_image_name.Disable()
        self._name_sub_sizer.Add(self._label_image_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._name_sub_sizer.Add((5, -1))
        self._name_sub_sizer.Add(self._field_image_name, proportion=1)
        self._information_sizer.Add(self._name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_name_tip = Tools.get_warning_tip(self._field_image_name, Strings.label_image_name)
        self._field_image_name_tip.SetMessage('')

        # Image preview
        self._image_sizer = wx.BoxSizer(wx.VERTICAL)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(wx.Image(Fetch.get_resource_path('menu_image_missing.png'),
                                       wx.BITMAP_TYPE_PNG)))
        self._image_sizer.Add(self._bitmap, flag=wx.ALL, border=1)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._save_button = wx.Button(self, wx.ID_OK, Strings.button_save)
        self._browse_button = wx.Button(self, wx.ID_OPEN, Strings.button_browse)
        self._save_button.Disable()
        self._browse_button.SetDefault()
        grouping_sizer.Add(self._save_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._browse_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._horizontal_sizer.Add(self._image_sizer, flag=wx.TOP | wx.RIGHT, border=Numbers.widget_border_size)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._save_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._browse_button)

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name) or None, None if canceled
        """
        with wx.FileDialog(self, Strings.label_select_image, Strings.home_directory, wildcard=Strings.image_jpg_only,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                return dlg.GetPath(), dlg.GetFilename()
            return None, None

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OPEN:
            self._save_button.Disable()
            self._image_path, self._image_name = self._ask_for_image()
            if self._image_path and self._image_name:
                self._load_image()
            if self._menu_image:
                self._save_button.Enable()
        elif event.GetId() == wx.ID_OK:
            if self._save():
                event.Skip()
        elif event.GetId() == wx.ID_CANCEL:
            event.Skip()

    def _save(self) -> bool:
        """
        Save the images in correct locations.
        :return: True if save successful.
        """
        # Check filename
        new_name: str = self._field_image_name.GetValue()
        # Only letters, - and numbers are allowed in image names.
        wrong_name: bool = False
        for c in new_name:
            if not c.isalnum():
                wrong_name = True
            if c == '-':
                wrong_name = False
        if wrong_name:
            self._field_image_name.SetBackgroundColour(Numbers.RED_COLOR)
            self._field_image_name_tip.SetMessage(Strings.warning_name_incorrect)
            self._field_image_name_tip.EnableTip(True)
            self._field_image_name_tip.Show(True)
            return False
        else:
            self._field_image_name_tip.SetMessage(Strings.status_ok)
            self._field_image_name_tip.DoHideNow()
            self._field_image_name.SetBackgroundColour(Numbers.GREEN_COLOR)

        # Attempt to save the files
        self._logos_path: str = os.path.join(self._working_directory, Strings.folder_images, Strings.folder_logos)
        logo_file: str = os.path.join(self._logos_path, new_name)
        if os.path.exists(logo_file + Strings.extension_jpg):
            result = wx.MessageBox(Strings.warning_file_exists_overwrite + ': \n' + logo_file, Strings.status_error,
                                   wx.YES_NO | wx.ICON_ERROR)
            if result == wx.NO:
                return False
        self._menu_image.SaveFile(logo_file + Strings.extension_jpg, wx.BITMAP_TYPE_JPEG)
        # Exceptions from here are caught automatically
        return True

    def _load_image(self) -> None:
        """
        Load and display the image and prepare a logo from it.
        :return: None
        """
        # Create the base image for resizing.
        self._menu_image = wx.Image(self._image_path, wx.BITMAP_TYPE_ANY)
        # Check image is a square
        if self._menu_image.GetWidth() != self._menu_image.GetHeight():
            wx.MessageBox(Strings.warning_not_square, Strings.status_error, wx.OK | wx.ICON_ERROR)
            self._save_button.Disable()
            return

        self._content_image_original_path.SetLabelText(self._image_path)
        image_name: str = os.path.splitext(self._image_name)[0]
        self._field_image_name.SetValue(Strings.label_logo + image_name.capitalize())
        self._field_image_name.Enable()

        if self._menu_image.GetSize() != (Numbers.menu_logo_image_size, Numbers.menu_logo_image_size):
            self._menu_image.Rescale(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size, wx.IMAGE_QUALITY_HIGH)

        self._content_image_size.SetLabelText(str(self._menu_image.GetWidth()) + ' x ' +
                                              str(self._menu_image.GetHeight()) + ' px')
        # Show the image.
        self._bitmap.SetBitmap(wx.Bitmap(self._menu_image))
        self.Layout()
