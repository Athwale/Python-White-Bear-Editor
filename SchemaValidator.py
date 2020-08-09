import os

from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError


class SchemaValidator:
    """

    """

    def __init__(self):
        """
        XML schema validator constructor
        """
        xmlschema_parsed = etree.parse(
            '/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Resources/main_page.xsd')
        self.xmlschema = etree.XMLSchema(xmlschema_parsed)

    def validate(self, html_file: str) -> bool:
        """

        :param html_file:
        :return:
        """
        try:
            xml_doc = html.parse(html_file)
            result = self.xmlschema.validate(xml_doc)
            print(self.xmlschema.error_log)
            return result
        except XMLSyntaxError as e:
            print(e)
            return False


if __name__ == '__main__':
    validator = SchemaValidator()
    document = os.path.join('/home/other/test_web_xml', 'regulovatelny-zdroj.html')
    print(validator.validate(document))
