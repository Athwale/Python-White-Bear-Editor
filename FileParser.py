from Exceptions.WrongFormatException import WrongFormatException
from ParsedFile import ParsedFile
from Strings.Strings import Strings


class FileParser:
    """
    """

    @staticmethod
    def parse_file(html_file_object):
        """

        :param html_file_object:
        :return:
        """
        title = None
        keywords = None
        description = None
        parsed = html_file_object.get_parsed_html()

        if html_file_object.get_type() != ParsedFile.TYPE_OTHER:
            # Set title
            if len(parsed.find_all('title')) != 1:
                raise WrongFormatException(Strings.exception_only_one_title_allowed + " " + html_file_object.get_name())
            else:
                # Finds first occurrence, but there is only one anyway
                title = parsed.title.string

            # Set description
            meta_tags = parsed.find_all('meta')
            for tag in meta_tags:
                try:
                    if tag['name'] == 'description':
                        description = tag['content']
                except KeyError:
                    continue
            # No description found
            if description is None:
                raise WrongFormatException(Strings.exception_meta_description_twice + " " + html_file_object.get_name())

        html_file_object.set_title(title)
        html_file_object.set_description(description)
        html_file_object.set_keywords(keywords)
