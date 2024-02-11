import contextlib
import json
import os
import pathlib
import uuid

import pytest

from slmc import item, layer


def make_path(name: str):
    return pathlib.Path(f'{name}.txt')


@contextlib.contextmanager
def tmp_file(content: bytes):
    path = make_path(str(uuid.uuid4()))
    try:
        path.write_bytes(content)
        yield path
    finally:
        path.unlink(missing_ok=True)


def test_file():
    with tmp_file(content := b'abc') as path:
        file = layer.File(path, optional=False)
        assert file.get_data() == content


def test_optional_file():
    file = layer.File(make_path('does_not_exists'), optional=True)
    assert file.get_data() == b''


def test_missing_file():
    file = layer.File(make_path('does_not_exists_2'), optional=False)
    with pytest.raises(FileNotFoundError):
        file.get_data()


def test_json_file():
    with tmp_file(b'{"a": 1, "b": {"c": null}}') as path:
        assert list(layer.make_file_layer(path, json.loads).get_data()) == [
            item.Item(['a'], 1),
            item.Item(['b', 'c'], None),
        ]


def test_env_layer_ci():
    os.environ['T_A'] = '1'
    os.environ['T_B_C'] = '2'
    os.environ['T_B_D'] = '3'
    layer_ = layer.EnvironmentVariablesSource(
        prefix='t_', nested_delimiter='_', case_sensitive=False
    )
    assert list(layer_.get_data()) == [
        item.Item(['a'], '1'),
        item.Item(['b', 'c'], '2'),
        item.Item(['b', 'd'], '3'),
    ]


def test_env_layer_cs():
    os.environ['T'] = '1'
    os.environ['t_A_O_b'] = '2'  # noqa: SIM112
    os.environ['t_A_o_b'] = '3'  # noqa: SIM112
    layer_ = layer.EnvironmentVariablesSource(
        prefix='t_', nested_delimiter='_o_', case_sensitive=True
    )
    assert list(layer_.get_data()) == [item.Item(['A_O_b'], '2'), item.Item(['A', 'b'], '3')]
