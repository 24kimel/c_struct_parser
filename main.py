import logging
from dataclasses import dataclass
from lark import Lark, logger, Transformer
from pprint import pprint
from functools import partial

from typing import List, Union, Optional

GRAMMAR_FILE="c_struct.lark"
TEXT_FILE="structs.c"

class FilterError(Exception):
    ...

@dataclass
class ArrayInfo:
    length: Union[int, str]

@dataclass
class Field:
    name: str
    field_type: str
    array_info: Optional[ArrayInfo]

@dataclass
class FieldList:
    field_list: List[Field]

@dataclass
class Struct:
    name: str
    parent: str
    struct_id: int
    field_list: List[Field]

@dataclass
class Inheritance:
    parent: str

@dataclass
class StructId:
    struct_id: int

def is_instance_kw(obj, classinfo):
    return isinstance(obj, classinfo)

nothing = lambda *args: None
get_first_child = lambda self, l: l[0]
get_children = lambda self, l: l

def get_single_element_by_filter(_list, _filter):
    matches = list(filter(_filter, _list))
    if len(matches) != 1:
        return None
    return matches[0]

class StructTransformer(Transformer):
    INT = int
    WORD = str
    CNAME = str
    HEX_NUMBER = staticmethod(partial(int, base=16))
    field_list = FieldList
    field_type = get_first_child
    const_length = get_first_child
    var_length = get_first_child
    array_length = get_first_child
    start = get_children
    number = get_first_child

    ARRAY_INFO_LENGTH_IDX = 1
    def array_info(self, array_info):
        return ArrayInfo(array_info[self.ARRAY_INFO_LENGTH_IDX])

    STRUCT_ID_NUMBER_IDX = 1
    def struct_id(self, struct_id):
        return StructId(struct_id[self.STRUCT_ID_NUMBER_IDX])

    FIELD_NAME_IDX = 1
    FIELD_TYPE_IDX = 0
    def field(self, field):
        array_info = get_single_element_by_filter(field, partial(is_instance_kw, classinfo=ArrayInfo))
        return Field(name=field[self.FIELD_NAME_IDX], field_type=field[self.FIELD_TYPE_IDX], array_info=array_info)

    INHERITANCE_PARENT_NAME = 1
    def inheritance(self, inheritance):
        return Inheritance(inheritance[self.INHERITANCE_PARENT_NAME])

    STRUCT_NAME_IDX = 1
    def struct(self, struct):
        field_list = get_single_element_by_filter(struct, partial(is_instance_kw, classinfo=FieldList))
        struct_id = get_single_element_by_filter(struct, partial(is_instance_kw, classinfo=StructId))
        struct_id = struct_id.struct_id if struct_id is not None else 0
        inheritance_info = get_single_element_by_filter(struct, partial(is_instance_kw, classinfo=Inheritance))
        parent = inheritance_info.parent if inheritance_info is not None else ""
        return Struct(name=struct[self.STRUCT_NAME_IDX], field_list=field_list.field_list, parent=parent, struct_id=struct_id)

def main():
    logger.setLevel(logging.WARN)
    with open(GRAMMAR_FILE) as f:
        grammar = f.read()

    with open(TEXT_FILE) as f:
        text = f.read()

    p = Lark(grammar)
    tree = p.parse(text)
    output = StructTransformer().transform(tree)
    pprint(output)


if __name__ == "__main__":
    main()
