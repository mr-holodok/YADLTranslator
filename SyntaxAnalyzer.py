from Token import TokenType
from Token import Token
from YADLSyntaxStructures import YADLClassData
from YADLSyntaxStructures import YADLMethodData
from YADLSyntaxStructures import YADLClassConstructor
from SymbolTable import SymbolTable
from SymbolTable import SymbolData
from SymbolTable import SymbolScopeType


class SyntaxAnalyzer(object):
    """class that performs syntax analysis of YADL source file based on tokens
    from Parser and return Abstract Syntax Tree"""
    def __init__(self, tokens:list):
        # tokens got from Parser
        self.tokens = tokens 
        # current token index in tokens list
        self.currTokenIndex = -1
        # dictionary that contains YADLClassData for every defined in src class
        self.defindedClasses = dict()
        # Symbol Table for methods
        self.localSymbolTable = SymbolTable()
        # vars that hold current values
        self.currentClassName = str()
        self.currentMethodName = str()
        # dict that contains classes. Classes contain methods. Method contains asm code
        self.listingsForClasses = dict()
    

    def Analyze(self):
        # main method; uses rule START -> CLASSES_DEFS MAIN_METHOD_DEF
        try:
            ClassesDefs()
            MainDef()
        except Exception as ex:
            raise Exception(ex + 'Unexpected syntax token at line: ' + self.tokens[self.currTokenIndex].line \
                + ' and position: ' + self.tokens[self.currTokenIndex].pos)


    def GetNextToken(self) -> Token:
        if self.currTokenIndex < len(self.tokens)-1:
            self.currTokenIndex += 1
            return self.tokens[self.currTokenIndex]
        else:
            raise Exception


    def PeekNextToken(self) -> Token:
        if self.currTokenIndex < len(self.tokens)-1:
            return self.tokens[self.currTokenIndex+1]
        else:
            raise Exception


    def GetCurrentToken(self) -> Token:
        return self.tokens[self.currTokenIndex]


    def Match(self, token:Token, type:TokenType, value:str = None):
        if token.type == type and value == None:
            return True
        elif tokne.type == type and token.val == value:
            return True
        else:
            return False


    def ClassDefs(self):
        # CLASS_DEFS → CLASS_DEF CLASS_DEFS | λ
        try:
            while True:
                t = PeekNextToken()
                if Match(t, TokenType.KEYWORD, 'class'):
                   ClassDef()
                else:
                    return
        except Exception:
            raise Exception()


    def ClassDef(self):
        try:
            if not Match(GetNextToken(), TokenType.KEYWORD, 'class') \
                    or not Match(GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()
            
            # if class with such name already defined
            className = GetCurrentToken().val
            if IsClassDefined(className):
                raise Exception()

            self.defindedClasses[className] = YADLClassData(className)
            self.currentClassName = className
            
            if not Match(GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()
            
            FieldDefs()
            Constructor()
            MethodDefs()
                
            if not Match(t, TokenType.C_FIGURE_BRACKET):
                raise Exception()
                    
            # check if class definition not empty
            if len(classData.vars) == 0 and len(classData.methods) == 0:
                raise Exception()
        except Exception:
            raise Exception()


    def IsClassDefined(self, className):
        return className in self.defindedClasses


    def FieldDefs(self):
        try:
            while True:
                t = PeekNextToken()
                if Match(t, TokenType.KEYWORD, 'int'):
                    FieldDef()
                elif len(self.defindedClasses[self.currentClassName].vars) > 0:
                    return
                else:
                    raise Exception('Class variable definitinon expected!')
        except Exception:
            raise Exception()


    def FieldDef(self):
        try:
            if not Match(GetNextToken(), TokenType.KEYWORD, 'int') \
                    or not Match(GetNextToken(), TokenType.IDENTIFIER):
                raise Exception
            
            fieldName = GetCurrentToken().val

            if not Match(GetNextToken(), TokenType.SEMICOLON):
                raise Exception

            if fieldName in self.definedClasses[self.currentClassName].vars:
                raise Exception('Class variable ' + fieldName + ' has been already defined!')

            self.defindedClasses[self.currentClassName].vars.append(fieldName)
        except Exception:
            raise Exception


    def Constructor(self):
        try:
            if not Match(GetNextToken(), TokenType.KEYWORD, 'CreateInstance') \
                    or not Match(GetNextToken(), TokenType.O_ROUND_BRACKET) \
                    or not Match(GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not Match(GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()
            FieldInits()
            if not Match(GetCurrentToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception()
            return initedValues
        except Exception:
            raise Exception()


    def FieldInits(self):
        try:
            while True:
                t = PeekNextToken()
                if Match(t, TokenType.KEYWORD, 'this'):
                    FieldInit()
                else:
                    if self.defindedClasses[self.currentClassName].constructor.IsAllVarsInited():
                        return
                    else:
                        raise Exception('All class variables must be initialized!')
        except Exception:
            raise Exception()


    def FieldInit(self):
        try:
            if not Match(GetNextToken(), TokenType.KEYWORD, 'this') \
                    or not Match(GetNextToken(), TokenType.ACCESS) \
                    or not Match(GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            varName = GetCurrentToken().val
            if varName not in self.defindedClasses[self.currentClassName].vars:
                raise Exception(varName + ' variable doesn\'t declared in ' \
                    + self.currentClassName + ' class variables!')

            if not Match(GetNextToken(), TokenType.ASSIGN) \
                    or Match(GetNextToken(), TokenType.NUMBER):
                raise Exception()

            num = int(GetCurrentToken().val)
            if num < -2147483648 or num > 2147483647:
                raise Exception('Number doesn\'t fit in 4 bytes!')

            if not Match(GetNextToken(), TokenType.SEMICOLON):
                raise Exception()

            self.defindedClasses[self.currentClassName].constructor.AddInitedVar( (varName, num) )
        except Exception:
            raise Exception()


    def MethodDefs(self):
        try:
            while True:
                t = PeekNextToken()
                if Match(t, TokenType.IDENTIFIER):
                    MethodDef()
                elif len(self.defindedClasses[self.currentClassName].methods) > 0:
                    return
                else:
                    raise Exception()
        except Exception:
            raise Exception()


    def MethodDef(self):
        try:
            if not Match(GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            methodName = GetCurrentToken().val

            if not Match(GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()
            
            methodParamType = None
            methodParamName = None
            # if method with parameter defined
            if Match(GetNextToken(), TokenType.IDENTIFIER) \
                    or Match(GetCurrentToken(), TokenType.KEYWORD, 'int'): 
                methodParamType = GetCurrentToken().val
                if not (methodParamType in self.defindedClasses or methodParamType == 'int'):
                    raise Exception('Type ' + methodParamType + ' not defined above!')
                if not Match(GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()
                methodParamName = GetCurrentToken().val
            
            if not Match(GetCurrentToken(), TokenType.C_ROUND_BRACKET) \
                    or not Match(GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            for m in self.defindedClasses[self.currentClassName].methods:
                if m.name == methodName:
                    raise Exception('Method with name ' + methodName + ' has been already defined!')
     
            self.defindedClasses[self.currentClassName].methods\
                    .append(YADLMethodData(methodName, methodParamType))
            
            self.currentMethodName = methodName

            self.localSymbolTable.Clear()
            for var in self.defindedClasses[self.currentClassName].vars:
                self.localSymbolTable.AddSymbol(SymbolData(var, 'int', SymbolScopeType.CLASS, SymbolState.DEFINED))
            if methodParamName != None:
                self.localSymbolTable.AddSymbol(SymbolData(metmethodParamName, methodParamType, SymbolScopeType.LOCAL, SymbolState.DEFINED))

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += '_' + self.currentClassName + '_' \
                            + self.currentMethodName + ':'

            Statements()
            
            if not Match(GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception

            return
        except Exception:
            raise Exception


    def Statements(self):
        try:
            if Match(PeekNextToken(), TokenType.KEYWORD, 'int'):
                IntLocalVarInit()
            elif Match(PeekNextToken(), TokenType.KEYWORD, 'if'):
                pass
            elif Match(PeekNextToken(), TokenType.KEYWORD, 'while'):
                pass
        except Exception:
            raise Exception()


    def IntLocalVarInit(self):
        try:
            if not Match(GetNextToken(), TokenType.KEYWORD, 'int') \
                    or not Match(GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()
            localVarName = GetCurrentToken().val

            if Match(GetNextToken(), TokenType.SEMICOLON):
                symbolData = self.localSymbolTable.FindSymbolInLastTable(localVarName, SymbolScopeType.LOCAL)
                if symbolData != None:
                    raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
                self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'int', SymbolScopeType.LOCAL, SymbolState.UNDEFINED))
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'SUB ESP, 4\n'
            elif Match(GetCurrentToken(), TokenType.ASSIGN):
                if Match(GetNextToken(), TokenType.NUMBER):
                    symbolData = self.localSymbolTable.FindSymbolInLastTable(localVarName, SymbolScopeType.LOCAL)
                    if symbolData != None:
                        raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
                    self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'int', SymbolScopeType.LOCAL, SymbolState.DEFINED))
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'SUB ESP, 4\n' \
                                    + 'MOV [ESP], ' + str(GetCurrentToken().val)
                elif Match(GetCurrentToken(), TokenType.IDENTIFIER):
                    rightVarName = GetCurrentToken().val
                    symbolData = self.localSymbolTable.FindSymbolGlobal(rightVarName, SymbolScopeType.LOCAL)
                    if symbolData == None:
                        raise Exception('Variable ' + rightVarName + ' undefined in method ' + self.currentMethodName + '!')
                    elif symbolData.type != 'int':
                        raise Exception('Variable ' + rightVarName + ' can\'t be assigned to variable ' + \
                                localVarName + ' as they have different types!')
                    elif symbolData.state == SymbolState.UNDEFINED:
                        raise Exception('Variable ' + rightVarName + ' has undefined value in method ' + self.currentMethodName + '!')
                    symbolData = self.localSymbolTable.FindSymbolInLastTable(localVarName, SymbolScopeType.LOCAL)
                    if symbolData != None:
                        raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
                    self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'int', SymbolScopeType.LOCAL, SymbolState.DEFINED))
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'SUB ESP, 4\n' \
                                    + 'MOV EAX, [EBP - ' + str(CalculateLocationOfVariableInStackFromTop(rightVarName)) + ']' \
                                    + 'MOV [ESP], EAX'  
                elif Match(GetCurrentToken(), TokenType.KEYWORD, 'this') \
                        and Match(GetNextToken(), TokenType.ACCESS)\
                        and Match(GetNextToken(), TokenType.IDENTIFIER):
                    rightVarName = GetCurrentToken().val
                    if rightVarName not in self.defindedClasses[self.currentClassName].vars:
                        raise Exception('Variable ' + rightVarName + ' undefined in class ' + self.currentClassName + '!')
                    symbolData = self.localSymbolTable.FindSymbolInLastTable(localVarName, SymbolScopeType.LOCAL)
                    if symbolData != None:
                        raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
                    self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'int', SymbolScopeType.LOCAL, SymbolState.DEFINED))
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'SUB ESP, 4\n' \
                                    + 'MOV EBX, [EBP + 8 ]' \
                                    + 'MOV EAX, [EBX + ' + self.defindedClasses[self.currentClassName].vars.index(rightVarName)*4 + ']' \
                                    + 'MOV [ESP], EAX'  
                    
                else:
                    raise Exception()
        except Exception:
            raise Exception()


    def CalculateLocationOfVariableInStackFromTop(self, varName:str):
        # calculates dw from value in EBP register to local variable in stack
        localTable = self.localSymbolTable
        data = localTable.FindSymbolGlobal(varName, SymbolScopeType.LOCAL)
        if data == None:
            raise Exception('Unexpected variable!')
        dwLength = 4 # length in double words (4 bytes)
        for symbolData in localTable.symbolsData:
            if symbolData == data:
                return dwLength
            else:
                if symbolData.type == 'int':
                    dwLength += 4
                else: 
                    dwLength += 4 * len(self.defindedClasses[data.type].vars)
                    # get type (className) and count class variables
        while localTable.nextScopeTable != None:
            localTable = localTable.nextScopeTable
            data = localTable.FindSymbolGlobal(varName, SymbolScopeType.LOCAL)
            if data == None:
                raise Exception('Unexpected variable!')
            for symbolData in localTable.symbolsData:
                if symbolData == data:
                    return dwLength
                else:
                    if symbolData.type == 'int':
                        dwLength += 4
                    else: 
                        dwLength += 4 * len(self.defindedClasses[data.type].vars)




    #def MainDef(self):
    #    # uses rule: MAIN_METHOD_DEF -> main() { STATEMENTS }
    #    if not Match(TokenType.KEYWORD, 'main') \
    #            or not Match(TokenType.O_ROUND_BRACKET) \
    #            or not Match(TokenType.C_ROUND_BRACKET) \
    #            or not Match(TokenType.O_FIGURE_BRACKET):
    #        raise Exception()
        