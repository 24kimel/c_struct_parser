import logging
from dataclasses import dataclass
from lark import Lark, logger, Transformer
from pprint import pprint

from typing import List

GRAMMAR_FILE="c_struct.lark"
TEXT_FILE="structs.c"

@dataclass
class Field:
    name: str
    field_type: str
    is_array: bool
    array_length: str

@dataclass
class Struct:
    name: str
    field_list: List[Field]

nothing = lambda *args: None
get_first_child = lambda self, l: l[0]
get_children = lambda self, l: l

class MyTransformer(Transformer):
    INT = int
    WORD = str
    field_list = get_children
    name = get_first_child
    field_type = get_first_child
    const_length = get_first_child
    var_length = get_first_child
    single_field = get_children
    array_field = get_children
    array_length = get_first_child
    SEMICOLON = nothing
    OSQUARE = nothing
    CSQUARE = nothing
    OCURLY = nothing
    CCURLY = nothing
    STRUCT_KEYWORD = nothing
    start = get_children


    FIELD_ARRAY_NUM_CHILDREN = 5
    FIELD_ARRAY_LENGTH_IDX = 3
    FIELD_NAME_IDX = 1
    FIELD_TYPE_IDX = 0

    def field(self, field):
        field_contents = field[0]
        is_array = len(field_contents) == self.FIELD_ARRAY_NUM_CHILDREN
        array_length = field_contents[self.FIELD_ARRAY_LENGTH_IDX] if is_array else ""
        return Field(name=field_contents[self.FIELD_NAME_IDX], field_type=field_contents[self.FIELD_TYPE_IDX], is_array=is_array, array_length=array_length)

    STRUCT_NAME_IDX = 1
    STRUCT_FIELD_LIST_IDX = 3

    def struct(self, struct):
        return Struct(name=struct[self.STRUCT_NAME_IDX], field_list=struct[self.STRUCT_FIELD_LIST_IDX])

def main():
    logger.setLevel(logging.WARN)
    with open(GRAMMAR_FILE) as f:
        grammar = f.read()

    with open(TEXT_FILE) as f:
        text = f.read()

    p = Lark(grammar)
    tree = p.parse(text)
    output = MyTransformer().transform(tree)
    pprint(output)


if __name__ == "__main__":
    main()
