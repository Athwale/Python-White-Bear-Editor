import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.MenuItem import MenuItem
from Tools.Tools import Tools


class EditMenuItemDialog(wx.Dialog):

    def __init__(self, parent, item: MenuItem):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param item: MenuItem instance being edited by tis dialog.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_image,
                           size=(Numbers.edit_aside_image_dialog_width, Numbers.edit_aside_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._item = item

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Disk location
        self.full_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_full_path = wx.StaticText(self, -1, Strings.label_image + ': ')
        self.content_image_full_path = wx.StaticText(self, -1, Strings.label_none)
        self.full_disk_location_sub_sizer.Add(self.label_image_full_path, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.full_disk_location_sub_sizer.Add(self.content_image_full_path,
                                              flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.full_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Link href
        self.href_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_href = wx.StaticText(self, -1, Strings.label_target + ': ')
        self.content_href = wx.StaticText(self, -1, Strings.label_none)
        self.href_sub_sizer.Add(self.label_href, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.href_sub_sizer.Add(self.content_href, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.href_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Original size
        self.image_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_size = wx.StaticText(self, -1, Strings.label_size + ': ')
        self.content_image_size = wx.StaticText(self, -1, Strings.label_none)
        self.image_size_sub_sizer.Add(self.label_image_size,
                                      flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.image_size_sub_sizer.Add((16, -1))
        self.image_size_sub_sizer.Add(self.content_image_size,
                                      flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.image_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Image name sub sizer
        self.name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_item_name = wx.StaticText(self, -1, Strings.label_name + ': ')
        self.field_item_name = wx.TextCtrl(self, -1)
        self.name_sub_sizer.Add(self.label_item_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.name_sub_sizer.Add((8, -1))
        self.name_sub_sizer.Add(self.field_item_name, proportion=1)
        self.information_sizer.Add(self.name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_item_name_tip = Tools.get_warning_tip(self.field_item_name,
                                                         Strings.label_article_image_caption)

        # Image link title sub sizer
        self.title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self.field_image_link_title = wx.TextCtrl(self, -1)
        self.title_sub_sizer.Add(self.label_image_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.title_sub_sizer.Add((44, -1))
        self.title_sub_sizer.Add(self.field_image_link_title, proportion=1)
        self.information_sizer.Add(self.title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_image_link_title_tip = Tools.get_warning_tip(self.field_image_link_title,
                                                                Strings.label_article_image_link_title)

        # Image alt sub sizer
        self.alt_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_alt = wx.StaticText(self, -1, Strings.label_alt_description + ': ')
        self.field_image_alt = wx.TextCtrl(self, -1)
        self.alt_sub_sizer.Add(self.label_image_alt, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.alt_sub_sizer.Add((5, -1))
        self.alt_sub_sizer.Add(self.field_image_alt, proportion=1)
        self.information_sizer.Add(self.alt_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_image_alt_tip = Tools.get_warning_tip(self.field_image_alt, Strings.label_article_image_alt)

        # Image preview
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))
        self.image_sizer.Add(self._bitmap, flag=wx.ALL, border=1)

        # Buttons
        self.button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self.ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self.cancel_button.SetDefault()
        grouping_sizer.Add(self.ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self.cancel_button)
        self.button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self.vertical_sizer.Add(self.information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                border=Numbers.widget_border_size)
        self.horizontal_sizer.Add(self.vertical_sizer, 1)
        self.horizontal_sizer.Add(self.image_sizer, flag=wx.TOP | wx.RIGHT, border=Numbers.widget_border_size)
        self.main_vertical_sizer.Add(self.horizontal_sizer, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                     border=Numbers.widget_border_size)
        self.SetSizer(self.main_vertical_sizer)
        # self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.cancel_button)

        self._original_name = self._item.get_menu_article_name()[0]
        self._original_title = self._item.get_menu_link_title()[0]
        self._original_alt = self._item.get_menu_image_alt()[0]

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OK:
            # Save new information into image and rerun seo test.
            self._item.set_caption(self.field_item_name.GetValue())
            self._item.set_title(self.field_image_link_title.GetValue())
            self._item.set_alt(self.field_image_alt.GetValue())

            if self._item.seo_test_self():
                event.Skip()
                return
            else:
                self._display_dialog_contents()
        else:
            # Restore original values
            self._item.set_caption(self._original_caption)
            self._item.set_title(self._original_title)
            self._item.set_alt(self._original_alt)
            self._item.set_modified(False)
            self._item.seo_test_self()
            event.Skip()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self.field_item_name: (self._item.get_caption(), self.field_item_name_tip),
                          self.field_image_link_title: (self._item.get_link_title(), self.field_image_link_title_tip),
                          self.field_image_alt: (self._item.get_image_alt(), self.field_image_alt_tip)}
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
        self._bitmap.SetBitmap(wx.Bitmap(self._item.get_image()))

        # Set thumbnail size
        thumbnail_size = self._item.get_thumbnail_size()
        if thumbnail_size:
            self.content_image_thumbnail_size.SetLabelText(
                str(thumbnail_size[0]) + ' x ' + str(thumbnail_size[1]) + ' px')
        else:
            self.content_image_thumbnail_size.SetLabelText(Strings.status_error)

        # Set original size
        original_size = self._item.get_original_size()
        if original_size:
            self.content_image_size.SetLabelText(
                str(original_size[0]) + ' x ' + str(original_size[1]) + ' px')
        else:
            self.content_image_size.SetLabelText(Strings.status_error)

        # Set disk paths
        full_path = self._item.get_original_image_path()
        self.SetTitle(Strings.label_dialog_edit_image + ': ' + self._item.get_full_filename())
        if full_path:
            self.content_image_full_path.SetLabelText(full_path)
        else:
            self.content_image_full_path.SetLabelText(self._item.get_full_filename())

        thumb_path = self._item.get_thumbnail_image_path()
        if thumb_path:
            self.content_image_thumbnail_path.SetLabelText(thumb_path)
        else:
            self.content_image_thumbnail_path.SetLabelText(self._item.get_thumbnail_filename())
        self.Enable()
