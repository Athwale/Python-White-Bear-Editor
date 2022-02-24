from pathlib import Path
from typing import Optional

import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter

from Constants.Constants import Strings
from Tools.ConfigManager import ConfigManager


class SpellCheckerWithIgnoreList(SpellChecker):
    """
    Subclass of SpellChecker that maintains a permanent list of ignored words.
    """

    def __init__(self, lang: str):
        """
        Constructor for spellchecker with EmailFilter, URLFilter and ignore list built in.
        :param lang: Spelling language.
        """
        super().__init__(lang, filters=[EmailFilter, URLFilter])
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self.reload_language()

    def reload_language(self) -> None:
        """
        Reload ignored words from disk. This must be run from instances kept in memory before checking spelling.
        Otherwise, words removed from ignore list will not be updated in them.
        :return: None
        """
        self.lang = self._config_manager.get_spelling_lang()
        self.dict = enchant.Dict(self.lang)
        user_exclusion_list = Path(enchant.get_user_config_dir() / Path(self.lang)).with_suffix(
            Strings.extension_excl)
        self._ignore_words.clear()
        if user_exclusion_list.exists():
            with open(user_exclusion_list, 'r') as file:
                for line in file:
                    self.ignore_always(line.strip())

    def ignore_always(self, word: Optional[str] = None) -> None:
        """
        Overridden internal ignore method that also saves the words to disk.
        :param word: Word to ignore
        :return: None
        """
        if word is None:
            word = self.word
        word = self.coerce_string(word)
        if word not in self._ignore_words:
            self._ignore_words[word] = True

        # Save to disk into enchant exclusion list.
        enchant_dict = self.dict
        if not enchant_dict.is_removed(word):
            enchant_dict.remove(word)
