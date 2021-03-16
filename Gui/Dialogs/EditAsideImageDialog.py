import math
import os

import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.AddImageDialog import AddImageDialog
from Tools.Document.AsideImage import AsideImage
from Tools.Tools import Tools


class EditAsideImageDialog(wx.Dialog):

    def __init__(self, parent, image: AsideImage, work_dir: str, section: str):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param image: AsideImage instance being edited by tis dialog.
        :param work_dir: The working directory of the editor.
        :param section: Menu section name.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_image,
                           size=(Numbers.edit_aside_image_dialog_width, Numbers.edit_aside_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._work_dir = work_dir
        self._section = section
        self._original_image: AsideImage = image
        self._image_copy: AsideImage = self._original_image.copy()
        self._image_copy.seo_test_self()

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Disk locations
        self._full_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_full_path = wx.StaticText(self, -1, Strings.label_image_path + ': ')
        self._content_image_full_path = wx.StaticText(self, -1, Strings.label_none,
                                                      style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._full_disk_location_sub_sizer.Add(self._label_image_full_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._full_disk_location_sub_sizer.Add(self._content_image_full_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._full_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        self._thumb_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_image_thumbnail_path + ': ')
        self._content_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_none,
                                                           style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._thumb_disk_location_sub_sizer.Add(self._label_image_thumbnail_path,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._thumb_disk_location_sub_sizer.Add(self._content_image_thumbnail_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._thumb_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Original size
        self._image_original_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_original_size = wx.StaticText(self, -1, Strings.label_original_size + ': ')
        self._content_image_original_size = wx.StaticText(self, -1, Strings.label_none)
        self._image_original_size_sub_sizer.Add(self._label_image_original_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_original_size_sub_sizer.Add((16, -1))
        self._image_original_size_sub_sizer.Add(self._content_image_original_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._image_original_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Thumbnail size
        self._image_thumbnail_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_thumbnail_size + ': ')
        self._content_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_none)
        self._image_thumbnail_size_sub_sizer.Add(self._label_image_thumbnail_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_thumbnail_size_sub_sizer.Add(self._content_image_thumbnail_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._image_thumbnail_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image caption sub sizer
        self._caption_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_caption = wx.StaticText(self, -1, Strings.label_article_image_caption + ': ')
        self._field_image_caption = wx.TextCtrl(self, -1)
        self._caption_sub_sizer.Add(self._label_image_caption, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._caption_sub_sizer.Add((8, -1))
        self._caption_sub_sizer.Add(self._field_image_caption, proportion=1)
        self._information_sizer.Add(self._caption_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_caption_tip = Tools.get_warning_tip(self._field_image_caption,
                                                              Strings.label_article_image_caption)

        # Image link title sub sizer
        self._title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self._field_image_link_title = wx.TextCtrl(self, -1)
        self._title_sub_sizer.Add(self._label_image_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._title_sub_sizer.Add((44, -1))
        self._title_sub_sizer.Add(self._field_image_link_title, proportion=1)
        self._information_sizer.Add(self._title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_link_title_tip = Tools.get_warning_tip(self._field_image_link_title,
                                                                 Strings.label_article_image_link_title)

        # Image alt sub sizer
        self._alt_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_alt = wx.StaticText(self, -1, Strings.label_alt_description + ': ')
        self._field_image_alt = wx.TextCtrl(self, -1)
        self._alt_sub_sizer.Add(self._label_image_alt, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._alt_sub_sizer.Add((5, -1))
        self._alt_sub_sizer.Add(self._field_image_alt, proportion=1)
        self._information_sizer.Add(self._alt_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_alt_tip = Tools.get_warning_tip(self._field_image_alt, Strings.label_article_image_alt)

        # Target blank checkbox all link always open in new page
        self._checkbox_target_blank = wx.CheckBox(self, -1, label=Strings.label_open_in_new_page)
        self._checkbox_target_blank.SetValue(True)
        self._checkbox_target_blank.Disable()
        self._information_sizer.Add(self._checkbox_target_blank, flag=wx.TOP, border=Numbers.widget_border_size)

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
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        self._browse_button = wx.Button(self, wx.ID_OPEN, Strings.button_browse)
        self._add_button = wx.Button(self, wx.ID_ADD, Strings.button_add)
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._browse_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._add_button)
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
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._browse_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._add_button)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OPEN:
            new_path, new_name = self._ask_for_image()
            img_dir: str = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_thumbnails)
            if not new_path:
                # No image was selected
                event.Skip()
                return
            if img_dir not in new_path:
                wx.MessageBox(Strings.warning_wrong_image_folder, Strings.status_error, wx.OK | wx.ICON_ERROR)
                return

            image = wx.Image(new_path, wx.BITMAP_TYPE_ANY)
            if not math.isclose(Numbers.photo_ratio, (image.GetWidth() / image.GetHeight()),
                                abs_tol=Numbers.photo_ratio_tolerance):
                # Test correct aspect ratio
                wx.MessageBox(Strings.warning_aside_impossible, Strings.status_error, wx.OK | wx.ICON_ERROR)
                return
            else:
                # Display the new image
                new_section: str = os.path.basename(os.path.dirname(new_path))
                html_thumbnail_filename: str = os.path.join(Strings.folder_images, Strings.folder_thumbnails,
                                                            new_section, new_name)
                self._image_copy = AsideImage(new_section, self._field_image_caption.GetValue(),
                                              self._field_image_link_title.GetValue(),
                                              self._field_image_alt.GetValue(),
                                              new_path.replace(Strings.folder_thumbnails, Strings.folder_originals),
                                              new_path, html_thumbnail_filename.replace(Strings.folder_thumbnails,
                                                                                        Strings.folder_originals),
                                              html_thumbnail_filename)
                # Initializes all internal variables.
                self._image_copy.seo_test_self()
                self._display_dialog_contents()
        elif event.GetId() == wx.ID_OK:
            # Save new information into image and rerun seo test.
            self._image_copy.set_caption(self._field_image_caption.GetValue())
            self._image_copy.set_link_title(self._field_image_link_title.GetValue())
            self._image_copy.set_alt(self._field_image_alt.GetValue())

            if self._image_copy.seo_test_self():
                # If the seo test is good, transfer all information into the original image.
                self._original_image.set_section(self._image_copy.get_section())
                self._original_image.set_caption(self._image_copy.get_caption()[0])
                self._original_image.set_link_title(self._image_copy.get_link_title()[0])
                self._original_image.set_alt(self._image_copy.get_image_alt()[0])
                self._original_image.set_original_image_path(self._image_copy.get_original_image_path())
                self._original_image.set_thumbnail_image_path(self._image_copy.get_thumbnail_image_path())
                self._original_image.set_full_filename(self._image_copy.get_full_filename())
                self._original_image.set_thumbnail_filename(self._image_copy.get_thumbnail_filename())
                self._original_image.seo_test_self()
                event.Skip()
                return
            else:
                self._display_dialog_contents()
        elif event.GetId() == wx.ID_ADD:
            dlg = AddImageDialog(self, self._work_dir, self._section)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            # Leave the old image as it is and do not do anything.
            event.Skip()

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name) or None, None if canceled
        """
        path = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_thumbnails, self._section.lower())
        if not path:
            path = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_thumbnails,
                                self._image_copy.get_section().lower())
        with wx.FileDialog(self, Strings.label_select_image, path, wildcard=Strings.image_extensions,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                return dlg.GetPath(), dlg.GetFilename()
            return None, None

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        :return: None
        """
        # Set image data
        field_to_value = {self._field_image_caption: (self._image_copy.get_caption(), self._field_image_caption_tip),
                          self._field_image_link_title: (self._image_copy.get_link_title(),
                                                         self._field_image_link_title_tip),
                          self._field_image_alt: (self._image_copy.get_image_alt(), self._field_image_alt_tip)}
        for field, value in field_to_value.items():
            tip = value[1]
            if value[0][1]:
                tip.SetMessage(Strings.seo_check + '\n' + value[0][1])
                tip.EnableTip(True)
                field.SetBackgroundColour(Numbers.RED_COLOR)
            else:
                tip.SetMessage(Strings.seo_check + '\n' + Strings.status_ok)
                tip.DoHideNow()
                field.SetBackgroundColour(Numbers.GREEN_COLOR)
            field.SetValue(value[0][0])

        # Set images
        self._bitmap.SetBitmap(wx.Bitmap(self._image_copy.get_image(normal=True)))

        # Set thumbnail size
        thumbnail_size = self._image_copy.get_thumbnail_size()
        if thumbnail_size:
            self._content_image_thumbnail_size.SetLabelText(
                str(thumbnail_size[0]) + ' x ' + str(thumbnail_size[1]) + ' px')
        else:
            self._content_image_thumbnail_size.SetLabelText(Strings.status_error)

        # Set original size
        original_size = self._image_copy.get_original_size()
        if original_size:
            self._content_image_original_size.SetLabelText(
                str(original_size[0]) + ' x ' + str(original_size[1]) + ' px')
        else:
            self._content_image_original_size.SetLabelText(Strings.status_error)

        # Set disk paths
        full_path = self._image_copy.get_original_image_path()
        self.SetTitle(Strings.label_dialog_edit_image + ': ' + self._image_copy.get_full_filename())
        if full_path:
            self._content_image_full_path.SetLabelText(full_path)
        else:
            self._content_image_full_path.SetLabelText(self._image_copy.get_full_filename())

        thumb_path = self._image_copy.get_thumbnail_image_path()
        if thumb_path:
            self._content_image_thumbnail_path.SetLabelText(thumb_path)
        else:
            self._content_image_thumbnail_path.SetLabelText(self._image_copy.get_thumbnail_filename())
