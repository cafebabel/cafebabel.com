from flask import Response


class ContainsResponse(Response):
    """Allows to directly test `<HTML fragment> in response`."""

    def __contains__(response, needle):
        return needle in response.get_data(as_text=True)
