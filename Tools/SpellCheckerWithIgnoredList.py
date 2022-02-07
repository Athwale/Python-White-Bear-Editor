from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter
import os

from Constants.Constants import Strings


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
        # Load ignored words.
        self._ignored_words = set()
        if os.path.exists(Strings.ignored_words_file):
            with open(Strings.ignored_words_file, 'r') as file:
                for line in file:
                    self._ignored_words.add(line.strip())
        for word in self._ignored_words:
            self.ignore_always(word)

    def save_ignored_word(self, word: str) -> None:
        """
        Append another ignored word to the ignored words file and add it to the internal ignore list.
        :param word: The word to ignore.
        :return: None
        """
        self.ignore_always(word)
        self._ignored_words.add(word)
        with open(Strings.ignored_words_file, 'w') as file:
            for word in self._ignored_words:
                file.write(word + '\n')
