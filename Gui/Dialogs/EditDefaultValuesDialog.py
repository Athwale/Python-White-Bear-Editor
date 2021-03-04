import wx

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Tools import Tools


class EditDefaultValuesDialog(wx.Dialog):

    def __init__(self, parent, no_cancel: bool = False):
        """
        Display a dialog that allows editing additional data used in html generation.
        Default main title, author, contact, keywords, main page meta description. script, main page red/black text
        :param parent: The parent frame.
        :param no_cancel: Do not display cancel button. Used to force page setup completion.
        """
        # TODO use this in tabbed mode to have ftp settings.
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_page_setup,
                           size=(Numbers.page_setup_dialog_width, Numbers.page_setup_dialog_height),
                           style=wx.CAPTION)

        self._config_manager: ConfigManager = ConfigManager.get_instance()
        # This is used just for seo testing keywords and description.
        self._test_doc: WhitebearDocument = WhitebearDocument('')

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title sub sizer
        # TODO maybe limit this somehow.
        self._title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_main_title = wx.StaticText(self, -1, Strings.label_main_title + ': ')
        self._field_global_title = wx.TextCtrl(self, -1)
        self._title_sub_sizer.Add(self._label_main_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._title_sub_sizer.Add((2, -1))
        self._title_sub_sizer.Add(self._field_global_title, proportion=1)
        self._information_sizer.Add(self._title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_main_title_tip = Tools.get_warning_tip(self._field_global_title, Strings.label_main_title)
        self._field_main_title_tip.SetMessage(Strings.label_main_title_tip)

        # Author sub sizer
        self._author_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_author = wx.StaticText(self, -1, Strings.label_author + ': ')
        self._field_author = wx.TextCtrl(self, -1)
        self._label_news = wx.StaticText(self, -1, Strings.label_number_of_news + ': ')
        self._news_spinner = wx.SpinCtrl(self, -1, style=wx.SP_ARROW_KEYS, min=Numbers.min_news, max=Numbers.max_news,
                                         initial=Numbers.default_news)
        self._author_sub_sizer.Add(self._label_author, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._author_sub_sizer.Add((20, -1))
        self._author_sub_sizer.Add(self._field_author, proportion=1)
        self._author_sub_sizer.Add(Numbers.widget_border_size, Numbers.widget_border_size)
        self._author_sub_sizer.Add(self._label_news, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._author_sub_sizer.Add(Numbers.widget_border_size, Numbers.widget_border_size)
        self._author_sub_sizer.Add(self._news_spinner, proportion=0.3)
        self._information_sizer.Add(self._author_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_author_tip = Tools.get_warning_tip(self._field_author, Strings.label_author)
        self._field_author_tip.SetMessage(Strings.label_author_tip)

        # e-mail sub sizer
        self._contact_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_contact = wx.StaticText(self, -1, Strings.label_contact + ': ')
        self._field_contact = wx.TextCtrl(self, -1)
        self._contact_sub_sizer.Add(self._label_contact, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._contact_sub_sizer.Add((14, -1))
        self._contact_sub_sizer.Add(self._field_contact, proportion=1)
        self._information_sizer.Add(self._contact_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_contact_tip = Tools.get_warning_tip(self._field_contact, Strings.label_contact)
        self._field_contact_tip.SetMessage(Strings.label_contact_tip)

        # Keywords sub sizer
        self._meta_keywords_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_meta_keywords = wx.StaticText(self, -1, Strings.label_default_keywords + ': ')
        self._field_meta_keywords = wx.TextCtrl(self, -1)
        self._meta_keywords_sub_sizer.Add(self._label_meta_keywords, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._meta_keywords_sub_sizer.Add(self._field_meta_keywords, proportion=1)
        self._information_sizer.Add(self._meta_keywords_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_keywords_tip = Tools.get_warning_tip(self._field_meta_keywords, Strings.label_article_keywords)
        self._field_keywords_tip.SetMessage(Strings.label_default_keywords_tip)

        # --------------------------------------------------------------------------------------------------------------
        # Description sub sizer
        self._meta_description_sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self._label_meta_description = wx.StaticText(self, -1, Strings.label_main_meta_description + ': ')
        self._field_meta_description = wx.TextCtrl(self, -1, size=wx.Size(-1, 60), style=wx.TE_MULTILINE)
        self._meta_description_sub_sizer.Add(self._label_meta_description, flag=wx.ALIGN_LEFT)
        self._meta_description_sub_sizer.Add(3, 3)
        self._meta_description_sub_sizer.Add(self._field_meta_description, proportion=1, flag=wx.EXPAND)
        self._information_sizer.Add(self._meta_description_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_description_tip = Tools.get_warning_tip(self._field_meta_description,
                                                            Strings.label_main_meta_description)
        self._field_description_tip.SetMessage(Strings.label_main_description_tip)

        # Script sub sizer
        self._script_sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self._label_script = wx.StaticText(self, -1, Strings.label_script + ': ')
        self._field_script = wx.TextCtrl(self, -1, size=wx.Size(-1, 135), style=wx.TE_MULTILINE)
        self._script_sub_sizer.Add(self._label_script, flag=wx.ALIGN_LEFT)
        self._script_sub_sizer.Add(3, 3)
        self._script_sub_sizer.Add(self._field_script, proportion=1, flag=wx.EXPAND)
        self._information_sizer.Add(self._script_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_script_tip = Tools.get_warning_tip(self._field_script, Strings.label_script)
        self._field_script_tip.SetMessage(Strings.label_script_tip)

        # Black text sub sizer
        self._black_text_sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self._label_black_text = wx.StaticText(self, -1, Strings.label_main_page_text + ': ')
        self._field_black_text = wx.TextCtrl(self, -1, size=wx.Size(-1, 135), style=wx.TE_MULTILINE)
        self._black_text_sub_sizer.Add(self._label_black_text, flag=wx.ALIGN_LEFT)
        self._black_text_sub_sizer.Add(3, 3)
        self._black_text_sub_sizer.Add(self._field_black_text, proportion=1, flag=wx.EXPAND)
        self._information_sizer.Add(self._black_text_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_black_text_tip = Tools.get_warning_tip(self._field_black_text, Strings.label_main_page_text)
        self._field_black_text_tip.SetMessage(Strings.label_main_page_text_tip)

        # Red text sub sizer
        self._red_text_sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self._label_red_text = wx.StaticText(self, -1, Strings.label_main_page_warning + ': ')
        self._label_red_text.SetForegroundColour(wx.RED)
        self._field_red_text = wx.TextCtrl(self, -1, size=wx.Size(-1, 135), style=wx.TE_MULTILINE)
        self._field_red_text.SetForegroundColour(wx.RED)
        self._red_text_sub_sizer.Add(self._label_red_text, flag=wx.ALIGN_LEFT)
        self._red_text_sub_sizer.Add(3, 3)
        self._red_text_sub_sizer.Add(self._field_red_text, proportion=1, flag=wx.EXPAND)
        self._information_sizer.Add(self._red_text_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_red_text_tip = Tools.get_warning_tip(self._field_red_text, Strings.label_main_page_warning)
        self._field_red_text_tip.SetMessage(Strings.label_main_page_warning_tip)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        if no_cancel:
            self._cancel_button.Hide()

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        for field in [self._field_global_title, self._field_author, self._field_contact, self._field_script,
                      self._field_black_text, self._field_red_text, self._field_meta_keywords,
                      self._field_meta_description]:
            self.Bind(wx.EVT_TEXT, self._text_handler, field)

        self._display_dialog_contents()

    # noinspection PyUnusedLocal
    def _text_handler(self, event: wx.CommandEvent) -> None:
        """
        Run seo test on keywords and description when the text changes and prevent saving the values if seo fails.
        :param event: Not used.
        :return: None
        """
        if not self._seo_test():
            self._ok_button.Disable()
            self._cancel_button.Disable()
        else:
            self._ok_button.Enable()
            self._cancel_button.Enable()

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            self._config_manager.store_global_title(self._field_global_title.GetValue())
            self._config_manager.store_author(self._field_author.GetValue())
            self._config_manager.store_contact(self._field_contact.GetValue())
            self._config_manager.store_global_keywords(self._field_meta_keywords.GetValue())
            self._config_manager.store_main_page_description(self._field_meta_description.GetValue())
            self._config_manager.store_script(self._field_script.GetValue())
            self._config_manager.store_black_text(self._field_black_text.GetValue())
            self._config_manager.store_red_text(self._field_red_text.GetValue())
            self._config_manager.store_number_of_news(self._news_spinner.GetValue())

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        self._field_global_title.SetValue(self._config_manager.get_global_title())
        self._field_author.SetValue(self._config_manager.get_author())
        self._field_contact.SetValue(self._config_manager.get_contact())
        self._field_meta_keywords.SetValue(self._config_manager.get_global_keywords())
        self._field_meta_description.SetValue(self._config_manager.get_main_meta_description())
        self._field_script.SetValue(self._config_manager.get_script())
        self._field_black_text.SetValue(self._config_manager.get_main_page_black_text())
        self._field_red_text.SetValue(self._config_manager.get_main_page_red_text())
        self._news_spinner.SetValue(self._config_manager.get_number_of_news())
        self._seo_test()
        self.Enable()

    def _seo_test(self) -> bool:
        """
        SEO test meta keywords and meta description.
        :return: True if seo is ok.
        """
        result = True
        # Keywords test.
        correct, message, color = self._test_doc.seo_test_keywords(self._field_meta_keywords.GetValue())
        result = result and correct
        self._field_meta_keywords.SetBackgroundColour(color)
        self._field_keywords_tip.SetMessage(Strings.label_default_keywords_tip + '\n\n' +
                                            Strings.seo_check + '\n' + message)

        # Description test.
        correct, message, color = self._test_doc.seo_test_description(self._field_meta_description.GetValue())
        result = result and correct
        self._set_field_background(self._field_meta_description, color)
        self._field_description_tip.SetMessage(Strings.label_main_description_tip + '\n\n' +
                                               Strings.seo_check + '\n' + message)

        for field in [self._field_global_title, self._field_author, self._field_contact, self._field_script,
                      self._field_black_text, self._field_red_text]:
            if not field.GetValue():
                result = False
                self._set_field_background(field, Numbers.RED_COLOR)
            else:
                self._set_field_background(field, Numbers.GREEN_COLOR)

        return result

    @staticmethod
    def _set_field_background(field: wx.TextCtrl, color: wx.Colour) -> None:
        """
        Set background color for a field.
        :param field: wx.TextCtrl.
        :param color: The wx.Color to set.
        :return: None
        """
        field.SetBackgroundColour(color)
        style_carrier = wx.TextAttr()
        # Set color for the current text separately, it does not work with just background color
        field.GetStyle(0, style_carrier)
        style_carrier.SetBackgroundColour(color)
        field.SetStyle(0, len(field.GetValue()), style_carrier)
