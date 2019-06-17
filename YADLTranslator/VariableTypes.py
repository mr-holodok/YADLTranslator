from enum import Enum


class LValueType(Enum):
    VARIABLE = 1                    # var
    VARIABLE_OF_CURRENT_CLASS = 2   # this.var
    OBJECT_WITH_INT_VARIABLE = 3    # obj.var


class LValue(object):
    """Represents left value in expression. Left value can be: local int variable,
    local variable of another type, class variable (with <this> keyword) or 
    object variable"""
    def __init__(self, name:str, type:str, ltype:LValueType):
        self.varName = name
        self.varType = type
        self.childVarName = ''
        self.lvalueType = ltype
        self.codeWithAddressInEBX = ''


class RValueType(Enum):
    VARIABLE = 1                    # var
    VARIABLE_OF_CURRENT_CLASS = 2   # this.var
    OBJECT_WITH_INT_VARIABLE = 3    # obj.var
    NUMBER = 4                      # 123


class RValue(object):
    """Represent right value in expression"""
    def __init__(self, name:str, type:str, rtype:RValueType):
        self.varName = name
        self.varType = type
        self.childVarName = ''
        self.rvalueType = rtype
        self.codeWithAddressOrValueInEAX = ''
        # int type contain value, other types - address (reference)