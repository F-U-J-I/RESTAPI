from bs4 import BeautifulSoup


class Parser:

    def __init__(self, obj):
        self.obj = obj
        self.s = self.get_content(obj)

        self.str_list = self.get_str_list()
        self.index_str_list = 0

        self.tag_list = self.get_tag_list()
        self.index_tag_list = 0

    @staticmethod
    def get_content(obj):
        str_obj = str(obj)
        left = len(obj.name) + 2
        right = len(str_obj) - len(obj.name) - 3
        return str_obj[left:right]

    def get_str_list(self):
        len_s = len(self.s)
        content = []
        text = ''

        tag = ''
        fill_tag = False
        tag_list = []
        is_head_tag = False
        is_close_tag = False
        for i in range(len_s):
            if self.s[i] == '<':
                if not fill_tag and not tag_list:
                    content.append(text)
                    text = ''
                is_head_tag = True
                fill_tag = True
                continue

            if is_head_tag or is_close_tag:
                if self.s[i] == '/':
                    is_close_tag = True
                    is_head_tag = False
                    continue
                if self.s[i] == '>':
                    if self.s[i - 1] != '/':
                        if is_close_tag:
                            tag_list.remove(tag)
                        else:
                            tag_list.append(tag)
                    tag = ''
                    is_head_tag = False
                    is_close_tag = False
                    fill_tag = False

                    if not tag_list:
                        content.append('')
                    continue
                else:
                    if self.s[i] == ' ':
                        fill_tag = False
                    if fill_tag:
                        tag += self.s[i]
            else:
                if not fill_tag and not tag_list:
                    text += self.s[i]

        content.append(text)
        return content[1:]

    def get_tag_list(self):
        text = ''
        content = []
        tag = ''
        tag_list = []
        is_head_tag = False
        is_close_tag = False

        len_s = len(self.s)
        for i in range(len_s):
            if self.s[i] == '<':
                is_head_tag = True

            if tag_list or is_head_tag:
                text += self.s[i]

            if is_head_tag or is_close_tag:
                if self.s[i] == '/' and (self.s[i + 1] == '>' or self.s[i - 1] == '<'):
                    is_close_tag = True
                    is_head_tag = False
                    continue
                if self.s[i] == '>':
                    if self.s[i - 1] != '/':
                        if is_close_tag:
                            tag_list.remove(tag)
                        else:
                            tag_list.append(tag)
                    else:
                        text += self.s[i]

                    if is_close_tag:
                        if not tag_list:
                            content.append(BeautifulSoup(text, "html.parser"))
                            text = ''
                    tag = ''
                    is_head_tag = False
                    is_close_tag = False
                else:
                    tag += self.s[i]
        return content

    @staticmethod
    def find(arr, index):
        if index == len(arr):
            return None, index
        return arr[index], index + 1

    def find_tag_list(self):
        if self.index_tag_list == len(self.tag_list):
            return None
        self.index_tag_list += 1
        return self.tag_list[self.index_tag_list - 1]

    def find_str_list(self):
        element, self.index_str_list = self.find(self.str_list, self.index_str_list)
        return element

