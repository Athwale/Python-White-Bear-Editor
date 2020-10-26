import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.AsideImage import AsideImage
from Tools.Tools import Tools


class EditAsideImageDialog(wx.Dialog):

    def __init__(self, parent, image: AsideImage):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param image: AsideImage instance being edited by tis dialog.
        """
        # TODO make interactive when the user edits it.
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_image,
                           size=(Numbers.edit_image_dialog_width, Numbers.edit_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._image = image

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self.information_sizer = wx.BoxSizer(wx.VERTICAL)
        # Disk locations
        self.full_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_full_path = wx.StaticText(self, -1, Strings.label_image_path + ': ')
        self.content_image_full_path = wx.StaticText(self, -1, Strings.label_none)
        self.full_disk_location_sub_sizer.Add(self.label_image_full_path, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.full_disk_location_sub_sizer.Add(self.content_image_full_path,
                                              flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.full_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        self.thumb_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_image_thumbnail_path + ': ')
        self.content_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_none)
        self.thumb_disk_location_sub_sizer.Add(self.label_image_thumbnail_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.thumb_disk_location_sub_sizer.Add(self.content_image_thumbnail_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.thumb_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Image caption sub sizer
        self.caption_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_caption = wx.StaticText(self, -1, Strings.label_article_image_caption + ': ')
        self.field_image_caption = wx.TextCtrl(self, -1)
        self.caption_sub_sizer.Add(self.label_image_caption, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.caption_sub_sizer.Add((8, -1))
        self.caption_sub_sizer.Add(self.field_image_caption, proportion=1)
        self.information_sizer.Add(self.caption_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_image_caption_tip = Tools.get_warning_tip(self.field_image_caption,
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

        # Target blank checkbox all link always open in new page
        self.checkbox_target_blank = wx.CheckBox(self, -1, label=Strings.label_open_in_new_page)
        self.checkbox_target_blank.SetValue(True)
        self.checkbox_target_blank.Disable()
        self.information_sizer.Add(self.checkbox_target_blank, flag=wx.TOP, border=Numbers.widget_border_size)

        # Image preview
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
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
        self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self.field_image_caption: (self._image.get_image_caption(), self.field_image_caption_tip),
                          self.field_image_link_title: (self._image.get_link_title(), self.field_image_link_title_tip),
                          self.field_image_alt: (self._image.get_image_alt(), self.field_image_alt_tip)}
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
        self._bitmap.SetBitmap(wx.Bitmap(self._image.get_image()))
        # Set disk paths
        full_path = self._image.get_original_image_path()
        self.SetTitle(Strings.label_dialog_edit_image + ': ' + self._image.get_full_filename())
        if full_path:
            self.content_image_full_path.SetLabelText(full_path)
        else:
            self.content_image_full_path.SetLabelText(self._image.get_full_filename())

        thumb_path = self._image.get_thumbnail_image_path()
        if thumb_path:
            self.content_image_thumbnail_path.SetLabelText(thumb_path)
        else:
            self.content_image_thumbnail_path.SetLabelText(self._image.get_thumbnail_filename())
        self.Enable()
