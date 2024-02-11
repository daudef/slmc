import abc
import dataclasses
import os
import pathlib
import typing

from slmc import item

type Transformer[T, S] = typing.Callable[[T], S]
type Layer = DataSource[item.Items]


class DataSource[T](abc.ABC):
    @abc.abstractmethod
    def get_data(self) -> T:
        ...

    def __or__[S](self, o: Transformer[T, S]):
        return TransformedDataSource(self, o)


@dataclasses.dataclass
class TransformedDataSource[T, S](DataSource[S]):
    source: DataSource[T]
    transformer: Transformer[T, S]

    def get_data(self):
        return self.transformer(self.source.get_data())


###


@dataclasses.dataclass
class File(DataSource[bytes]):
    path: pathlib.Path
    optional: bool = False

    def get_data(self):
        try:
            return self.path.read_bytes()
        except FileNotFoundError:
            if self.optional:
                return b''
            raise


def make_file_layer(
    path: pathlib.Path, parser: Transformer[bytes, item.ValueTree], *, optional: bool = False
) -> DataSource[item.Items]:
    return File(path, optional) | parser | item.list_items


@dataclasses.dataclass
class EnvironmentVariablesSource(DataSource[item.Items]):
    prefix: str
    nested_delimiter: str
    case_sensitive: bool = False

    def get_data(self):
        prefix = self.prefix
        nested_delimiter = self.nested_delimiter
        if self.case_sensitive:
            prefix = prefix.lower()
            nested_delimiter = nested_delimiter.lower()
        for var_name, value in os.environ.items():
            if not self.case_sensitive:
                var_name = var_name.lower()
            if var_name.startswith(self.prefix):
                path = var_name.removeprefix(self.prefix).split(self.nested_delimiter)
                yield item.Item(path, value)
