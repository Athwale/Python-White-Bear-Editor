import os

import wx

from Constants.Constants import Strings, Numbers
from Exceptions.LogoException import LogoException
from Resources.Fetch import Fetch
from Tools.ConfigManager import ConfigManager
from Tools.Tools import Tools


class AddLogoDialog(wx.Dialog):

    def __init__(self, parent, work_dir: str, article_name: str):
        """
        This dialog helps with adding a new menu logo into the folder structure of the website.
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param work_dir: The working directory of the editor.
        :param article_name: Name used to create the logo filename. If empty, image file name is used.
        """
        # TODO refuse too large images 500x500?
        # TODO try big, small, completely white, tall, short images
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
        self._file_path = None
        self._article_name = article_name
        self._config_manager = ConfigManager.get_instance()

        # Detection preview
        self._preview_bitmap = wx.StaticBitmap(self, -1,
                                               wx.Bitmap(wx.Image(Fetch.get_resource_path('preview_missing.png'),
                                                                  wx.BITMAP_TYPE_PNG)))
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
        self._label_image_size = wx.StaticText(self, -1, f'{Strings.label_size}: ')
        self._content_image_size = wx.StaticText(self, -1, Strings.label_none,
                                                 style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._image_original_size_sub_sizer.Add(self._label_image_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_original_size_sub_sizer.Add((14, -1))
        self._image_original_size_sub_sizer.Add(self._content_image_size, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_original_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Selection size
        self._image_selection_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_selection_image_size = wx.StaticText(self, -1, Strings.label_selection_size)
        self._content_image_selection_size = wx.StaticText(self, -1, Strings.label_none,
                                                           style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._image_selection_size_sub_sizer.Add(self._label_selection_image_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_selection_size_sub_sizer.Add((13, -1))
        self._image_selection_size_sub_sizer.Add(self._content_image_selection_size, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_selection_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
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

        # Controls sub sizers
        self._border_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_border = wx.StaticText(self, -1, Strings.label_border)
        self._border_spinner = wx.SpinCtrl(self, -1, '', min=0, max=Numbers.border_max, initial=Numbers.border_default)
        self._border_sub_sizer.Add(self._label_border, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._border_sub_sizer.Add((3, -1))
        self._border_sub_sizer.Add(self._border_spinner, proportion=1)
        self._information_sizer.Add(self._border_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)

        self._threshold_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_threshold = wx.StaticText(self, -1, Strings.label_threshold)
        self._threshold_spinner = wx.SpinCtrl(self, -1, '', min=0, max=Numbers.threshold_max,
                                              initial=Numbers.threshold_default)
        self._threshold_sub_sizer.Add(self._label_threshold, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._threshold_sub_sizer.Add((15, -1))
        self._threshold_sub_sizer.Add(self._threshold_spinner, proportion=1)
        self._information_sizer.Add(self._threshold_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image preview
        self._image_sizer = wx.BoxSizer(wx.VERTICAL)
        self._logo_bitmap = wx.StaticBitmap(self, -1,
                                            wx.Bitmap(wx.Image(Fetch.get_resource_path('menu_image_missing.png'),
                                                               wx.BITMAP_TYPE_PNG)))
        self._logo_size_label = wx.StaticText(self, -1, f'{Numbers.menu_logo_image_size} x '
                                                        f'{Numbers.menu_logo_image_size} px')
        self._image_sizer.Add(self._logo_bitmap, flag=wx.ALL, border=1)
        self._image_sizer.Add(self._logo_size_label, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=1)

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
        self._horizontal_sizer.Add(self._preview_bitmap, 1, flag=wx.TOP | wx.LEFT, border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._horizontal_sizer.Add(self._image_sizer, flag=wx.TOP | wx.RIGHT | wx.EXPAND,
                                   border=Numbers.widget_border_size)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._save_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._browse_button)
        self.Bind(wx.EVT_TEXT, self._switch_default_button, self._field_image_name)
        self.Bind(wx.EVT_SPINCTRL, self._spinner_handler, self._border_spinner)
        self.Bind(wx.EVT_SPINCTRL, self._spinner_handler, self._threshold_spinner)

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
        with wx.FileDialog(self, Strings.label_select_image, last_dir, wildcard=Strings.image_jpg_only,
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
            if self._menu_image:
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
        self._logos_path: str = os.path.join(self._working_directory, Strings.folder_images, Strings.folder_logos)
        logo_file: str = os.path.join(self._logos_path, new_name)
        if os.path.exists(logo_file + Strings.extension_jpg):
            result = wx.MessageBox(f'{Strings.warning_file_exists_overwrite}: \n{logo_file, Strings.status_error}',
                                   Strings.status_error, wx.YES_NO | wx.ICON_ERROR)
            if result == wx.NO:
                return False
        self._menu_image.SaveFile(logo_file + Strings.extension_jpg, wx.BITMAP_TYPE_JPEG)
        self._file_path = logo_file + Strings.extension_jpg
        # Exceptions from here are caught automatically
        return True

    # noinspection PyUnusedLocal
    def _spinner_handler(self, event: wx.CommandEvent) -> None:
        """
        Update images when the user changes settings.
        :param event: Not used
        :return: None
        """
        # TODO interactive redraw on spinner changes.
        self._save_button.Disable()
        if self._image_path and self._image_name:
            self._load_image()
            self._field_image_name.SetFocus()
        if self._menu_image:
            self._save_button.Enable()

    def _load_image(self) -> None:
        """
        Load and display the image and prepare a logo from it.
        :return: None
        """
        # Create the base image for resizing.
        try:
            preview_image, self._menu_image = self.process_image(self._image_path,
                                                                 self._threshold_spinner.GetValue(),
                                                                 self._border_spinner.GetValue())
        except LogoException as _:
            self._logo_bitmap.SetBitmap(wx.Bitmap(wx.Image(Fetch.get_resource_path('menu_image_missing.png'),
                                                  wx.BITMAP_TYPE_PNG)))
            self._preview_bitmap.SetBitmap(wx.Bitmap(wx.Image(Fetch.get_resource_path('preview_missing.png'),
                                                     wx.BITMAP_TYPE_PNG)))
            # TODO disable save
            return

        self._content_image_original_path.SetLabelText(self._image_path)
        image_name: str = os.path.splitext(self._image_name)[0]
        if self._article_name:
            self._field_image_name.SetValue(f'{Strings.label_logo}{self._article_name.capitalize()}')
        else:
            self._field_image_name.SetValue(f'{Strings.label_logo}{image_name.capitalize()}')
        self._field_image_name.Enable()

        self._content_image_size.SetLabelText(f'{self._menu_image.GetWidth()} x {self._menu_image.GetHeight()} px')
        # Show the image.
        self._logo_bitmap.SetBitmap(wx.Bitmap(self._menu_image))
        if preview_image.GetWidth() > Numbers.main_image_width or preview_image.GetHeight() > Numbers.main_image_height:
            width_scale = Numbers.main_image_width / preview_image.GetWidth()
            height_scale = Numbers.main_image_height / preview_image.GetHeight()
            bounded_scale = min(width_scale, height_scale)
            preview_image.Rescale(width=int(preview_image.GetWidth() * bounded_scale),
                                  height=int(preview_image.GetHeight() * bounded_scale),
                                  quality=wx.IMAGE_QUALITY_HIGH)
        # Place the small logo into the middle of the final correctly sized image with white background.
        x_center = int((Numbers.main_image_width - preview_image.GetWidth()) / 2)
        y_center = int((Numbers.main_image_height - preview_image.GetHeight()) / 2)
        preview_image.Resize((Numbers.main_image_width, Numbers.main_image_height), (x_center, y_center), 255, 255, 255)
        self._preview_bitmap.SetBitmap(wx.Bitmap(preview_image))
        self.Layout()

    @staticmethod
    def process_image(img_path: str, limit: int, border: int) -> (wx.Image, wx.Image):
        """
        Search for the image based on red color threshold from the set direction. Then cut the image out and prepare
        the menu logo image of correct size.
        :param img_path: Path to an image.
        :param limit: The red color threshold where we consider the image to be useful.
        :param border: How many white pixels to put around the image.
        :return: 2 images - preview and finished logo.
        :raises LogoException: If no image is found in the input image or the found image is too small.
        """
        image = wx.Image(img_path)
        if image.GetWidth() == Numbers.menu_logo_image_size and image.GetHeight() == Numbers.menu_logo_image_size:
            # We presume the image is supposed to be used as a logo as is.
            return wx.Image(Fetch.get_resource_path('preview_noconvert.png'), wx.BITMAP_TYPE_PNG), image
        image: wx.Image = image.ConvertToGreyscale()
        # Bounding box will be drawn only into the preview.
        preview = image.Copy()
        # Top will be set only once on the first matching pixel.
        top = None
        # Bottom is the last matching pixel.
        bottom = None
        # Left will be gradually adjusted to the leftmost smallest x coordinate.
        left = (image.GetWidth(), 0)
        # Right will be gradually adjusted to the rightmost highest x coordinate.
        right = (0, 0)
        for y in range(0, image.GetHeight() - 1):
            for x in range(0, image.GetWidth() - 1):
                color = image.GetRed(x, y)
                # A shade of gray that we consider gray enough to count as the image we want.
                if color < limit:
                    if not top:
                        top = (x, y)
                    if x < left[0]:
                        left = (x, y)
                    if x > right[0]:
                        right = (x, y)
                    else:
                        bottom = (x, y)
                else:
                    # Repaint all lighter colors with white
                    preview.SetRGB(x, y, 255, 255, 255)
                    image.SetRGB(x, y, 255, 255, 255)

        if top is None or bottom is None:
            raise LogoException(Strings.warning_no_image)

        top_left = (left[0], top[1])
        bottom_right = (right[0], bottom[1])

        # Draw a bounding box around the selected area.
        for y in range(0, preview.GetHeight() - 1):
            for x in range(0, preview.GetWidth() - 1):
                if x == top_left[0] or x == bottom_right[0]\
                        or y == top_left[1] or y == bottom_right[1]:
                    preview.SetRGB(x, y, 255, 0, 0)
        # Get only the selected part of the image.
        crop: wx.Image = image.GetSubImage(wx.Rect(wx.Point(top_left), wx.Point(bottom_right)))
        if crop.GetWidth() < Numbers.menu_logo_image_size or crop.GetHeight() < Numbers.menu_logo_image_size:
            raise LogoException(Strings.warning_image_small)
        # Rescale it to fit into the logo size - border and respect aspect ratio
        width_scale = Numbers.menu_logo_image_size / crop.GetWidth()
        height_scale = Numbers.menu_logo_image_size / crop.GetHeight()
        bounded_scale = min(width_scale, height_scale)
        width = int(crop.GetWidth() * bounded_scale) - border
        height = int(crop.GetHeight() * bounded_scale) - border
        width = width if width > 0 else 1
        height = height if height > 0 else 1
        crop.Rescale(width, height, quality=wx.IMAGE_QUALITY_HIGH)
        logo_size = (Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        # Place the small logo into the middle of the final correctly sized image with white background.
        x_center = int((Numbers.menu_logo_image_size - crop.GetWidth()) / 2)
        y_center = int((Numbers.menu_logo_image_size - crop.GetHeight()) / 2)
        crop.Resize(logo_size, (x_center, y_center), 255, 255, 255)
        return preview, crop

    def get_logo_location(self) -> (str, str):
        """
        Return logo image disk path and filename. Use this only after the dialog was confirmed.
        :return: Image disk path and filename.
        """
        return self._file_path, os.path.basename(self._file_path)
