"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values. The text file has the following format:

    [First line] A dictionary describing the environment
    [n-th line] The n-th instruction in our program.

As an example, the program below sums up the numbers a, b and c:

    {"a": 1, "b": 3, "c": 5}
    x = add a b
    x = add x c
"""

from lang import *


def line2env(line: str) -> Env:
    """
    Maps a string (the line) to a dictionary in python. This function will be
    useful to read the first line of the text file. This line contains the
    initial environment of the program that will be created. If you don't like
    the function, feel free to drop it off.

    Example
        >>> line2env('{"zero": 0, "one": 1, "three": 3, "iter": 9}').get('one')
        1
    """
    import json

    env_dict = json.loads(line)
    env_lang = Env()
    for k, v in env_dict.items():
        env_lang.set(k, v)
    return env_lang

from enum import Enum
from typing import List, Tuple, Dict

class Token(Enum):
    EQUAL = 0,
    ID = 1,
    ADD = 2,
    MUL = 3,
    LTH = 4,
    GEQ = 5,
    BT = 6,
    NUMBER = 7,
    ENDL = 8,

keywords = {
        "add": Token.ADD,
        "mul": Token.MUL,
        "lth": Token.LTH,
        "geq": Token.GEQ,
        "bt": Token.BT,
        }

class ScannedToken:
    token_type: Token
    lexeme: str
    line: int

    def __init__(s, token_type: Token, lexeme: str, line: int):
        super().__init__()
        s.token_type = token_type
        s.lexeme = lexeme
        s.line = line

class Error(Exception):
    def __init__(self, message: str, line: int, where: str):
        super().__init__(f"Error {where} line {line}: {message}")

def scan_tokens(lines: List[str]) -> List[ScannedToken]:
    tokens = []
    
    for line_no, line_text in enumerate(lines, start = 1):
        i = 0

        while i < len(line_text):
            char = line_text[i]

            if char.isspace():
                i += 1
                continue
            if char == '=':
                tokens.append(ScannedToken(Token.EQUAL, "=", line_no))
                i += 1
                continue

            start = i
            while i < len(line_text) and not line_text[i].isspace() and line_text[i] != '=':
                i += 1
            lexeme = line_text[start:i]

            if lexeme.isalpha():
                token_type = keywords.get(lexeme, Token.ID)
            elif lexeme.isdigit():
                token_type = Token.NUMBER
            else:
                raise Error(f"Invalid token: {lexeme}", line_no, "Scanner")
            tokens.append(ScannedToken(token_type, lexeme, line_no))
        tokens.append(ScannedToken(Token.ENDL, "",line_no))

    return tokens

def split_lines(tokens: List[ScannedToken]) -> List[List[ScannedToken]]:
    lines: List[List[ScannedToken]] = []
    current: List[ScannedToken] = []

    for token in tokens:
        if token.token_type == Token.ENDL:
            lines.append(current)
            current = []
        else:
            current.append(token)

    return lines

def parse_assign(line_tokens: List[ScannedToken], line_no: int) -> Inst:
    if len(line_tokens) != 5:
        raise Error("Expected format: ID = OP ID ID", line_no, "Parser")

    dest, equal, op, arg1, arg2 = line_tokens

    if equal.token_type != Token.EQUAL:
        raise Error("Expected '=' after ID", line_no, "Parser")

    if arg1.token_type != Token.ID or arg2.token_type != Token.ID:
        raise Error("Operation argument must be IDs", line_no, "Parser")

    if op.token_type == Token.ADD:
        return Add(dest.lexeme, arg1.lexeme, arg2.lexeme)
    elif op.token_type == Token.MUL:
        return Mul(dest.lexeme, arg1.lexeme, arg2.lexeme)
    elif op.token_type == Token.LTH:
        return Lth(dest.lexeme, arg1.lexeme, arg2.lexeme)
    elif op.token_type == Token.GEQ:
        return Geq(dest.lexeme, arg1.lexeme, arg2.lexeme)
    else:
        raise Error("Unsupported op: {}".format(op.lexeme), line_no, "Parser")

def parse_bt(line_tokens: List[ScannedToken], line_no: int) -> Tuple[Bt, int]:
    if len(line_tokens) != 3:
        raise Error("Expected format: bt ID NUMBER", line_no, "Parser")
    
    bt, cond, jline = line_tokens

    if cond.token_type != Token.ID:
        raise Error("Expected ID after bt", line_no, "Parser")

    if jline.token_type != Token.NUMBER:
        raise Error("Expected NUMBER after ID", line_no, "Parser")
    return Bt(cond.lexeme), int(jline.lexeme)

def line2instr(tokens: List[ScannedToken]) -> Tuple[List[Inst], Dict[int, int]]:
    instructions = []
    bt_target = {}

    for line_idx, line_tokens in enumerate(split_lines(tokens)):
        if not line_tokens:
            continue

        first = line_tokens[0]

        if first.token_type == Token.BT:
            bt, target_line = parse_bt(line_tokens, line_idx)
            bt_target[len(instructions)] = target_line
            instructions.append(bt)

        elif first.token_type == Token.ID:
            instructions.append(parse_assign(line_tokens, line_idx))

        else:
            raise Error("Instructions must begin with bt or ID", line_idx, "Parser")

    return instructions, bt_target

def link_inst(tokens: List[Inst], bt_target: Dict[int, int]):
    for i, token in enumerate(tokens):
        if isinstance(token, Bt):
            j_line = bt_target[i]

            if j_line >= len(tokens):
                raise Error("Index of BT must be in range of instructions", i, "Parser")

            token.add_true_next(tokens[j_line])

        if i + 1 < len(tokens):
            token.add_next(tokens[i + 1])

def file2cfg_and_env(lines: List[str]) -> Tuple[Env, List[Inst]]:
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.

    Example:
        >>> l0 = '{"a": 0, "b": 3}'
        >>> l1 = 'bt a 1'
        >>> l2 = 'x = add a b'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        3

        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> env, prog = file2cfg_and_env([l0, l1, l2, l3])
        >>> interp(prog[0], env).get("x")
        42

        >>> l0 = '{"a": 1, "b": 3, "c": 5}'
        >>> l1 = 'x = add a b'
        >>> l2 = 'x = add x c'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        9
    """
    env = line2env(lines[0])
    tokens = scan_tokens(lines[1:])
    insts, bt_target = line2instr(tokens)
    link_inst(insts, bt_target)
    return (env, insts)