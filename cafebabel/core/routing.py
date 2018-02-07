from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class LangConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(LangConverter, self).__init__(url_map)
        self.regex = '[a-z]{2}'
