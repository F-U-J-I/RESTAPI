from bs4 import BeautifulSoup, NavigableString

from .core.parser import Parser


class ParseHtml:
    HEADER_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    PARAGRAPH_TAG = 'p'
    IMAGE_TAG = 'img'
    STYLE_TAG = 'style'

    def __init__(self, html):
        self.html = BeautifulSoup(html, "html.parser")
        self.data = []

    @staticmethod
    def parse_style(styles):
        data = {}
        for style in styles.split(';'):
            if style:
                item = style.split(':')
                data[item[0].strip()] = item[1].strip()
        return data

    def parse_obj(self, obj):
        data = {}
        if type(obj) == str:
            data['text'] = obj

        else:
            data['tag'] = obj.name
            if obj.name == self.IMAGE_TAG:
                data['src'] = obj['src']
            else:
                if obj.name == self.PARAGRAPH_TAG and 'style' in obj.attrs:
                    data['style'] = {}
                    for (key, value) in self.parse_style(obj['style']).items():
                        data['style'][key] = value

                parser = Parser(obj)
                if parser.tag_list:
                    data['content'] = []
                    for s in parser.str_list:
                        if s == '':
                            tag_list_element = parser.find_tag_list()
                            if tag_list_element is not None:
                                data['content'].append(self.parse_obj(tag_list_element.find()))
                        else:
                            data['content'].append({
                                'text': s
                            })
                    if parser.index_tag_list + 1 < len(parser.tag_list):
                        for i in range(parser.index_tag_list, len(parser.tag_list)):
                            data['content'].append(self.parse_obj(parser.tag_list[i].find()))
                else:
                    text = obj.get_text()
                    if text is not None:
                        data['text'] = text

        return data

    def parse(self):
        for tag in self.html:
            if type(tag) != NavigableString:
                self.data.append(self.parse_obj(tag))
        return self.data
