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
            '/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Resources/schema_article.xsd')
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
    files_articles = ['satelit-pro-wifi.html', 'dymovnice.html', 'htc-desire-hd-root.html', 'vakuova-pumpa.html',
                      'plasma-v-zavarovacce.html', 'joule-thief.html', 'desire-hd-mikrofon.html',
                      'usb-led-svitilna.html',
                      'optimalizace-2.html', 'zdroj-vysokeho-napeti.html', 'zdroj-vysokeho-napeti-jedna.html',
                      'oprava-notebooku.html', 'eten-flash-rom.html',
                      'aluminotermie.html', 'regulovatelny-zdroj.html', 'postrehy-z-pajeni.html',
                      'pen-e-pl6-makro-svetlo.html',
                      'usb-zesilovac-lm386.html', 'bramborove-delo.html', 'vyroba-plosnych-spoju.html',
                      'pulzni-motor.html',
                      'core.html', 'strelny-prach.html', 'eten-static-gps.html', 'tesluv-transformator.html',
                      'vibrator.html',
                      'point-clientcommand.html', 'zdroj-vysokeho-napeti-civka.html', 'pen-epl6-kabelova-spoust.html',
                      'optimalizace-0.html', 'rpi-ochrana-gpio.html', 'medvedi-led-svitilna.html',
                      'optimalizace-1.html',
                      'optimalizace.html']
    files_menu = ['elektro.html', 'chemie.html', 'hammer.html', 'lockpicking.html']
    for file in files_articles:
        document = os.path.join('/home/other/test_web_xml', file)
        print(validator.validate(document))
