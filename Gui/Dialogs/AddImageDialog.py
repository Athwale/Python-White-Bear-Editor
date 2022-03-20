import math
import os

import wx

from Constants.Constants import Strings, Numbers
from Resources.Fetch import Fetch
from Tools.ConfigManager import ConfigManager
from Tools.Tools import Tools


class AddImageDialog(wx.Dialog):

    def __init__(self, parent, work_dir: str):
        """
        This dialog helps with adding a new image to the website folder structure.
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param work_dir: The working directory of the editor.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_add_image,
                           size=(Numbers.add_image_dialog_width, Numbers.add_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_path = None
        self._image_name = None
        self._full_image = None
        self._thumbnail = None
        self._originals_path = None
        self._thumbnails_path = None
        self._thumbnail_path = None
        self._working_directory = work_dir
        self._config_manager = ConfigManager.get_instance()

        # Disk location
        self._original_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_original_path = wx.StaticText(self, -1, f'{Strings.label_image}: ')
        self._content_image_original_path = wx.StaticText(self, -1, Strings.label_none,
                                                          style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._original_disk_location_sub_sizer.Add(self._label_image_original_path,
                                                   flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._original_disk_location_sub_sizer.Add(self._content_image_original_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._original_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Original size
        self._image_original_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_original_size = wx.StaticText(self, -1, f'{Strings.label_full_size}: ')
        self._content_image_original_size = wx.StaticText(self, -1, Strings.label_none,
                                                          style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._image_original_size_sub_sizer.Add(self._label_image_original_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_original_size_sub_sizer.Add((1, -1))
        self._image_original_size_sub_sizer.Add(self._content_image_original_size, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_original_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Thumbnail size
        self._image_thumbnail_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_thumbnail_size = wx.StaticText(self, -1, f'{Strings.label_thumbnail_size}: ')
        self._content_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_none,
                                                           style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._image_thumbnail_size_sub_sizer.Add(self._label_image_thumbnail_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_thumbnail_size_sub_sizer.Add(self._content_image_thumbnail_size, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_thumbnail_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image name sub sizer
        self._name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_name = wx.StaticText(self, -1, f'{Strings.label_name}: ')
        self._field_image_name = wx.TextCtrl(self, -1)
        self._field_image_name.Disable()
        self._name_sub_sizer.Add(self._label_image_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._name_sub_sizer.Add((5, -1))
        self._name_sub_sizer.Add(self._field_image_name, proportion=1)
        self._information_sizer.Add(self._name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_name_tip = Tools.get_warning_tip(self._field_image_name, Strings.label_image_name)
        self._field_image_name_tip.SetMessage('')

        # Image type sub sizer
        self._type_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._radio_text = wx.RadioButton(self, -1, Strings.label_text_image)
        self._radio_aside = wx.RadioButton(self, -1, Strings.label_aside_image)
        # Disable by default, the button will be enabled only if 300x225 resize is possible after an image is selected.
        self._radio_aside.Disable()
        self._type_sub_sizer.Add(self._radio_text, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._type_sub_sizer.Add(self._radio_aside, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._type_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)

        # Warning sub sizer
        self._warning_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_warning = wx.StaticText(self, -1, Strings.warning_aside_impossible)
        self._warning_sub_sizer.Add(self._label_warning, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._warning_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._label_warning.Hide()

        # Image preview
        self._image_sizer = wx.BoxSizer(wx.VERTICAL)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(wx.Image(Fetch.get_resource_path('main_image_missing.png'),
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
        self.Bind(wx.EVT_RADIOBUTTON, self._handle_radio_buttons)
        self.Bind(wx.EVT_TEXT, self._switch_default_button, self._field_image_name)

    # noinspection PyUnusedLocal
    def _switch_default_button(self, event: wx.CommandEvent) -> None:
        """
        Switch the default button to save once the user changes the image name.
        :param event: Not used
        :return: None
        """
        self._save_button.SetDefault()

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name) or None, None if canceled
        """
        last_dir = self._config_manager.get_last_img_dir()
        if not os.path.exists(last_dir):
            last_dir = Strings.home_directory
        with wx.FileDialog(self, Strings.label_select_image, last_dir, wildcard=Strings.image_extensions,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                self._config_manager.store_last_img_dir(os.path.dirname(dlg.GetPath()))
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
                self._field_image_name.SetFocus()
            if self._full_image:
                self._save_button.Enable()
        elif event.GetId() == wx.ID_OK and self._save_button.IsEnabled():
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
        self._originals_path: str = os.path.join(self._working_directory, Strings.folder_images,
                                                 Strings.folder_originals)
        self._thumbnails_path: str = os.path.join(self._working_directory, Strings.folder_images,
                                                  Strings.folder_thumbnails)
        self._thumbnail_path: str = os.path.join(self._thumbnails_path, new_name)
        full_file: str = os.path.join(self._originals_path, new_name)
        # Determine the file type, we can only open jpg and png files in the browse dialog.
        _, file_extension = os.path.splitext(os.path.join(self._image_path, self._image_name))
        if file_extension.lower() == Strings.extension_jpg:
            img_type = wx.BITMAP_TYPE_JPEG
        else:
            img_type = wx.BITMAP_TYPE_PNG

        self._thumbnail_path = self._thumbnail_path + file_extension.lower()
        full_file = full_file + file_extension.lower()
        if os.path.exists(self._thumbnail_path):
            result = wx.MessageBox(f'{Strings.warning_file_exists_overwrite}: \n{self._thumbnail_path}',
                                   Strings.status_error, wx.YES_NO | wx.ICON_ERROR)
            if result == wx.NO:
                return False
        self._thumbnail.SaveFile(self._thumbnail_path, img_type)

        if os.path.exists(full_file):
            result = wx.MessageBox(f'{Strings.warning_file_exists_overwrite}: \n{full_file}',
                                   Strings.status_error, wx.YES_NO | wx.ICON_ERROR)
            if result == wx.NO:
                return False
        self._full_image.SaveFile(full_file, img_type)

        # Exceptions from here are caught automatically
        return True

    # noinspection PyUnusedLocal
    def _handle_radio_buttons(self, event: wx.CommandEvent) -> None:
        """
        Simply remake the thumbnail based on selected option.
        :param event: Not used.
        :return: None
        """
        self._load_thumbnail()

    def _load_image(self) -> None:
        """
        Load and display the image, resize it if needed and make a thumbnail.
        :return: None
        """
        self._content_image_original_path.SetLabelText(self._image_path)
        image_name: str = os.path.splitext(self._image_name)[0]
        self._field_image_name.SetValue(image_name)
        self._field_image_name.Enable()

        # Create the base image for resizing.
        self._full_image = wx.Image(self._image_path, wx.BITMAP_TYPE_ANY)
        # Check aspect ratio of the image and disable the aside image option if 300x225 resize is impossible.
        if not math.isclose(Numbers.photo_ratio, (self._full_image.GetWidth() / self._full_image.GetHeight()),
                            abs_tol=Numbers.photo_ratio_tolerance):
            self._radio_aside.Disable()
            self._radio_text.SetValue(True)
            self._label_warning.Show(True)
        else:
            self._radio_aside.Enable()
            self._radio_aside.SetValue(True)
            self._label_warning.Show(False)
        if self._full_image.GetWidth() > Numbers.original_image_max_width:
            # Resize the original image to 50% if too big.
            self._full_image.Rescale(self._full_image.GetWidth() / 2, self._full_image.GetHeight() / 2,
                                     wx.IMAGE_QUALITY_HIGH)
        # Display the originals image width
        self._content_image_original_size.SetLabelText(f'{self._full_image.GetWidth()} x {self._full_image.GetHeight()}'
                                                       f' px')
        # Create the thumbnail and show it.
        self._load_thumbnail()

    def _load_thumbnail(self) -> None:
        """
        Create and display the correct thumbnail according to selected image type.
        :return: None
        """
        self._thumbnail: wx.Image = self._full_image.Copy()
        if self._radio_text.GetValue():
            # Text image thumbnail must be max 534px wide create a thumbnail and resize it if needed.
            if self._thumbnail.GetWidth() > Numbers.text_image_max_size:
                new_height = self._thumbnail.GetHeight() * (Numbers.text_image_max_size / self._thumbnail.GetWidth())
                self._thumbnail.Rescale(Numbers.text_image_max_size, new_height, wx.IMAGE_QUALITY_HIGH)
        else:
            # The other option is aside or main image which must be exactly 300x225px.
            self._thumbnail.Rescale(Numbers.main_image_width, Numbers.main_image_height, wx.IMAGE_QUALITY_HIGH)

        self._content_image_thumbnail_size.SetLabelText(f'{self._thumbnail.GetWidth()} x {self._thumbnail.GetHeight()}'
                                                        f' px')
        self._bitmap.SetBitmap(wx.Bitmap(self._thumbnail))
        height = self._thumbnail.GetHeight()
        if height < Numbers.main_image_height:
            height = Numbers.main_image_height + 20
        elif height == Numbers.main_image_height:
            height = Numbers.main_image_height + 120
        self.SetSize(Numbers.add_image_dialog_width, height)
        self.Layout()

    def get_thumbnail_location(self) -> (str, str):
        """
        Return thumbnail image disk path and filename. Use this only after the dialog was confirmed.
        :return: Image disk path and filename.
        """
        return self._thumbnail_path, os.path.basename(self._thumbnail_path)
