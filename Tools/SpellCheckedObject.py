from Tools.ConfigManager import ConfigManager
from enchant.checker import SpellChecker


class SpellCheckedObject:

    def __init__(self):
        """
        Constructor for a spell checked element base class.
        Sets up spellchecker.
        """
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        # TODO single instance breaks while saving in threads. How to have multiple checkers with one file?
        self._checker: SpellChecker = self._config_manager.get_spellchecker()

    def _spell_check(self, text: str) -> bool:
        """
        Do a spellcheck on the text.
        :param text: Text to check.
        :return: Return False if incorrect.
        """
        self._checker.set_text(text)
        try:
            self._checker.next()
            return False
        except StopIteration:
            # Next raises exception if no mistake is found.
            return True
