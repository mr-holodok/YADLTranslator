class SymbolData(object):
    """Class that hold data about local symbol that stored in SymbolTable"""
    def __init__(self, name:str, type:str):
        self.name = name
        self.type = type


class SymbolTable(object):
    """Class that represent symbol table that contains data about local variables
    such as name and type. This type is used for method scope. Also it supports
    double linked list symbol tables for situations when method has another built 
    in scope such as cycles or if-statements """
    def __init__(self):
        self.symbolsData = list()
        self.nextScopeTable = None
        self.prevTable = None
        self.paramSymbol = None
        

    def AddSymbol(self, s:SymbolData):
        lastTable = self.GetLastTable()
        lastTable.symbolsData.append(s)


    def AddParamSymbol(self, s:SymbolData):
        self.paramSymbol = s


    def AddNewScopeTable(self):
        lastTable = self.GetLastTable()
        lastTable.nextScopeTable = SymbolTable()
        lastTable.nextScopeTable.prevTable = lastTable


    def RemoveLastScopeTable(self):
        lastTable = self.GetLastTable()
        lastTable.prevTable.nextScopeTable = None
        lastTable.prevTable = None
        del lastTable


    def GetLastTable(self):
        lastTable = self
        while lastTable.nextScopeTable != None:
            lastTable = lastTable.nextScopeTable
        return lastTable


    def FindSymbolInLastTable(self, name:str) -> SymbolData:
        lastTable = self.GetLastTable()
        if lastTable.paramSymbol != None and lastTable.paramSymbol.name == name:
            return lastTable.paramSymbol
        for symbol in lastTable.symbolsData:
            if symbol.name == name:
                return symbol
        return None


    def FindSymbolGlobal(self, name) -> SymbolData:
        if self.paramSymbol != None and self.paramSymbol.name == name:
            return self.paramSymbol
        # recursive upper search
        lastTable = self.GetLastTable()
        for symbol in lastTable.symbolsData:
            if symbol.name == name:
                return symbol
        while lastTable.prevTable != None:
            lastTable = lastTable.prevTable
            for symbol in lastTable.symbolsData:
                if symbol.name == name:
                    return symbol
        return None


    def Clear(self):
        # use this function when method definition starts
        # when every scope ends it cleans up last Symbol Table
        # so when method ends this table contains only one Table
        self.symbolsData.clear()
        self.paramSymbol = None


    def IsNameFreeInScope(self, name:str) -> bool:
        if self.paramSymbol != None and name == self.paramSymbol.name:
            return False
        if self.FindSymbolInLastTable(name) != None:
            return False
        return True


    def IsItMethodParamName(self, name:str) -> bool:
        if self.paramSymbol != None and name == self.paramSymbol.name:
            return True
        return False