from flask import Response


class ContainsResponse(Response):
    """Allows to directly test `<HTML fragment> in response`."""

    def __contains__(self, needle):
        return needle in self.get_data(as_text=True)

    def contains_only_once(self, needle):
        response = self.get_data(as_text=True)
        return needle in response and response.count(needle) == 1
