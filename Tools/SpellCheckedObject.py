from Tools.ConfigManager import ConfigManager
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter


class SpellCheckedObject:

    def __init__(self):
        """
        Constructor for a spell checked element base class.
        Sets up spellchecker.
        """
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._spellchecker = SpellChecker(self._config_manager.get_spelling_lang(), filters=[EmailFilter, URLFilter])

    def _spell_check(self, text: str) -> bool:
        """
        Do a spellcheck on the text.
        :param text: Text to check.
        :return: Return False if incorrect.
        """
        self._spellchecker.set_text(text)
        try:
            self._spellchecker.next()
            return False
        except StopIteration:
            # Next raises exception if no mistake is found.
            return True
