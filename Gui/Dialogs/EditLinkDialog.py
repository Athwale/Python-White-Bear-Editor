import wx

from Constants.Constants import Strings, Numbers
from Tools.Tools import Tools


class EditLinkDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        # TODO pass in an instance of seo checkable parsed link from the article to display or a blank link if new
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_link,
                           size=(Numbers.edit_image_dialog_width, Numbers.edit_link_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Link URL sub sizer
        self.url_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_url = wx.StaticText(self, -1, Strings.label_url + ': ')
        self.field_url = wx.TextCtrl(self, -1)
        self.url_sub_sizer.Add(self.label_url, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.url_sub_sizer.Add((35, -1))
        self.url_sub_sizer.Add(self.field_url, proportion=1)
        self.information_sizer.Add(self.url_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_url_tip = Tools.get_warning_tip(self.field_url, Strings.label_url)

        # Link title sub sizer
        self.title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_link_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self.field_link_title = wx.TextCtrl(self, -1)
        self.title_sub_sizer.Add(self.label_link_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.title_sub_sizer.Add((8, -1))
        self.title_sub_sizer.Add(self.field_link_title, proportion=1)
        self.information_sizer.Add(self.title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_link_title_tip = Tools.get_warning_tip(self.field_link_title, Strings.label_link_title)

        # Link text sub sizer
        self.text_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_link_text = wx.StaticText(self, -1, Strings.label_text + ': ')
        self.field_link_text = wx.TextCtrl(self, -1)
        self.text_sub_sizer.Add(self.label_link_text, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.text_sub_sizer.Add((35, -1))
        self.text_sub_sizer.Add(self.field_link_text, proportion=1)
        self.information_sizer.Add(self.text_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_link_text_tip = Tools.get_warning_tip(self.field_link_text, Strings.label_text)

        # Target blank checkbox
        self.checkbox_target_blank = wx.CheckBox(self, -1, label=Strings.label_open_in_new_page)
        self.information_sizer.Add(self.checkbox_target_blank, flag=wx.TOP, border=Numbers.widget_border_size)

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
        self.main_vertical_sizer.Add(self.horizontal_sizer, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                     border=Numbers.widget_border_size)
        self.SetSizer(self.main_vertical_sizer)
        # TODO modify this to show a combo box wit editability showing all currently loaded pages to pick from.

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self.field_url: (self._image.get_image_caption(), self.field_url_tip),
                          self.field_link_title: (self._image.get_link_title(), self.field_link_title_tip),
                          self.field_link_text: (self._image.get_image_alt(), self.field_link_text_tip)}
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

        # Set target blank checkbox state
        self.checkbox_target_blank.Disable()
        self.checkbox_target_blank.SetValue(True)
        self.Enable()
