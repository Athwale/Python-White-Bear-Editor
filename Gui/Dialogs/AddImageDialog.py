import os

import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Tools import Tools
from fractions import Fraction


class AddImageDialog(wx.Dialog):

    def __init__(self, parent, doc: WhitebearDocumentArticle):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param doc: The currently opened document.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_add_image,
                           size=(Numbers.add_image_dialog_width, Numbers.edit_text_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)
        self._doc = doc
        self._image_path = None
        self._image_name = None
        self._menu_section = None
        self._full_image = None
        self._thumbnail = None
        self._originals_path = None
        self._thumbnails_path = None
        self._working_directory = self._doc.get_working_directory()

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

        # Target section
        self._target_section_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_target_section = wx.StaticText(self, -1, Strings.label_target_section + ': ')
        self._content_target_section = wx.StaticText(self, -1, Strings.label_none,
                                                     style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._target_section_sub_sizer.Add(self._label_target_section, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._target_section_sub_sizer.Add(self._content_target_section, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._target_section_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Original size
        self._image_original_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_original_size = wx.StaticText(self, -1, Strings.label_full_size + ': ')
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
        self._label_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_thumbnail_size + ': ')
        self._content_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_none,
                                                           style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._image_thumbnail_size_sub_sizer.Add(self._label_image_thumbnail_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_thumbnail_size_sub_sizer.Add(self._content_image_thumbnail_size, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_thumbnail_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image name sub sizer
        self._name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_name = wx.StaticText(self, -1, Strings.label_name + ': ')
        self._field_image_name = wx.TextCtrl(self, -1)
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

        # Image name sub sizer
        self._warning_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_warning = wx.StaticText(self, -1, Strings.warning_aside_impossible)
        self._warning_sub_sizer.Add(self._label_warning, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._warning_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._label_warning.Hide()

        # Image preview
        self._image_sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))
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

        self._menu_section = self._doc.get_menu_section().get_page_name()[0]
        self._content_target_section.SetLabelText(self._menu_section)

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name)
        """
        with wx.FileDialog(self, Strings.label_select_image, Strings.home_directory, wildcard=Strings.image_extensions,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath(), dlg.GetFilename()

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OPEN:
            self._save_button.Disable()
            self._image_path, self._image_name = self._ask_for_image()
            self._load_image()
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
        new_name = self._field_image_name.GetValue()
        if '/' in new_name or '\\' in new_name or str.startswith(new_name, '.') or not new_name:
            self._field_image_name.SetBackgroundColour(Numbers.RED_COLOR)
            self._field_image_name_tip.SetMessage(Strings.warning_name_incorrect)
            self._field_image_name_tip.EnableTip(True)
            return False
        else:
            self._field_image_name_tip.SetMessage(Strings.status_ok)
            self._field_image_name_tip.DoHideNow()
            self._field_image_name.SetBackgroundColour(Numbers.GREEN_COLOR)
        # Attempt to save the files
        # TODO do not save double extension
        # TODO label saying why image can not be aside
        thumbnail_file: str = os.path.join(self._thumbnails_path, new_name)
        full_file: str = os.path.join(self._originals_path, new_name)
        if os.path.exists(thumbnail_file):
            wx.MessageBox(Strings.warning_file_exists + ': ' + thumbnail_file, Strings.status_error,
                          wx.OK | wx.ICON_ERROR)
            return False
        if os.path.exists(full_file):
            wx.MessageBox(Strings.warning_file_exists + ': ' + full_file, Strings.status_error,
                          wx.OK | wx.ICON_ERROR)
            return False

        print(thumbnail_file)
        print(full_file)

        return True

    def _handle_radio_buttons(self, event: wx.CommandEvent) -> None:
        """
        Simply remake the thumbnail based on selected option.
        :param event: Not used.
        :return: None
        """
        self._load_thumbnail()

    def _load_image(self) -> None:
        """
        Copy the selected image into the right place and make a thumbnail.
        :return: None
        """
        self._content_image_original_path.SetLabelText(self._image_path)
        self._field_image_name.SetValue(self._image_name)

        # Create the base image for resizing.
        self._full_image = wx.Image(self._image_path, wx.BITMAP_TYPE_ANY)
        # Check aspect ratio of the image and disable the aside image option if 300x225 resize is impossible.
        if Numbers.photo_ratio != Fraction(self._full_image.GetWidth(), self._full_image.GetHeight()):
            self._radio_aside.Disable()
            self._radio_text.SetValue(True)
            self._label_warning.Show(True)
        else:
            self._radio_aside.Enable()
            self._label_warning.Show(False)
        if self._full_image.GetWidth() > Numbers.original_image_max_width:
            # Resize the original image to 50% if too bit.
            self._full_image.Rescale(self._full_image.GetWidth() / 2, self._full_image.GetHeight() / 2,
                                     wx.IMAGE_QUALITY_HIGH)
        # Display the originals image width
        self._content_image_original_size.SetLabelText(
            str(self._full_image.GetWidth()) + ' x ' + str(self._full_image.GetHeight()) + ' px')
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

        self._content_image_thumbnail_size.SetLabelText(str(self._thumbnail.GetWidth()) + ' x ' +
                                                        str(self._thumbnail.GetHeight()) + ' px')
        self._bitmap.SetBitmap(wx.Bitmap(self._thumbnail))
        self.SetSize(Numbers.add_image_dialog_width, self._thumbnail.GetHeight() + 120)
        self._originals_path: str = os.path.join(self._working_directory, Strings.folder_images,
                                                 Strings.folder_originals, self._menu_section.lower())
        self._thumbnails_path: str = os.path.join(self._working_directory, Strings.folder_images,
                                                  Strings.folder_thumbnails, self._menu_section.lower())
        self.Layout()
