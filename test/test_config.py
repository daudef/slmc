import dataclasses
import typing

from slmc import config, item, layer


@dataclasses.dataclass
class Model:
    a: typing.Any
    b: typing.Any


@dataclasses.dataclass
class Layer(layer.DataSource[item.Items]):
    data: typing.Any

    def get_data(self):
        return item.list_items(self.data)


def test_config():
    assert config.read_config(Model, [Layer({'a': 1, 'b': 1}), Layer({'a': 2})]) == Model(2, 1)
    assert config.read_config(
        Model,
        [Layer({'a': 1, 'b': {'c': 1}}), Layer({'b': 2})],
        on_conflict=item.ConflictPolicy.OVERWRITE,
    ) == Model(1, 2)
