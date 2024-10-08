import math
import os

import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.AddImageDialog import AddImageDialog
from Gui.Dialogs.SpellCheckedDialog import SpellCheckedDialog
from Tools.Document.AsideImage import AsideImage
from Tools.Tools import Tools


class EditAsideImageDialog(SpellCheckedDialog):

    def __init__(self, parent, image: AsideImage, work_dir: str):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param image: AsideImage instance being edited by this dialog.
        :param work_dir: The working directory of the editor.
        """
        super().__init__(parent, title=Strings.label_dialog_edit_image,
                         size=(Numbers.edit_aside_image_dialog_width, Numbers.edit_aside_image_dialog_height),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._work_dir = work_dir
        self._original_image: AsideImage = image
        self._image_copy: AsideImage = self._original_image.copy()
        self._image_copy.test_self()

        self._alt_lock = False
        self._title_lock = False

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Disk locations
        self._full_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_full_path = wx.StaticText(self, -1, f'{Strings.label_image_path}: ')
        self._content_image_full_path = wx.StaticText(self, -1, Strings.label_none,
                                                      style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._full_disk_location_sub_sizer.Add(self._label_image_full_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._full_disk_location_sub_sizer.Add(self._content_image_full_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._full_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        self._thumb_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_thumbnail_path = wx.StaticText(self, -1, f'{Strings.label_image_thumbnail_path}: ')
        self._content_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_none,
                                                           style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._thumb_disk_location_sub_sizer.Add(self._label_image_thumbnail_path,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._thumb_disk_location_sub_sizer.Add(self._content_image_thumbnail_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._thumb_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Original size
        self._image_original_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_original_size = wx.StaticText(self, -1, f'{Strings.label_original_size}: ')
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
        self._label_image_thumbnail_size = wx.StaticText(self, -1, f'{Strings.label_thumbnail_size}: ')
        self._content_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_none)
        self._image_thumbnail_size_sub_sizer.Add(self._label_image_thumbnail_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_thumbnail_size_sub_sizer.Add(self._content_image_thumbnail_size,
                                                 flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._image_thumbnail_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image caption sub sizer
        self._caption_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_caption = wx.StaticText(self, -1, f'{Strings.label_article_image_caption}: ')
        self._field_image_caption = wx.TextCtrl(self, -1)
        self._caption_sub_sizer.Add(self._label_image_caption, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._caption_sub_sizer.Add(self._field_image_caption, proportion=1)
        self._information_sizer.Add(self._caption_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_caption_tip = Tools.get_warning_tip(self._field_image_caption,
                                                              Strings.label_article_image_caption)

        # Image link title sub sizer
        self._title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_title = wx.StaticText(self, -1, f'{Strings.label_link_title}: ')
        self._field_image_link_title = wx.TextCtrl(self, Numbers.ID_IMAGE_LINK)
        self._title_sub_sizer.Add(self._label_image_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._title_sub_sizer.Add(self._field_image_link_title, proportion=1)
        self._information_sizer.Add(self._title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_link_title_tip = Tools.get_warning_tip(self._field_image_link_title,
                                                                 Strings.label_article_image_link_title)

        # Image alt sub sizer
        self._alt_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_alt = wx.StaticText(self, -1, f'{Strings.label_alt_description}: ')
        self._field_image_alt = wx.TextCtrl(self, Numbers.ID_IMAGE_ALT)
        self._alt_sub_sizer.Add(self._label_image_alt, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._alt_sub_sizer.Add(self._field_image_alt, proportion=1)
        self._information_sizer.Add(self._alt_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_image_alt_tip = Tools.get_warning_tip(self._field_image_alt, Strings.label_article_image_alt)

        self._label_image_caption.SetMinSize(self._label_image_alt.GetSize())
        self._label_image_title.SetMinSize(self._label_image_alt.GetSize())

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
        self._delete_button = wx.Button(self, wx.ID_DELETE, Strings.button_delete_images)
        self._delete_button.SetForegroundColour(wx.RED)
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._browse_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._add_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._delete_button)
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

        # Disable auto copy of fields if the fields contain different data.
        if self._field_image_caption.GetValue() != self._field_image_link_title.GetValue():
            self._title_lock = True
        if self._field_image_caption.GetValue() != self._field_image_alt.GetValue():
            self._alt_lock = True

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._browse_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._add_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._delete_button)

        self.Bind(wx.EVT_TEXT, self._handle_edit, self._field_image_caption)
        self.Bind(wx.EVT_TEXT, self._lock_fields, self._field_image_alt)
        self.Bind(wx.EVT_TEXT, self._lock_fields, self._field_image_link_title)

    # noinspection PyUnusedLocal
    def _handle_edit(self, event: wx.CommandEvent) -> None:
        """
        Copy the text from the first field to the other fields as long as the contents of them are the same.
        Speeds up filling the metadata for new images.
        :param event: Not used.
        :return: None
        """
        text = self._field_image_caption.GetValue()
        if not self._alt_lock:
            self._field_image_alt.SetValue(text)
        if not self._title_lock:
            self._field_image_link_title.SetValue(text)

    def _lock_fields(self, event: wx.CommandEvent) -> None:
        """
        Prevents automatic copying of text to other fields when they are edited manually.
        :param event:
        :return: None
        """
        if event.GetId() == Numbers.ID_IMAGE_LINK:
            if self._field_image_caption.GetValue() != self._field_image_link_title.GetValue():
                self._title_lock = True
        elif event.GetId() == Numbers.ID_IMAGE_ALT:
            if self._field_image_caption.GetValue() != self._field_image_alt.GetValue():
                self._alt_lock = True

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OPEN:
            new_path, new_name = self._ask_for_image()
            if not new_path:
                # No image was selected
                event.Skip()
                return
            else:
                self._change_image(new_path, new_name)
                self._ok_button.SetDefault()
        elif event.GetId() == wx.ID_OK and self._ok_button.IsEnabled():
            # Spellcheck dialog only appears if a mistake is found.
            self._run_spellcheck(((self._field_image_caption, Strings.label_article_image_caption),
                                  (self._field_image_link_title, Strings.label_link_title),
                                  (self._field_image_alt, Strings.label_alt_description)))
            # Save new information into image and rerun seo test.
            self._image_copy.set_caption(self._field_image_caption.GetValue())
            self._image_copy.set_link_title(self._field_image_link_title.GetValue())
            self._image_copy.set_alt(self._field_image_alt.GetValue())

            if self._image_copy.test_self():
                # If the seo test is good, transfer all information into the original image.
                self._original_image.set_caption(self._image_copy.get_caption()[0])
                self._original_image.set_link_title(self._image_copy.get_link_title()[0])
                self._original_image.set_alt(self._image_copy.get_image_alt()[0])
                self._original_image.set_original_image_path(self._image_copy.get_original_image_path())
                self._original_image.set_thumbnail_image_path(self._image_copy.get_thumbnail_image_path())
                self._original_image.set_full_filename(self._image_copy.get_full_filename())
                self._original_image.set_thumbnail_filename(self._image_copy.get_thumbnail_filename())
                self._original_image.test_self()
                event.Skip()
                return
            else:
                self._display_dialog_contents()
        elif event.GetId() == wx.ID_ADD:
            dlg = AddImageDialog(self, self._work_dir)
            saved = dlg.ShowModal()
            if saved == wx.ID_OK:
                result = wx.MessageBox(Strings.label_use_image, Strings.label_image, wx.YES_NO | wx.ICON_QUESTION)
                if result == wx.YES:
                    # This function must be used only when the add image dialog is confirmed.
                    # Parameter expansion, expands tuple into the two arguments needed by the function.
                    self._change_image(*dlg.get_thumbnail_location())
            dlg.Destroy()
        elif event.GetId() == wx.ID_DELETE:
            result = wx.MessageBox(f'{Strings.label_image_path}: {self._image_copy.get_original_image_path()}\n'
                                   f'{Strings.label_image_thumbnail_path}: '
                                   f'{self._image_copy.get_thumbnail_image_path()}',
                                   Strings.label_delete_images,
                                   wx.YES_NO | wx.ICON_QUESTION)
            if result == wx.YES:
                for path in (self._image_copy.get_thumbnail_image_path(), self._image_copy.get_original_image_path()):
                    if os.path.exists(path) and os.access(path, os.R_OK) and os.access(path, os.W_OK):
                        os.remove(path)
                    else:
                        wx.MessageBox(f'{Strings.warning_can_not_delete}:\n{path}', Strings.status_error,
                                      wx.OK | wx.ICON_ERROR)
                self._image_copy.test_self()
                self._display_dialog_contents()
        else:
            # Leave the old image as it is and do not do anything.
            event.Skip()

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name) or None, None if canceled
        """
        path = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_thumbnails)
        if not path:
            path = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_thumbnails)
        with wx.FileDialog(self, Strings.label_select_image, path, wildcard=Strings.image_extensions,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                return dlg.GetPath(), dlg.GetFilename()
            return None, None

    def _change_image(self, path: str, name: str) -> None:
        """
        Change image displayed in the dialog to a new image selected form disk.
        :param path: Disk path.
        :param name: File name
        :return: None
        """
        img_dir: str = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_thumbnails)
        if not path:
            # No image was selected
            return
        if img_dir not in path:
            wx.MessageBox(Strings.warning_wrong_image_folder, Strings.status_error, wx.OK | wx.ICON_ERROR)
            return

        image = wx.Image(path, wx.BITMAP_TYPE_ANY)
        if not math.isclose(Numbers.photo_ratio, (image.GetWidth() / image.GetHeight()),
                            abs_tol=Numbers.photo_ratio_tolerance):
            # Test correct aspect ratio
            wx.MessageBox(Strings.warning_aside_impossible, Strings.status_error, wx.OK | wx.ICON_ERROR)
            return
        else:
            # Display the new image
            html_thumbnail_filename: str = os.path.join(Strings.folder_images, Strings.folder_thumbnails, name)
            self._image_copy = AsideImage(self._field_image_caption.GetValue(),
                                          self._field_image_link_title.GetValue(),
                                          self._field_image_alt.GetValue(),
                                          path.replace(Strings.folder_thumbnails, Strings.folder_originals),
                                          path, html_thumbnail_filename.replace(Strings.folder_thumbnails,
                                                                                Strings.folder_originals),
                                          html_thumbnail_filename)
            # Initializes all internal variables.
            self._image_copy.test_self()
            self._display_dialog_contents()

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
                tip.SetMessage(f'{Strings.seo_check}\n{value[0][1]}')
                tip.EnableTip(True)
                field.SetBackgroundColour(Numbers.RED_COLOR)
            else:
                tip.SetMessage(f'{Strings.seo_check}\n{Strings.status_ok}')
                tip.DoHideNow()
                field.SetBackgroundColour(Numbers.GREEN_COLOR)
            field.SetValue(value[0][0])

        # Set images
        self._bitmap.SetBitmap(wx.Bitmap(self._image_copy.get_image(normal=True)))

        # Set thumbnail size
        thumbnail_size = self._image_copy.get_thumbnail_size()
        if thumbnail_size:
            self._content_image_thumbnail_size.SetLabelText(f'{thumbnail_size[0]} x {thumbnail_size[1]} px')
        else:
            self._content_image_thumbnail_size.SetLabelText(Strings.status_error)

        # Set original size
        original_size = self._image_copy.get_original_size()
        if original_size:
            self._content_image_original_size.SetLabelText(f'{original_size[0]} x {original_size[1]} px')
        else:
            self._content_image_original_size.SetLabelText(Strings.label_none)

        # Set disk paths
        full_path = self._image_copy.get_original_image_path()
        self.SetTitle(f'{Strings.label_dialog_edit_image}: {self._image_copy.get_full_filename()}')
        if full_path:
            self._content_image_full_path.SetLabelText(full_path)
        else:
            self._content_image_full_path.SetLabelText(self._image_copy.get_full_filename())

        thumb_path = self._image_copy.get_thumbnail_image_path()
        if thumb_path:
            self._content_image_thumbnail_path.SetLabelText(thumb_path)
        else:
            self._content_image_thumbnail_path.SetLabelText(self._image_copy.get_thumbnail_filename())

    def was_modified(self) -> bool:
        """
        Returns True if the image was modified in the dialog in any way.
        :return: True if the image was modified in the dialog in any way.
        """
        return self._original_image.is_modified()
