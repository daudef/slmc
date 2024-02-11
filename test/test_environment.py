import enum
import os

import pytest

from slmc import environment


class Env(environment.Environment):
    A = enum.auto()
    B = enum.auto()


def test_valid_env():
    os.environ['ENV'] = 'a'
    assert Env.get_from_env('ENV') == Env.A
    os.environ['ENV'] = 'B'
    assert Env.get_from_env('ENV', default=Env.A) == Env.B


def test_default_env():
    os.environ['ENV'] = ''
    assert Env.get_from_env('ENV', default=Env.A) == Env.A
    os.environ['ENV'] = 'C'
    assert Env.get_from_env('ENV', default=Env.B, ignore_invalid=True) == Env.B


def test_invalid_env():
    os.environ['ENV'] = 'C'
    with pytest.raises(environment.InvalidValueError):
        Env.get_from_env('ENV')

    os.environ['ENV'] = 'C'
    with pytest.raises(environment.NoEnvironmentError):
        Env.get_from_env('ENV', ignore_invalid=True)

    os.environ['ENV'] = ''
    with pytest.raises(environment.NoEnvironmentError):
        Env.get_from_env('ENV')
