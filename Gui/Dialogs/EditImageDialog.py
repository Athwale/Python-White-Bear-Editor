import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.AsideImage import AsideImage


class EditImageDialog(wx.Dialog):

    def __init__(self, parent, image: AsideImage):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        :param image: AsideImage instance being edited by tis dialog.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_image,
                           size=(Numbers.edit_image_dialog_width, Numbers.edit_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self.image = image

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
        self.label_image_caption = wx.StaticText(self, -1, Strings.label_alt_description + ': ')
        self.field_image_caption = wx.TextCtrl(self, -1)
        self.caption_sub_sizer.Add(self.label_image_caption, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.caption_sub_sizer.Add((5, -1))
        self.caption_sub_sizer.Add(self.field_image_caption, proportion=1)
        self.information_sizer.Add(self.caption_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)

        # Image link title sub sizer
        self.title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self.field_image_link_title = wx.TextCtrl(self, -1)
        self.title_sub_sizer.Add(self.label_image_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.title_sub_sizer.Add((44, -1))
        self.title_sub_sizer.Add(self.field_image_link_title, proportion=1)
        self.information_sizer.Add(self.title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)

        # Image alt sub sizer
        self.alt_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_alt = wx.StaticText(self, -1, Strings.label_alt_description + ': ')
        self.field_image_alt = wx.TextCtrl(self, -1)
        self.alt_sub_sizer.Add(self.label_image_alt, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.alt_sub_sizer.Add((5, -1))
        self.alt_sub_sizer.Add(self.field_image_alt, proportion=1)
        self.information_sizer.Add(self.alt_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)

        # Target blank checkbox
        self.checkbox_target_blank = wx.CheckBox(self, -1, label=Strings.label_open_in_new_page)
        self.information_sizer.Add(self.checkbox_target_blank, flag=wx.TOP, border=Numbers.widget_border_size)

        # Image preview
        self.image_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, Strings.label_image)
        placeholder_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))
        self.image_sizer.Add(self._bitmap, flag=wx.ALL, border=1)

        # Buttons
        self.button_sizer = wx.BoxSizer(wx.VERTICAL)
        gouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self.ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self.cancel_button.SetDefault()
        gouping_sizer.Add(self.ok_button)
        gouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        gouping_sizer.Add(self.cancel_button)
        self.button_sizer.Add(gouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self.vertical_sizer.Add(self.information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                border=Numbers.widget_border_size)
        self.horizontal_sizer.Add(self.vertical_sizer, 1)
        self.horizontal_sizer.Add(self.image_sizer, flag=wx.TOP, border=Numbers.widget_border_size)
        self.main_vertical_sizer.Add(self.horizontal_sizer, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                     border=Numbers.widget_border_size)
        self.SetSizer(self.main_vertical_sizer)
