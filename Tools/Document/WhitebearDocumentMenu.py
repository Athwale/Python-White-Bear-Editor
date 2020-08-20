from typing import List

from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

from Constants.Strings import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Resources.Fetch import Fetch
from Tools.Document.WhitebearDocument import WhitebearDocument


class WhitebearDocumentMenu(WhitebearDocument):
    """
    This class represents a menu file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name, path):
        """
        Create a new WhitebearDocumentMenuIndex object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        """
        # File properties are in base class
        super().__init__(name, path, None)

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # Only parse if not parsed already and only if the document is valid.
        if not self._parsed_html and self.is_valid():
            pass

    def validate_self(self) -> (bool, List[str]):
        """
        Validate this document against the menu xml schema.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails
        """
        errors = []
        try:
            xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path('schema_menu.xsd')))
            xml_doc = html.parse(self.get_path())
            self._valid = xmlschema.validate(xml_doc)
        except XMLSyntaxError as e:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + str(e))
        for error in xmlschema.error_log:
            errors.append(error.message)
        return self._valid, errors

    # Getters ----------------------------------------------------------------------------------------------------------

    # Setters ----------------------------------------------------------------------------------------------------------
