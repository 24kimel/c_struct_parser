import logging
from dataclasses import dataclass
from lark import Lark, logger, Transformer
from pprint import pprint

from typing import List, Union

GRAMMAR_FILE="c_struct.lark"
TEXT_FILE="structs.c"

@dataclass
class Field:
    name: str
    field_type: str
    is_array: bool
    array_length: str

@dataclass
class FieldList:
    field_list: List[Field]

@dataclass
class Struct:
    name: str
    parent: str
    field_list: List[Field]

@dataclass
class Inheritance:
    parent: str

@dataclass
class ArrayInfo:
    length: Union[int, str]

nothing = lambda *args: None
get_first_child = lambda self, l: l[0]
get_children = lambda self, l: l

class StructTransformer(Transformer):
    INT = int
    WORD = str
    CNAME = str
    field_list = FieldList
    field_type = get_first_child
    const_length = get_first_child
    var_length = get_first_child
    array_length = get_first_child
    start = get_children

    ARRAY_INFO_LENGTH_IDX = 1
    def array_info(self, array_info):
        return ArrayInfo(array_info[self.ARRAY_INFO_LENGTH_IDX])

    FIELD_NAME_IDX = 1
    FIELD_TYPE_IDX = 0
    def field(self, field):
        print(field)
        array_info_list = [c for c in field if isinstance(c, ArrayInfo)]
        is_array = len(array_info_list) > 0
        array_length = array_info_list[0].length if is_array else ""
        return Field(name=field[self.FIELD_NAME_IDX], field_type=field[self.FIELD_TYPE_IDX], is_array=is_array, array_length=array_length)

    INHERITANCE_PARENT_NAME = 1
    def inheritance(self, inheritance):
        return Inheritance(inheritance[self.INHERITANCE_PARENT_NAME])

    STRUCT_NAME_IDX = 1
    STRUCT_FIELD_LIST_IDX = 3

    def struct(self, struct):
        field_list = [c for c in struct if isinstance(c, FieldList)][0]
        inheritance_list = [c for c in struct if isinstance(c, Inheritance)]
        parent = [c for c in struct if isinstance(c, Inheritance)][0].parent if len(inheritance_list) > 0 else ""
        return Struct(name=struct[self.STRUCT_NAME_IDX], field_list=field_list.field_list, parent=parent)

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
