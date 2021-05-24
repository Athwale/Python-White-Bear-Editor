import wx

from Constants.Constants import Strings, Numbers
from Threads.WorkerThread import WorkerThread
from Tools.ConfigManager import ConfigManager
from Tools.Document.ArticleElements.Video import Video
from Tools.Tools import Tools


class EditVideoDialog(wx.Dialog):

    def __init__(self, parent, video: Video):
        """
        Display a dialog with information about the video where the user can edit it.
        :param parent: Parent frame.
        :param video: Video instance being edited by tis dialog.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_video, size=(Numbers.edit_video_dialog_width,
                                                                                      Numbers.edit_video_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._video = video
        self._config_manager = ConfigManager.get_instance()

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title sub sizer
        self._title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_video_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self._field_video_link_title = wx.TextCtrl(self, -1)
        self._title_sub_sizer.Add(self._label_video_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._title_sub_sizer.Add((5, -1))
        self._title_sub_sizer.Add(self._field_video_link_title, proportion=1)
        self._information_sizer.Add(self._title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_video_link_title_tip = Tools.get_warning_tip(self._field_video_link_title,
                                                                 Strings.label_video_link_title)

        # Url sub sizer
        self._url_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_video_url = wx.StaticText(self, -1, Strings.label_url + ': ')
        self._field_video_url = wx.TextCtrl(self, -1)
        self._url_sub_sizer.Add(self._label_video_url, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._url_sub_sizer.Add((34, -1))
        self._url_sub_sizer.Add(self._field_video_url, proportion=1)
        self._information_sizer.Add(self._url_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_video_url_tip = Tools.get_warning_tip(self._field_video_url, Strings.label_url)

        # Size
        self._video_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_video_size = wx.StaticText(self, -1, Strings.label_video_size + ': ')
        self._content_video_size = wx.StaticText(self, -1, Strings.label_none)
        self._video_size_sub_sizer.Add(self._label_video_size, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._video_size_sub_sizer.Add(self._content_video_size, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._information_sizer.Add(self._video_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)

        self._original_url = self._video.get_url()[0]
        self._original_title = self._video.get_title()[0]

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OK:
            # Save new information into image and rerun seo test.
            self._video.set_title(self._field_video_link_title.GetValue())
            self._video.set_url(self._field_video_url.GetValue())

            # Run seo test in thread and show a testing dialog.
            self._seo_test(return_value=wx.ID_OK)
        else:
            # Restore original values
            self._video.set_url(self._original_url)
            self._video.set_title(self._original_title)
            self._video.set_modified(False)
            self._seo_test(return_value=wx.ID_CANCEL)

    def _seo_test(self, return_value: int) -> None:
        """
        Run a url seo test in a separate thread and wait for result from a callback method.
        Display a waiting message.
        :param return_value: wx return code to end this dialog with when the thread finishes.
        :return: None
        """
        thread = WorkerThread(self,
                              function=self._video.seo_test_self,
                              args=(self._config_manager.get_online_test(),),
                              callback=self.on_seo_done,
                              passing_arg=return_value)
        thread.start()
        self.Disable()
        self.SetTitle(Strings.status_seo + ': ' + Strings.status_testing_link)

    def on_seo_done(self, result: bool, return_value: int) -> None:
        """
        Receive the result of the video url SEO test. This is used when closing the dialog.
        :param result: True or False depending on whether the link passed SEO test
        :param return_value: Dialog wx return value.
        :return: None
        """
        self.Enable()
        self.SetTitle(Strings.label_dialog_edit_video)
        if result and self._video.get_status_color() != Numbers.RED_COLOR:
            self.EndModal(return_value)
        else:
            self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self._field_video_link_title: (self._video.get_title(), self._field_video_link_title_tip),
                          self._field_video_url: (self._video.get_url(), self._field_video_url_tip)}
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
            self._content_video_size.SetLabelText(str(size[0]) + ' / ' + str(size[1]) + 'px')
        else:
            self._content_video_size.SetLabelText(Strings.status_error)
        self.Enable()
