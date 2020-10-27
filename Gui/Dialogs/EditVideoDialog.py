import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.ArticleElements.Video import Video
from Tools.Tools import Tools


class EditVideoDialog(wx.Dialog):

    def __init__(self, parent, video: Video):
        """
        Display a dialog with information about the video where the user can edit it.
        :param parent: Parent frame.
        :param video: Video instance being edited by tis dialog.
        """
        # TODO make interactive when the user edits it.
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_video, size=(Numbers.edit_video_dialog_width,
                           Numbers.edit_video_dialog_height), style=wx.DEFAULT_DIALOG_STYLE)
        self._video = video

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title sub sizer
        self.title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_video_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self.field_video_link_title = wx.TextCtrl(self, -1)
        self.title_sub_sizer.Add(self.label_video_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.title_sub_sizer.Add((5, -1))
        self.title_sub_sizer.Add(self.field_video_link_title, proportion=1)
        self.information_sizer.Add(self.title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_video_link_title_tip = Tools.get_warning_tip(self.field_video_link_title,
                                                                Strings.label_video_link_title)

        # Url sub sizer
        self.url_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_video_url = wx.StaticText(self, -1, Strings.label_url + ': ')
        self.field_video_url = wx.TextCtrl(self, -1)
        self.url_sub_sizer.Add(self.label_video_url, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.url_sub_sizer.Add((34, -1))
        self.url_sub_sizer.Add(self.field_video_url, proportion=1)
        self.information_sizer.Add(self.url_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_video_url_tip = Tools.get_warning_tip(self.field_video_url, Strings.label_url)

        # Size
        self.video_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_video_size = wx.StaticText(self, -1, Strings.label_video_size + ': ')
        self.content_video_size = wx.StaticText(self, -1, Strings.label_none)
        self.video_size_sub_sizer.Add(self.label_video_size, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.video_size_sub_sizer.Add(self.content_video_size, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.video_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

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
        self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self.field_video_link_title: (self._video.get_title(), self.field_video_link_title_tip),
                          self.field_video_url: (self._video.get_url(), self.field_video_url_tip)}
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
        # Set size
        size = self._video.get_size()
        if size:
            self.content_video_size.SetLabelText(str(size[0]) + ' / ' + str(size[1]) + 'px')
        else:
            self.content_video_size.SetLabelText(Strings.status_error)
        self.Enable()
