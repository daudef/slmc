import pytest

from slmc.item import ConflictError, ConflictPolicy, Item, list_items, set_item


def test_list_items():
    assert list_items({}) == []
    assert list_items(tree=True) == [Item([], value=True)]
    assert list_items({'a': True, 'b': None, 'c': False}) == [
        Item(['a'], value=True),
        Item(['b'], value=None),
        Item(['c'], value=False),
    ]
    assert list_items({'a': True, 'b': {'c': True, 'd': None, 'e': {'f': True}}}) == [
        Item(['a'], value=True),
        Item(['b', 'c'], value=True),
        Item(['b', 'd'], value=None),
        Item(['b', 'e', 'f'], value=True),
    ]
    assert list_items({'a': {'b': {'c': {'d': []}}}}) == [Item(['a', 'b', 'c', 'd'], value=[])]


def test_set_items_no_conflict():
    policy = None
    assert set_item({}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({}, Item(['a', 'b', 'c'], 1), policy) == {'a': {'b': {'c': 1}}}
    assert set_item({}, Item([], 1), policy) == 1
    assert set_item({'a': 1}, Item(['a'], 2), policy) == {'a': 2}
    assert set_item({'a': 1}, Item(['b'], 2), policy) == {'a': 1, 'b': 2}
    assert set_item({'a': 1}, Item(['b', 'c'], 2), policy) == {'a': 1, 'b': {'c': 2}}
    assert set_item({'a': {'b': 1}}, Item(['a', 'b'], 2), policy) == {'a': {'b': 2}}
    assert set_item({'a': {'b': 1}}, Item(['a', 'c'], 2), policy) == {'a': {'b': 1, 'c': 2}}
    assert set_item(1, Item([], 2), policy) == 2


def test_set_items_keep():
    policy = ConflictPolicy.KEEP
    assert set_item({}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({'a': 1}, Item([], 1), policy) == {'a': 1}
    assert set_item({'a': {'b': 1}}, Item(['a'], 1), policy) == {'a': {'b': 1}}
    assert set_item(1, Item(['a'], 1), policy) == 1
    assert set_item({'a': 1}, Item(['a', 'b'], 1), policy) == {'a': 1}


def test_set_items_overwrite():
    policy = ConflictPolicy.OVERWRITE
    assert set_item({}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({'a': 1}, Item([], 1), policy) == 1
    assert set_item({'a': {'b': 1}}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item(1, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({'a': 1}, Item(['a', 'b'], 1), policy) == {'a': {'b': 1}}


def test_set_items_nest():
    policy = ConflictPolicy.NEST
    assert set_item({}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({'a': 1}, Item([], 1), policy) == {'a': 1}
    assert set_item({'a': {'b': 1}}, Item(['a'], 1), policy) == {'a': {'b': 1}}
    assert set_item(1, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({'a': 1}, Item(['a', 'b'], 1), policy) == {'a': {'b': 1}}


def test_set_items_trim():
    policy = ConflictPolicy.TRIM
    assert set_item({}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item({'a': 1}, Item([], 1), policy) == 1
    assert set_item({'a': {'b': 1}}, Item(['a'], 1), policy) == {'a': 1}
    assert set_item(1, Item(['a'], 1), policy) == 1
    assert set_item({'a': 1}, Item(['a', 'b'], 1), policy) == {'a': 1}


def test_set_items_raise():
    policy = ConflictPolicy.RAISE
    assert set_item({}, Item(['a'], 1), policy) == {'a': 1}

    with pytest.raises(ConflictError) as e:
        set_item({'a': 1}, Item([], 1), policy)
    assert e.value.conflict.new == Item([], 1)
    assert e.value.conflict.existing == {'a': 1}

    with pytest.raises(ConflictError) as e:
        set_item({'a': {'b': 1}}, Item(['a'], 1), policy)
    assert e.value.conflict.new == Item([], 1)
    assert e.value.conflict.existing == {'b': 1}

    with pytest.raises(ConflictError) as e:
        set_item(1, Item(['a'], 1), policy)
    assert e.value.conflict.new == Item(['a'], 1)
    assert e.value.conflict.existing == 1

    with pytest.raises(ConflictError) as e:
        set_item({'a': 1}, Item(['a', 'b'], 1), policy)
    assert e.value.conflict.new == Item(['b'], 1)
    assert e.value.conflict.existing == 1
