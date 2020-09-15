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
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_image, size=(600, 400),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self.image = image

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self.information_sizer = wx.BoxSizer(wx.VERTICAL)
        # Disk locations
        # TODO do the same sizer thing as below here
        self.label_image_full_path = wx.StaticText(self, -1, Strings.label_image_path + ': ')
        self.label_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_image_thumbnail_path + ': ')
        self.information_sizer.Add(self.label_image_full_path, flag=wx.TOP, border=Numbers.widget_border_size)
        self.information_sizer.Add(self.label_image_thumbnail_path, flag=wx.TOP, border=Numbers.widget_border_size)

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

        # Buttons
        self.button_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'buttons')
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self.ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self.cancel_button.SetDefault()
        self.button_sizer.Add(self.ok_button, flag=wx.ALIGN_LEFT)
        self.button_sizer.Add(self.cancel_button, flag=wx.ALIGN_RIGHT)

        # Putting the sizers together
        self.main_vertical_sizer.Add(self.information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                     border=Numbers.widget_border_size)
        self.main_vertical_sizer.Add(self.button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                                     border=Numbers.widget_border_size)
        self.SetSizer(self.main_vertical_sizer)
