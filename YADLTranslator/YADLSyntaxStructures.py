class YADLMethodData(object):
    """Class that holds data about class method"""
    def __init__(self, name, paramType, paramName):
        self.name = name
        self.paramType = paramType
        self.paramName = paramName


class YADLClassData(object):
    """Represent structure of YADS class and saves data about defined 
    methods and variables"""

    def __init__(self, className:str):
        self.name = className
        self.vars = list()
        self.methods = list()


    def AddVar(self, varName:str):
        self.vars.append(varName)

    def IsVarInList(self, varName:str) -> bool :
        if varName in self.vars:
            return True
        return False

    def AddMethod(self, method):
        self.methods.append(method)

    def FindMethodInList(self, methodName:str) -> YADLMethodData:
        for method in self.methods:
            if method.name == methodName:
                return method
        return None