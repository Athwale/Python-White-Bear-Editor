import os

import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.AddLogoDialog import AddLogoDialog
from Gui.Dialogs.SpellCheckedDialog import SpellCheckedDialog
from Tools.Document.MenuItem import MenuItem
from Tools.Tools import Tools


class EditMenuItemDialog(SpellCheckedDialog):

    def __init__(self, parent, item: MenuItem, work_dir: str):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param item: MenuItem instance being edited by this dialog.
        :param work_dir: Working directory of the editor.
        """
        super().__init__(parent, title=Strings.label_dialog_edit_menu_item,
                         size=(Numbers.edit_aside_image_dialog_width, Numbers.edit_menu_item_dialog_height),
                         style=wx.DEFAULT_DIALOG_STYLE)

        self._work_dir = work_dir
        self._original_item: MenuItem = item
        self._item_copy: MenuItem = self._original_item.copy()
        self._item_copy.test_self()

        self._alt_lock = False
        self._title_lock = False

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Disk location
        self._full_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_full_path = wx.StaticText(self, -1, f'{Strings.label_image}: ')
        self.content_image_full_path = wx.StaticText(self, -1, Strings.label_none,
                                                     style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._full_disk_location_sub_sizer.Add(self.label_image_full_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._full_disk_location_sub_sizer.Add(self.content_image_full_path, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._full_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Link href
        self._href_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_href = wx.StaticText(self, -1, f'{Strings.label_target}: ')
        self._content_href = wx.StaticText(self, -1, Strings.label_none,
                                           style=wx.ST_ELLIPSIZE_MIDDLE | wx.ST_NO_AUTORESIZE)
        self._href_sub_sizer.Add(self._label_href, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._href_sub_sizer.Add(self._content_href, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._href_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Original size
        self._image_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_image_size = wx.StaticText(self, -1, f'{Strings.label_size}: ')
        self._content_image_size = wx.StaticText(self, -1, Strings.label_none)
        self._image_size_sub_sizer.Add(self._label_image_size,
                                       flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._image_size_sub_sizer.Add(self._content_image_size,
                                       flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._image_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image name sub sizer
        self._name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_item_name = wx.StaticText(self, -1, f'{Strings.label_menu_name}: ')
        self._field_item_name = wx.TextCtrl(self, -1)
        self._name_sub_sizer.Add(self._label_item_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._name_sub_sizer.Add(self._field_item_name, proportion=1)
        self._information_sizer.Add(self._name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_item_name_tip = Tools.get_warning_tip(self._field_item_name,
                                                          Strings.label_menu_item_name)

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

        self._label_item_name.SetMinSize(self._label_image_alt.GetSize())
        self._label_image_title.SetMinSize(self._label_image_alt.GetSize())

        # Image preview
        self._image_sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))

        # Item name
        menu_text_field_font = wx.Font(Numbers.small_font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                       wx.FONTWEIGHT_NORMAL, False)
        self._content_item_name = wx.StaticText(self, -1, Strings.label_article_menu_logo_name_placeholder,
                                                style=wx.ALIGN_CENTRE_HORIZONTAL)
        self._content_item_name.SetMaxSize((Numbers.menu_logo_image_size, -1))
        self._content_item_name.SetFont(menu_text_field_font)
        self._image_sizer.Add(self._bitmap, flag=wx.CENTER | wx.ALL, border=1)
        self._image_sizer.Add(self._content_item_name, flag=wx.CENTER | wx.ALL, border=1)

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
        self._horizontal_sizer.Add(self._image_sizer, 0, flag=wx.TOP | wx.RIGHT | wx.EXPAND,
                                   border=Numbers.widget_border_size)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_TEXT, self._handle_name_change, self._field_item_name)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._browse_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._add_button)
        self.Bind(wx.EVT_TEXT, self._lock_fields, self._field_image_alt)
        self.Bind(wx.EVT_TEXT, self._lock_fields, self._field_image_link_title)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._delete_button)

    # noinspection PyUnusedLocal
    def _handle_name_change(self, event: wx.CommandEvent) -> None:
        """
        Handle text changes in the item name field, these have to be shown in the live preview under the image.
        Copy the text from the first field to the other fields as long as the contents of them are the same.
        Speeds up filling the metadata for new images.
        :param event: Not used
        :return: None
        """
        self._set_interactive_item_name(self._field_item_name.GetValue())
        text = self._field_item_name.GetValue()
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
        if event.GetId() == Numbers.ID_IMAGE_ALT:
            if self._field_image_alt.GetValue() != self._field_item_name.GetValue():
                self._alt_lock = True
        elif event.GetId() == Numbers.ID_IMAGE_LINK:
            if self._field_image_link_title.GetValue() != self._field_item_name.GetValue():
                self._title_lock = True

    def _set_interactive_item_name(self, text: str) -> None:
        """
        Set a new text into the live preview item name static text, wrap it and return False if it has
        more than 2 lines.
        :param text: The new text.
        :return: None
        """
        self._content_item_name.SetLabelText(text)
        self._content_item_name.Wrap(Numbers.menu_logo_image_size)
        self._image_sizer.Layout()
        if self._content_item_name.GetSize()[1] > Numbers.logo_text_width or len(
                self._field_item_name.GetValue()) < Numbers.menu_name_min_length:
            # The menu name would have 3 or 0 lines which we do not want
            self._ok_button.Disable()
            self._content_item_name.SetBackgroundColour(Numbers.RED_COLOR)
            self._field_item_name.SetBackgroundColour(Numbers.RED_COLOR)
            if len(self._field_item_name.GetValue()) < Numbers.menu_name_min_length:
                self._field_item_name_tip.SetMessage(f'{Strings.seo_check}\n{Strings.seo_error_menu_name_length}')
            if self._content_item_name.GetSize()[1] > Numbers.logo_text_width:
                self._field_item_name_tip.SetMessage(f'{Strings.seo_check}\n{Strings.seo_error_menu_name_width}')
            self._field_item_name_tip.EnableTip(True)
        else:
            self._content_item_name.SetBackgroundColour(wx.NullColour)
            self._item_copy.set_article_name(text)
            self._item_copy.test_self()
            if self._item_copy.get_article_name()[1]:
                # There is an error message for article name.
                self._field_item_name.SetBackgroundColour(Numbers.RED_COLOR)
                self._field_item_name_tip.SetMessage(f'{Strings.seo_check}\n{self._item_copy.get_article_name()[1]}')
                self._field_item_name_tip.EnableTip(True)
            else:
                self._field_item_name.SetBackgroundColour(Numbers.GREEN_COLOR)
                self._field_item_name_tip.SetMessage(f'{Strings.seo_check}\n{Strings.status_ok}')
                self._field_item_name_tip.DoHideNow()
                self._ok_button.Enable()

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event.
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
            # Save new information into image and rerun seo test.
            self._run_spellcheck(((self._field_item_name, Strings.label_menu_item_name),
                                  (self._field_image_link_title, Strings.label_link_title),
                                  (self._field_image_alt, Strings.label_alt_description)))
            self._item_copy.set_article_name(self._field_item_name.GetValue())
            self._item_copy.set_link_title(self._field_image_link_title.GetValue())
            self._item_copy.set_image_alt(self._field_image_alt.GetValue())

            if self._item_copy.test_self():
                self._original_item.set_article_name(self._item_copy.get_article_name()[0])
                self._original_item.set_link_title(self._item_copy.get_link_title()[0])
                self._original_item.set_image_alt(self._item_copy.get_image_alt()[0])
                self._original_item.set_href(self._item_copy.get_link_href())
                self._original_item.set_image_path(self._item_copy.get_image_path())
                self._original_item.set_filename(self._item_copy.get_filename())
                self._original_item.test_self()
                event.Skip()
                return
            else:
                self.display_dialog_contents()
        elif event.GetId() == wx.ID_ADD:
            dlg = AddLogoDialog(self, self._work_dir, self._item_copy.get_article_name()[0])
            saved = dlg.ShowModal()
            if saved == wx.ID_OK:
                result = wx.MessageBox(Strings.label_use_image, Strings.label_image, wx.YES_NO | wx.ICON_QUESTION)
                if result == wx.YES:
                    # This function must be used only when the add image dialog is confirmed.
                    # Parameter expansion, expands tuple into the two arguments needed by the function.
                    self._change_image(*dlg.get_logo_location())
            dlg.Destroy()
        elif event.GetId() == wx.ID_DELETE:
            result = wx.MessageBox(f'{Strings.label_image}: {self._item_copy.get_image_path()}\n',
                                   Strings.label_delete_images,
                                   wx.YES_NO | wx.ICON_QUESTION)
            if result == wx.YES:
                path = self._item_copy.get_image_path()
                if os.path.exists(path) and os.access(path, os.R_OK) and os.access(path, os.W_OK):
                    os.remove(path)
                else:
                    wx.MessageBox(f'{Strings.warning_can_not_delete}:\n{path}', Strings.status_error,
                                  wx.OK | wx.ICON_ERROR)
            self._item_copy.test_self()
            self.display_dialog_contents()
        else:
            # Leave the original item as it is.
            event.Skip()

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name) or None, None if canceled
        """
        path = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_logos)
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
        img_dir: str = os.path.join(self._work_dir, Strings.folder_images, Strings.folder_logos)
        if not path:
            return
        if img_dir not in path:
            wx.MessageBox(Strings.warning_wrong_logo_folder, Strings.status_error, wx.OK | wx.ICON_ERROR)
            return

        image = wx.Image(path, wx.BITMAP_TYPE_ANY)
        if image.GetSize() != (Numbers.menu_logo_image_size, Numbers.menu_logo_image_size):
            wx.MessageBox(Strings.warning_wrong_logo_size, Strings.status_error, wx.OK | wx.ICON_ERROR)
            return
        else:
            # Display the new image
            html_image_filename: str = os.path.join(Strings.folder_images, Strings.folder_logos, name)
            self._item_copy = MenuItem(self._field_item_name.GetValue(),
                                       self._field_image_link_title.GetValue(),
                                       self._field_image_alt.GetValue(),
                                       self._original_item.get_link_href(),
                                       path,
                                       html_image_filename)
            # Initializes all internal variables.
            self._item_copy.test_self()
            self.display_dialog_contents()

    def display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        Must be called after the dialog is constructed for label size measuring to work correctly.
        :return: None
        """
        # Set image data
        field_to_value = {self._field_item_name: (self._item_copy.get_article_name(), self._field_item_name_tip),
                          self._field_image_link_title: (self._item_copy.get_link_title(),
                                                         self._field_image_link_title_tip),
                          self._field_image_alt: (self._item_copy.get_image_alt(), self._field_image_alt_tip)}
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

        # Set image
        self._bitmap.SetBitmap(wx.Bitmap(self._item_copy.get_image(normal=True)))

        # Set target
        self._content_href.SetLabelText(self._item_copy.get_link_href())

        # Set name label
        self._set_interactive_item_name(self._item_copy.get_article_name()[0])

        # Set image size
        size = self._item_copy.get_image_size()
        if size:
            self._content_image_size.SetLabelText(f'{size[0]} x {size[1]} px')
        else:
            self._content_image_size.SetLabelText(Strings.status_error)

        # Set disk paths
        full_path = self._item_copy.get_image_path()
        self.SetTitle(f'{Strings.label_dialog_edit_menu_item}: {self._item_copy.get_article_name()[0]}')
        if full_path:
            self.content_image_full_path.SetLabelText(full_path)
        else:
            self.content_image_full_path.SetLabelText(self._item_copy.get_filename())

        # Disable auto copy of fields if the fields contain different data.
        if self._field_image_link_title.GetValue() != self._field_item_name.GetValue():
            self._title_lock = True
        if self._field_image_alt.GetValue() != self._field_item_name.GetValue():
            self._alt_lock = True

    def was_modified(self) -> bool:
        """
        Returns True if the item was modified in the dialog in any way.
        :return: True if the item was modified in the dialog in any way.
        """
        return self._original_item.is_modified()
