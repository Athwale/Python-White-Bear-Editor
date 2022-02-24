from Tools.ConfigManager import ConfigManager

from Tools.SpellCheckerWithIgnoredList import SpellCheckerWithIgnoreList


class SpellCheckedObject:

    def __init__(self):
        """
        Constructor for a spell checked element base class.
        Sets up spellchecker.
        """
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._checker = SpellCheckerWithIgnoreList(self._config_manager.get_spelling_lang())

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
