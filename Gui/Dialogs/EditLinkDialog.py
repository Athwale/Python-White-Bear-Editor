import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.SpellCheckedDialog import SpellCheckedDialog
from Threads.WorkerThread import WorkerThread
from Tools.ConfigManager import ConfigManager
from Tools.Document.ArticleElements.Link import Link
from Tools.Tools import Tools


class EditLinkDialog(SpellCheckedDialog):

    def __init__(self, parent, link: Link):
        """
        Display a dialog with information about the link where the user can edit it.
        :param parent: Parent frame.
        :param link: the Link instance to display.
        """
        super().__init__(parent, title=Strings.label_dialog_edit_link,
                         size=(Numbers.edit_link_dialog_width, Numbers.edit_link_dialog_height),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._link = link
        self._config_manager = ConfigManager.get_instance()

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Link URL sub sizer
        self._url_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_url = wx.StaticText(self, -1, Strings.label_url + ': ')
        choices = self._link.get_loaded_pages()
        choices.append(Strings.index + Strings.extension_html)
        self._field_url = wx.ComboBox(self, -1, choices=choices, style=wx.CB_DROPDOWN | wx.CB_SORT)
        # Fires when you type in the box
        self.Bind(wx.EVT_TEXT, self._combobox_handler, self._field_url)

        self._url_sub_sizer.Add(self._label_url, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._url_sub_sizer.Add((35, -1))
        self._url_sub_sizer.Add(self._field_url, proportion=1)
        self._information_sizer.Add(self._url_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_url_tip = Tools.get_warning_tip(self._field_url, Strings.label_url)

        # Link title sub sizer
        self._title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_link_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self._field_link_title = wx.TextCtrl(self, -1)
        self._title_sub_sizer.Add(self._label_link_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._title_sub_sizer.Add((8, -1))
        self._title_sub_sizer.Add(self._field_link_title, proportion=1)
        self._information_sizer.Add(self._title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_link_title_tip = Tools.get_warning_tip(self._field_link_title, Strings.label_link_title)

        # Link text sub sizer
        self._text_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_link_text = wx.StaticText(self, -1, Strings.label_text + ': ')
        self._field_link_text = wx.TextCtrl(self, -1)
        self._text_sub_sizer.Add(self._label_link_text, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._text_sub_sizer.Add((35, -1))
        self._text_sub_sizer.Add(self._field_link_text, proportion=1)
        self._information_sizer.Add(self._text_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_link_text_tip = Tools.get_warning_tip(self._field_link_text, Strings.label_text)

        # Target blank checkbox
        self._checkbox_target_blank = wx.CheckBox(self, -1, label=Strings.label_open_in_new_page)
        self._checkbox_target_blank.SetValue(True)
        self._checkbox_target_blank.Disable()
        # Local link checkbox
        self._checkbox_local = wx.CheckBox(self, -1, label=Strings.label_link_local)
        self._checkbox_local.Disable()
        self._information_sizer.Add(self._checkbox_target_blank, flag=wx.TOP, border=Numbers.widget_border_size)
        self._information_sizer.Add(self._checkbox_local, flag=wx.TOP, border=Numbers.widget_border_size)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        self._delete_button = wx.Button(self, wx.ID_DELETE, Strings.button_remove_link)
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._delete_button)
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
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._delete_button)

        self._original_text = self._link.get_text()[0]
        self._original_url = self._link.get_url()[0]
        self._original_title = self._link.get_title()[0]

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing on ok if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_DELETE:
            # Only OK and Cancel button close the dialog by default.
            event.Skip()
            self.EndModal(wx.ID_DELETE)
        elif event.GetId() == wx.ID_OK:
            self._run_spellcheck(((self._field_link_title, Strings.label_link_title),
                                  (self._field_link_text, Strings.label_text)))
            # Save new information into image and rerun seo test.
            self._link.set_text(self._field_link_text.GetValue())
            self._link.set_title(self._field_link_title.GetValue())
            self._link.set_url(self._field_url.GetValue())

            # Run seo test in thread and show a testing dialog.
            self._seo_test(return_value=wx.ID_OK)
        else:
            # Restore original values
            self._link.set_url(self._original_url)
            self._link.set_title(self._original_title)
            self._link.set_text(self._original_text)
            self._link.set_modified(False)
            self._seo_test(return_value=wx.ID_CANCEL)

    def _seo_test(self, return_value: int) -> None:
        """
        Run a link seo test in a separate thread and wait for result from a callback method.
        Display a waiting message.
        :param return_value: wx return code to end this dialog with when the thread finishes.
        :return: None
        """
        thread = WorkerThread(self,
                              function=self._link.seo_test_self,
                              args=(self._config_manager.get_online_test(),),
                              callback=self.on_seo_done,
                              passing_arg=return_value)
        thread.start()
        self.Disable()
        self.SetTitle(Strings.status_seo + ': ' + Strings.status_testing_link)

    def on_seo_done(self, result: bool, return_value: int) -> None:
        """
        Receive the result of the link's SEO test. This is used when closing the dialog.
        :param result: True or False depending on whether the link passed SEO test
        :param return_value: Dialog wx return value.
        :return: None
        """
        if return_value == wx.ID_CANCEL:
            self.EndModal(return_value)
        self.Enable()
        self.SetTitle(Strings.label_dialog_edit_link)
        if result and self._link.get_status_color() != Numbers.RED_COLOR:
            self.EndModal(return_value)
        else:
            self._display_dialog_contents()

    # noinspection PyUnusedLocal
    def _combobox_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle actions made in the combobox control.
        :param event: Not used.
        :return: None
        """
        if self._field_url.GetValue() in self._link.get_loaded_pages():
            self._link.set_local(True)
            self._checkbox_local.SetValue(True)
        else:
            self._link.set_local(False)
            self._checkbox_local.SetValue(False)

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self._field_url: (self._link.get_url(), self._field_url_tip),
                          self._field_link_title: (self._link.get_title(), self._field_link_title_tip),
                          self._field_link_text: (self._link.get_text(), self._field_link_text_tip)}
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

        # Set checkbox local state
        self._checkbox_local.SetValue(self._link.is_local())
        self.Enable()
