import dataclasses
import enum
import typing

type Value = typing.Any

type ValueTree = dict[str, ValueTree] | Value
type Path = typing.Collection[str]
type Items = typing.Iterable[Item]


@dataclasses.dataclass
class Item:
    path: Path
    value: Value


class ConflictPolicy(enum.Enum):
    KEEP = enum.auto()
    OVERWRITE = enum.auto()
    NEST = enum.auto()
    TRIM = enum.auto()
    RAISE = enum.auto()


@dataclasses.dataclass
class Conflict:
    existing: ValueTree
    new: Item


@dataclasses.dataclass
class ConflictError(Exception):
    conflict: Conflict


def list_items(tree: ValueTree) -> Items:
    if not isinstance(tree, dict):
        return [Item([], tree)]

    items: list[Item] = []
    for k, v in tree.items():
        items.extend(Item([k, *i.path], i.value) for i in list_items(v))
    return items


def should_overwrite(conflict: Conflict, on_conflict: ConflictPolicy | None):
    match on_conflict:
        case ConflictPolicy.KEEP:
            return False
        case ConflictPolicy.OVERWRITE:
            return True
        case ConflictPolicy.NEST:
            return len(conflict.new.path) > 0
        case ConflictPolicy.TRIM:
            return len(conflict.new.path) == 0
        case _:
            raise ConflictError(conflict)


def set_item(tree: ValueTree, item: Item, on_conflict: ConflictPolicy | None) -> ValueTree:
    if len(item.path) == 0:
        if (
            not isinstance(tree, dict)
            or len(tree) == 0
            or should_overwrite(Conflict(tree, item), on_conflict)
        ):
            return item.value
        return tree

    if not isinstance(tree, dict):
        if not should_overwrite(Conflict(tree, item), on_conflict):
            return tree
        tree = {}

    key, *path = item.path

    try:
        tree[key] = set_item(tree.get(key, {}), Item(path, value=item.value), on_conflict)
    except ConflictError as e:
        e.add_note(f'at {key}')
        raise

    return tree
