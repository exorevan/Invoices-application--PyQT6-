import typing as ty

from conf import config


class Handler:
    _handler_name: str | None = None

    @property
    def handler_name(self) -> str | None:
        if self._handler_name:
            return self._handler_name

        self._handler_name = "Untitled Handler"
        self._raise_error(txt=f"No handler name")

    @handler_name.setter
    def handler_name(self, handler_name: str) -> None:
        if len(str(handler_name)) < config.MAX_TEXT_LENGTH_TO_PRINT:
            self._handler_name = handler_name
            return

        self._raise_error(txt=f"Too long handler's name (len = '{len(handler_name)}')")

    def _raise_error(self, txt: str) -> ty.NoReturn:
        print(f"\nPlace: {self.handler_name}")
        print(f"- Fatal error: {txt}")
        quit()
