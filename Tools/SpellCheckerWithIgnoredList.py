from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter
import os

from Constants.Constants import Strings


class SpellCheckerWithIgnoreList(SpellChecker):
    """
    Subclass of SpellChecker that maintains a permanent list of ignored words.
    """

    _IGNORED_WORDS = set()

    def __init__(self, lang: str):
        """
        Constructor for spellchecker with EmailFilter, URLFilter and ignore list built in.
        :param lang: Spelling language.
        """
        super().__init__(lang, filters=[EmailFilter, URLFilter])
        return

        # Load ignored words.
        if os.path.exists(Strings.ignored_words_file):
            with open(Strings.ignored_words_file, 'r') as file:
                for line in file:
                    SpellCheckerWithIgnoreList._IGNORED_WORDS.add(line.strip())
        for word in SpellCheckerWithIgnoreList._IGNORED_WORDS:
            self.ignore_always(word)

    def reload_ignored(self) -> None:
        """
        Reload ignored words from the internal class wide variable. This must be run from instances that are kept in
        memory before checking spelling.
        :return: None
        """
        for word in SpellCheckerWithIgnoreList._IGNORED_WORDS:
            self.ignore_always(word)

    def save_ignored_word(self, word: str) -> None:
        """
        Append another ignored word to the ignored words file and add it to the internal ignore list.
        :param word: The word to ignore.
        :return: None
        """
        self.ignore_always(word)
        enchant_dict = self.dict
        if not enchant_dict.is_removed(word):
            enchant_dict.remove(word)
