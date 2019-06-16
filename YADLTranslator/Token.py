from enum import Enum

class Token(object):
    """Class that stores date about YADL token"""
    def __init__(self, type, val:str, line:int, pos:int):
        self.type = type
        self.value = val
        self.line = line
        self.pos = pos


class TokenType(Enum):
    """Enum with types of YADL Tokens"""
    IDENTIFIER = 1
    KEYWORD = 2
    NUMBER = 3                      # 5   -5   125
    O_FIGURE_BRACKET = 4            # {
    C_FIGURE_BRACKET = 5            # }
    O_ROUND_BRACKET = 6             # (
    C_ROUND_BRACKET = 7             # )
    ASSIGN = 8                      # =
    GREATER = 9                     # >
    GREATER_EQUAL = 10              # >=
    LESS = 11                       # <
    LESS_EQUAL = 12                 # <=
    EQUAL = 13                      # ==
    SEMICOLON = 14                  # ;
    ACCESS = 15                     # .