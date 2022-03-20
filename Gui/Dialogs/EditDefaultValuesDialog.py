import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.SpellCheckedDialog import SpellCheckedDialog
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.SpellCheckerWithIgnoredList import SpellCheckerWithIgnoreList
from Tools.Tools import Tools


class EditDefaultValuesDialog(SpellCheckedDialog):

    def __init__(self, parent, no_cancel: bool = False):
        """
        Display a dialog that allows editing additional data used in html generation.
        Default main title, author, contact, keywords, main page meta description. script, main page red/black text
        :param parent: The parent frame.
        :param no_cancel: Do not display cancel button. Used to force page setup completion.
        """
        super().__init__(parent, title=Strings.label_dialog_page_setup, size=(Numbers.page_setup_dialog_width,
                         Numbers.page_setup_dialog_height), style=wx.CAPTION)

        self._config_manager: ConfigManager = ConfigManager.get_instance()
        # Multiple inheritance with spellchecked object was causing trouble, so we have our own method.
        self._checker = SpellCheckerWithIgnoreList(self._config_manager.get_spelling_lang())
        # This is used just for seo testing keywords and description.
        self._test_doc: WhitebearDocument = WhitebearDocument('')
        self._save_all = False

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title sub sizer
        self._title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_main_title = wx.StaticText(self, -1, f'{Strings.label_global_title}: ')
        self._field_global_title = wx.TextCtrl(self, -1)
        self._title_sub_sizer.Add(self._label_main_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._title_sub_sizer.Add((2, -1))
        self._title_sub_sizer.Add(self._field_global_title, proportion=1)
        self._information_sizer.Add(self._title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_global_title_tip = Tools.get_warning_tip(self._field_global_title, Strings.label_global_title)
        self._field_global_title_tip.SetMessage(Strings.label_main_title_tip)

        # Url sub sizer
        self._url_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_url = wx.StaticText(self, -1, f'{Strings.label_website_url}: ')
        self._field_url = wx.TextCtrl(self, -1)
        self._url_sub_sizer.Add(self._label_url, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._url_sub_sizer.Add((44, -1))
        self._url_sub_sizer.Add(self._field_url, proportion=1)
        self._information_sizer.Add(self._url_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_url_tip = Tools.get_warning_tip(self._field_url, Strings.label_website_url)
        self._field_url_tip.SetMessage(Strings.label_website_url_tip)

        # Author sub sizer
        self._author_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_author = wx.StaticText(self, -1, f'{Strings.label_author}: ')
        self._field_author = wx.TextCtrl(self, -1)
        self._label_news = wx.StaticText(self, -1, f'{Strings.label_number_of_news}: ')
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
        self._label_contact = wx.StaticText(self, -1, f'{Strings.label_contact}: ')
        self._field_contact = wx.TextCtrl(self, -1)
        self._contact_sub_sizer.Add(self._label_contact, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._contact_sub_sizer.Add((14, -1))
        self._contact_sub_sizer.Add(self._field_contact, proportion=1)
        self._information_sizer.Add(self._contact_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_contact_tip = Tools.get_warning_tip(self._field_contact, Strings.label_contact)
        self._field_contact_tip.SetMessage(Strings.label_contact_tip)

        # Keywords sub sizer
        self._meta_keywords_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_meta_keywords = wx.StaticText(self, -1, f'{Strings.label_default_keywords}: ')
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
        self._label_meta_description = wx.StaticText(self, -1, f'{Strings.label_main_meta_description}: ')
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
        self._label_script = wx.StaticText(self, -1, f'{Strings.label_script}: ')
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
        self._label_black_text = wx.StaticText(self, -1, f'{Strings.label_main_page_text}: ')
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
        self._label_red_text = wx.StaticText(self, -1, f'{Strings.label_main_page_warning}: ')
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
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)

        self._display_dialog_contents()

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OK and self._ok_button.IsEnabled():
            # Run spellcheck then run seo test, then save if ok.
            self._run_spellcheck(((self._field_global_title, Strings.label_global_title),
                                  (self._field_author, Strings.label_author),
                                  (self._field_meta_keywords, Strings.label_default_keywords),
                                  (self._field_meta_description, Strings.label_main_meta_description),
                                  (self._field_black_text, Strings.label_main_page_text),
                                  (self._field_red_text, Strings.label_main_page_warning)))
            if self._seo_test():
                # In these cases all documents must be re-exported to reflect the change.
                result = self._config_manager.store_global_title(self._field_global_title.GetValue())
                self._save_all = self._save_all or result
                result = self._config_manager.store_author(self._field_author.GetValue())
                self._save_all = self._save_all or result
                result = self._config_manager.store_script(self._field_script.GetValue())
                self._save_all = self._save_all or result

                # Keywords can be individual for each page. The global value is for new articles.
                self._config_manager.store_url(self._field_url.GetValue())
                self._config_manager.store_global_keywords(self._field_meta_keywords.GetValue())
                self._config_manager.store_contact(self._field_contact.GetValue())
                self._config_manager.store_main_page_description(self._field_meta_description.GetValue())
                self._config_manager.store_black_text(self._field_black_text.GetValue())
                self._config_manager.store_red_text(self._field_red_text.GetValue())
                self._config_manager.store_number_of_news(self._news_spinner.GetValue())
                event.Skip()
        elif event.GetId() == wx.ID_CANCEL:
            event.Skip()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        self._field_global_title.SetValue(self._config_manager.get_global_title())
        self._field_url.SetValue(self._config_manager.get_url())
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
        # Spellcheck here is a part of the seo tests.
        correct, message, color = self._test_doc.seo_test_keywords(self._field_meta_keywords.GetValue())
        result = result and correct
        self._field_meta_keywords.SetBackgroundColour(color)
        self._field_keywords_tip.SetMessage(f'{Strings.label_default_keywords_tip}\n\n{Strings.seo_check}\n{message}')

        # Description test.
        correct, message, color = self._test_doc.seo_test_description(self._field_meta_description.GetValue())
        result = result and correct
        Tools.set_field_background(self._field_meta_description, color)
        self._field_description_tip.SetMessage(f'{Strings.label_main_description_tip}\n\n{Strings.seo_check}\n'
                                               f'{message}')

        # Check emptiness.
        # Check length and spelling.
        for sp, field, tip, msg in ((True, self._field_global_title, self._field_global_title_tip,
                                     Strings.label_main_title_tip),
                                    (True, self._field_author, self._field_author_tip,
                                     Strings.label_author_tip),
                                    (False, self._field_contact, self._field_contact_tip,
                                     Strings.label_contact_tip),
                                    (False, self._field_url, self._field_url_tip,
                                     Strings.label_website_url_tip),
                                    (False, self._field_script, self._field_script_tip,
                                     Strings.label_script_tip),
                                    (True, self._field_black_text, self._field_black_text_tip,
                                     Strings.label_main_page_text_tip),
                                    (True, self._field_red_text, self._field_red_text_tip,
                                     Strings.label_main_page_warning_tip)):
            if field in (self._field_global_title, self._field_author, self._field_contact, self._field_url) and \
                    (len(field.GetValue()) > Numbers.default_max_length or len(field.GetValue()) < 1):
                result = False
                Tools.set_field_background(field, Numbers.RED_COLOR)
                tip.SetMessage(f'{msg}\n\n{Strings.seo_check}\n{Strings.seo_error_length}: 1 - '
                               f'{Numbers.default_max_length}')
            elif field in (self._field_script, self._field_black_text, self._field_red_text) and not field.GetValue():
                result = False
                Tools.set_field_background(field, Numbers.RED_COLOR)
                tip.SetMessage(f'{msg}\n\n{Strings.seo_check}\n{Strings.seo_error_not_empty}')
            elif not self._spell_check(field.GetValue()) and sp:
                # Run spellcheck on this field.
                # In other cases spellcheck is done by the object copy and error messages are set in it.
                # Here we do not have the copy and have to do it as part of this method again.
                # Keywords and description already have a spellcheck in their builtin seo test.
                result = False
                Tools.set_field_background(field, Numbers.RED_COLOR)
                tip.SetMessage(f'{msg}\n\n{Strings.seo_check}\n{Strings.spelling_error}')
            else:
                Tools.set_field_background(field, Numbers.GREEN_COLOR)
                tip.SetMessage(f'{msg}\n\n{Strings.seo_check}\n{Strings.status_ok}')

        return result

    def _spell_check(self, text: str) -> bool:
        """
        Do a spellcheck on the text.
        :param text: Text to check.
        :return: Return False if incorrect.
        """
        # Reload ignored words, these internal instances would not otherwise know about new words added to the list.
        self._checker.reload_language()
        self._checker.set_text(text)
        try:
            self._checker.next()
            return False
        except StopIteration:
            # Next raises exception if no mistake is found.
            return True

    def save_all(self) -> bool:
        """
        Returns True if main title, author or script changed in that case all documents must be re-exported to
        reflect the new change.
        :return: True if re-export of all document is needed.
        """
        return self._save_all
