import wx

from Constants.Constants import Strings, Events
from Gui.Dialogs.SpellCheckerDialog import SpellCheckerDialog
from Gui.Panels.CustomRichText import CustomRichText


class RichTextSpellCheckerDialog(SpellCheckerDialog):
    """
    Spellchecker dialog that works with a customized rich text control. It uses an external instance of
    enchant spellchecker.
    """

    def __init__(self, parent, text_area: CustomRichText) -> None:
        """
        Spellchecker dialog constructor.
        :param parent: Dialog parent.
        :param text_area: RichTextCtrl instance to work with.
        """
        super().__init__(parent, Strings.label_dialog_spellcheck_main, '')
        self._text_area = text_area

    def go_to_next(self) -> bool:
        """
        Moves the SpellChecker to the next mistake, if there is one. It then displays the mistake and some
        surrounding context, as well as listing the suggested replacements.
        :return: False if there is nothing to advance to.
        """
        if super(RichTextSpellCheckerDialog, self).go_to_next():
            self._text_area.SelectWord(self._checker.wordpos)
            # The +1 ensures we always display a line even if it is the last line in currently visible document.
            self._text_area.ShowPosition(self._checker.wordpos + 1)
            return True
        return False

    def _replace(self) -> None:
        """
        Instructs the spellchecker to replace current mistake with the contents of replace_with_field.
        :return: None
        """
        replacement = self.replace_with_field.GetValue()
        if replacement:
            # Replace text inside the rich text control as well as in the checker's text which the checker uses
            # internally.
            self._checker.replace(replacement)
            self._text_area.replace_string_with_style(replacement)
        self.go_to_next()

    # noinspection PyUnusedLocal
    def _close_button_handler(self, event: wx.CloseEvent) -> None:
        """
        Handle dialog closing.
        :param event: Unused.
        :return: None
        """
        # Send an event to the main gui to signal dialog closing.
        done_evt = Events.SpellcheckEvent(self.GetId())
        if self.word_lists_changed():
            # Signal whether to recolor all other documents.
            done_evt.SetInt(1)
        else:
            done_evt.SetInt(0)
        # Dialog has its own event handler, so use the parent.
        wx.PostEvent(self.GetParent().GetEventHandler(), done_evt)
        self.Destroy()

    def run(self) -> None:
        """
        Run spellchecker using the text area given to it.
        :return: None.
        """
        self._checker.set_text(self._text_area.get_text())
        self._found_mistake = self.go_to_next()
