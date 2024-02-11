import enum
import os
import typing


class InvalidValueError(Exception):
    pass


class NoEnvironmentError(Exception):
    pass


class Environment(enum.Enum):
    @classmethod
    def get_from_env(
        cls, var_name: str, *, default: typing.Self | None = None, ignore_invalid: bool = False
    ) -> typing.Self:
        value = os.environ.get(var_name)
        if value:
            for self in cls:
                if self.name.lower() == value.lower():
                    return self

            missing_reason = (
                f"The value '{value}' for environment variable '{var_name}' is invalid, "
                f"possible choices are '{', '.join(s.name for s in cls)}"
            )
            if not ignore_invalid:
                raise InvalidValueError(missing_reason)
        else:
            missing_reason = f"Environment variable '{var_name}' is not defined"

        if default is not None:
            return default

        message = f'{missing_reason} and not default value was provided'
        raise NoEnvironmentError(message)
