from Token import TokenType
from Token import Token
from YADLSyntaxStructures import YADLClassData
from YADLSyntaxStructures import YADLMethodData
from SymbolTable import SymbolTable
from SymbolTable import SymbolData


class SyntaxAnalyzer(object):
    """class that performs syntax analysis of YADL source file based on tokens
    from Parser and makes syntax based translation"""
    def __init__(self, tokens:list):
        # tokens got from Parser
        self.tokens = tokens 
        # current token index in tokens list
        self.currTokenIndex = -1
        # dictionary that contains YADLClassData for every defined in src class
        self.definedClasses = dict()
        # Symbol Table for methods
        self.localSymbolTable = SymbolTable()
        # vars that hold current values
        self.currentClassName = str()
        self.currentMethodName = str()
        # dict that contains classes. Classe contains methods. Method contains asm code
        self.listingsForClasses = dict()
        # variable for creating unique labels
        self.originalIdNum = 0
    

    def Analyze(self):
        # main method; uses rule START -> CLASSES_DEFS MAIN_METHOD_DEF
        try:
            self.ClassDefs()
            self.MainDef()
        except Exception as ex:
            raise Exception(str(ex) + 'Unexpected syntax token at line: ' + str(self.tokens[self.currTokenIndex].line) \
                + ' and position: ' + str(self.tokens[self.currTokenIndex].pos))


    def GetOriginalIdNum(self) -> int:
        self.originalIdNum += 1
        return self.originalIdNum


    def GetNextToken(self) -> Token:
        if self.currTokenIndex < len(self.tokens)-1:
            self.currTokenIndex += 1
            return self.tokens[self.currTokenIndex]
        else:
            raise Exception()


    def PeekNextToken(self) -> Token:
        if self.currTokenIndex < len(self.tokens)-1:
            return self.tokens[self.currTokenIndex+1]
        else:
            raise Exception()


    def GetCurrentToken(self) -> Token:
        return self.tokens[self.currTokenIndex]


    def Match(self, token:Token, type:TokenType, value:str = None):
        if token.type == type and value == None:
            return True
        elif token.type == type and token.value == value:
            return True
        else:
            return False


    def ClassDefs(self):
        # CLASS_DEFS → CLASS_DEF CLASS_DEFS | λ
        try:
            while True:
                t = self.PeekNextToken()
                if self.Match(t, TokenType.KEYWORD, 'class'):
                   self.ClassDef()
                else:
                    return
        except Exception as ex:
            raise Exception(str(ex))


    def ClassDef(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'class') \
                    or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()
            
            # if class with such name already defined
            className = self.GetCurrentToken().value
            if self.IsClassDefined(className):
                raise Exception('Class with ' + className + ' has been already defined!')

            self.definedClasses[className] = YADLClassData(className)
            self.currentClassName = className
            
            if not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()
            
            self.listingsForClasses[self.currentClassName] = dict()

            self.FieldDefs()
            self.MethodDefs()
                
            if not self.Match(self.GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception()            

        except Exception as ex:
            raise Exception(str(ex))


    def IsClassDefined(self, className):
        return className in self.definedClasses


    def FieldDefs(self):
        try:
            while True:
                t = self.PeekNextToken()
                if self.Match(t, TokenType.KEYWORD, 'int'):
                    self.FieldDef()
                elif len(self.definedClasses[self.currentClassName].vars) > 0:
                    return
                else:
                    raise Exception('Class variable definitinon expected! Class should contain at least 1 variable definition!')
        except Exception as ex:
            raise Exception(str(ex))


    def FieldDef(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'int') \
                    or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception
            
            fieldName = self.GetCurrentToken().value

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception

            if fieldName in self.definedClasses[self.currentClassName].vars:
                raise Exception('Class variable ' + fieldName + ' has been already defined!')

            self.definedClasses[self.currentClassName].vars.append(fieldName)

        except Exception as ex:
            raise Exception(str(ex))


    def MethodDefs(self):
        try:
            while True:
                t = self.PeekNextToken()
                if self.Match(t, TokenType.IDENTIFIER):
                    self.MethodDef()
                elif len(self.definedClasses[self.currentClassName].methods) > 0:
                    return
                else:
                    raise Exception('Class method definitinon expected! Class should contain at least 1 method definitions!')
        
        except Exception as ex:
            raise Exception(str(ex))


    def MethodDef(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            methodName = self.GetCurrentToken().value

            if not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()
            
            methodParamType = None
            methodParamName = None
            # if method with parameter defined
            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER) \
                    or self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'int'): 
                methodParamType = self.GetCurrentToken().value
                if not (methodParamType in self.definedClasses.keys() or methodParamType == 'int'):
                    raise Exception('Type ' + methodParamType + ' not defined above!')
                if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()
                methodParamName = self.GetCurrentToken().value
                if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET):
                    raise Exception()
            elif not self.Match(self.GetCurrentToken(), TokenType.C_ROUND_BRACKET):
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            if self.definedClasses[self.currentClassName].FindMethodInList(methodName) != None:
                raise Exception('Method with name ' + methodName + ' has been already defined!')
     
            self.definedClasses[self.currentClassName].methods\
                    .append(YADLMethodData(methodName, methodParamType, methodParamName))
            
            self.currentMethodName = methodName

            self.localSymbolTable.Clear()
            if methodParamName != None:
                self.localSymbolTable.AddParamSymbol(SymbolData(methodParamName, methodParamType))

            self.listingsForClasses[self.currentClassName][self.currentMethodName] = str()
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            '_' + self.currentClassName + '_' + self.currentMethodName + ':\n' \
                            + 'PUSH EBP \n' \
                            + 'MOV EBP, ESP \n' 
            
            if methodParamName != None:
                # save object to stack to simplify data manipulations
                if methodParamType == 'int':
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'SUB ESP, 4 \n' \
                        + 'MOV EAX, [EBP + 12] \n'\
                        + 'MOV [EBP - 4], EAX \n'
                else:
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'SUB ESP, ' + str(len(4*self.definedClasses[methodParamType].vars)) + '\n'\
                            + 'MOV EBX, [EBP + 12] \n'
                    for i in range(0, len(self.definedClasses[methodParamType].vars)):
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV EAX, [EBX - ' + str(4*i + 4) + '] \n' \
                            + 'MOV [EBP - ' + str(4*i + 4) + '], EAX \n'

            self.Statements()

            if methodParamName != None and methodParamType != 'int':
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                    'MOV EBX, [EBP + 12] \n' 
                for i in range(0, len(self.definedClasses[methodParamType].vars)):
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'MOV EAX, [EBP - ' + str(4*i) + '] \n' \
                        + 'MOV [EBX - ' + str(4*i) + '], EAX \n'

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'MOV ESP, EBP \n' \
                                                                                   + 'POP EBP \n' 
            if methodParamName != None:
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'RET 4 \n'
            else:
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += 'RET \n'
            
            if not self.Match(self.GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception()

        except Exception as ex:
            raise Exception(str(ex))


    def Statements(self):
        try:
            self.Statement()  # method can't be empty
            while(True):
                if not self.Match(self.PeekNextToken(), TokenType.C_FIGURE_BRACKET):
                    self.Statement()
                else:
                    return
        except Exception as ex:
            raise Exception(str(ex))


    def Statement(self):
        try:
            # find out rule type with help of next Token
            if self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'int'):
                self.IntLocalVarInit()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'this'):
                self.ClassVariableAssign()
            elif self.Match(self.PeekNextToken(), TokenType.IDENTIFIER):
                self.VariableAssignOrMethodCall()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'if'):
                self.IfStatement()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'while'):
                self.WhileStatement()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'print'):
                self.PrintStatement()
        except Exception as ex:
            raise Exception(str(ex))


    def IntLocalVarInit(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'int') \
                    or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            localVarName = self.GetCurrentToken().value
            # if var in same scope with such name exists
            if not self.localSymbolTable.IsNameFreeInScope(localVarName):
                raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
         
            self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'int'))

            if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                raise Exception()

            if self.Match(self.GetNextToken(), TokenType.NUMBER):
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'SUB ESP, 4 \n' \
                                    + 'MOV [ESP], DWORD ' + str(self.GetCurrentToken().value) + ' \n'
            elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                    and self.Match(self.PeekNextToken(), TokenType.SEMICOLON):
                # check if var exists, check if var has int type, assign
                rightVarName = self.GetCurrentToken().value
                symbolData = self.localSymbolTable.FindSymbolGlobal(rightVarName)
                if symbolData == None:
                    raise Exception('Variable ' + rightVarName + ' undefined in method ' + self.currentMethodName + '!')
                elif symbolData.type != 'int':
                    raise Exception('Variable ' + rightVarName + ' can\'t be assigned to variable ' + \
                                localVarName + ' as they have different types!')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'SUB ESP, 4\n' \
                                + 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightVarName)) + '] \n' \
                                + 'MOV [ESP], EAX \n'
            elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                    and self.Match(self.PeekNextToken(), TokenType.ACCESS):
                rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if rightData == None:
                    raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    
                if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()

                rightVarName = self.GetCurrentToken().value
                if rightVarName not in self.definedClasses[rightData.type].vars:
                    raise Exception('Variable ' + rightVarName + ' is undefined in class ' + rightData.type + '!')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'SUB ESP, 4 \n' \
                        + 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name) \
                        + 4*self.definedClasses[rightData.type].vars.index(rightVarName)) + '] \n' \
                        + 'MOV [ESP], EAX \n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                        and self.Match(self.GetNextToken(), TokenType.ACCESS)\
                        and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                # check if class var exists, assign
                rightVarName = self.GetCurrentToken().value
                if rightVarName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + rightVarName + ' undefined in class ' + self.currentClassName + '!')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'SUB ESP, 4\n' \
                                + 'MOV EBX, [EBP + 8 ] \n' \
                                + 'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(rightVarName)*4) + '] \n' \
                                + 'MOV [ESP], EAX \n'
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def CalculateLocationOfVariableInStackFromTop(self, varName:str):
        # calculates dw from value in EBP register to local variable in stack
        localTable = self.localSymbolTable
        data = localTable.FindSymbolGlobal(varName)
        if data == None:
            raise Exception('Unexpected variable!')
        dwLength = 4 # length in double words (4 bytes)
        if localTable.paramSymbol != None:
            if varName == localTable.paramSymbol.name:
                return dwLength
            else:
                dwLength += len(4*self.definedClasses[localTable.paramSymbol.type])
        for symbolData in localTable.symbolsData:
            if symbolData == data:
                return dwLength
            else:
                if symbolData.type == 'int':
                    dwLength += 4
                else: 
                    dwLength += 4 * len(self.definedClasses[symbolData.type].vars)
                    # get type (className) and count class variables
        while localTable.nextScopeTable != None:
            localTable = localTable.nextScopeTable
            data = localTable.FindSymbolGlobal(varName)
            if data == None:
                raise Exception('Unexpected variable!')
            for symbolData in localTable.symbolsData:
                if symbolData == data:
                    return dwLength
                else:
                    if symbolData.type == 'int':
                        dwLength += 4
                    else: 
                        dwLength += 4 * len(self.definedClasses[symbolData.type].vars)


    def ClassVariableAssign(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'this') \
                    or not self.Match(self.GetNextToken(), TokenType.ACCESS)  \
                    or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            classVarName = self.GetCurrentToken().value

            # check if classVarName exists
            if classVarName not in self.definedClasses[self.currentClassName].vars:
                raise Exception('Variable ' + classVarName + ' undefined in class ' + self.currentClassName + '!')

            if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                raise Exception()

            if self.Match(self.GetNextToken(), TokenType.NUMBER):
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV EBX, [EBP + 8] \n' \
                             + 'MOV [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(classVarName)*4) \
                             + '], DWORD ' + str(self.GetCurrentToken().value) + ' \n'
            elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                    and self.Match(self.PeekNextToken(), TokenType.SEMICOLON):
                # check local var: if exists, if int. Assign
                rightVarName = self.GetCurrentToken().value
                symbolData = self.localSymbolTable.FindSymbolGlobal(rightVarName)
                if symbolData == None:
                    raise Exception('Variable ' + rightVarName + ' undefined in method ' + self.currentMethodName + '!')
                elif symbolData.type != 'int':
                    raise Exception('Variable ' + rightVarName + ' can\'t be assigned to variable ' + \
                                localVarName + ' as they have different types!')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                         'MOV EBX, [EBP + 8] \n' \
                          + 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightVarName)) + '] \n' \
                          + 'MOV [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(classVarName)*4) + '], EAX \n'
            elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                    and self.Match(self.PeekNextToken(), TokenType.ACCESS):
                rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if rightData == None:
                    raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    
                if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()

                rightVarName = self.GetCurrentToken().value
                if rightVarName not in self.definedClasses[rightData.type].vars:
                    raise Exception('Variable ' + rightVarName + ' is undefined in class ' + rightData.type + '!')
                
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                    'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name) \
                    + 4*self.definedClasses[rightData.type].vars.index(rightVarName)) + '] \n' \
                    + 'MOV EBX, [EBP + 8] \n' \
                    + 'MOV [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(classVarName)*4) + '], EAX \n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS)      \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                # check class var: if exists. Assign
                rightVarName = self.GetCurrentToken().value
                if rightVarName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + rightVarName + ' undefined in class ' + self.currentClassName + '!')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EBX, [EBP + 8] \n' \
                                    + 'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(rightVarName)*4) + '] \n' \
                                    + 'MOV [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(classVarName)*4) + '], EAX \n'
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def VariableAssignOrMethodCall(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            if self.Match(self.PeekNextToken(), TokenType.O_ROUND_BRACKET):
                self.ClassMethodCall()
            elif self.Match(self.PeekNextToken(), TokenType.ACCESS):
                self.ObjectVarAssignOrMethodCall()
            elif self.Match(self.PeekNextToken(), TokenType.ASSIGN):
                self.LocalVarAssign()
            elif self.Match(self.PeekNextToken(), TokenType.IDENTIFIER):
                self.LocalObjectInit()

        except Exception as ex:
            raise Exception(str(ex))


    def ClassMethodCall(self):
        try:
            methodName = self.GetCurrentToken().value
            
            if not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            methodData = self.definedClasses[self.currentClassName].FindMethodInList(methodName)
            if methodData == None:
                raise Exception('Method does not defined in class ' + self.currentClassName + '!')

            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER) \
                    and self.Match(self.PeekNextToken(), TokenType.C_ROUND_BRACKET):
                # method call with parameter
                argName = self.GetCurrentToken().value
                argData = self.localSymbolTable.FindSymbolGlobal(argName)
                if argData == None:
                    raise Exception('Argument ' + argName + ' in method ' + self.currentMethodName + ' is not defined earlier!') 
                elif methodData.paramType != argData.type:
                    raise Exception('Argument ' + argName + ' has unexpected type! Method ' + self.currentMethodName \
                            + ' expects argument of type ' + methodData.paramType)
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EAX, EBP \n' \
                                    + 'SUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(argName)) + '\n' \
                                    + 'PUSH EAX \n'     \
                                    + 'MOV EAX, [EBP + 8] \n' \
                                    + 'PUSH EAX \n'     \
                                    + 'CALL ' + '_' + self.currentClassName + '_' + methodName + '\n'
                if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                        or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                    raise Exception()
            elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                    and self.Match(self.PeekNextToken(), TokenType.ACCESS):
                rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if rightData == None:
                    raise Exception('Argument ' + rightData.name + ' in method ' + self.currentMethodName + ' is not defined earlier!')
                    
                if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()

                rightVarName = self.GetCurrentToken().value
                if rightVarName not in self.definedClasses[rightData.type].vars:
                    raise Exception('Variable ' + rightVarName + ' is undefined in class ' + rightData.type + '!')
                
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                    'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name) \
                    + 4*self.definedClasses[rightData.type].vars.index(rightVarName)) + '] \n' \
                    + 'PUSH EAX \n'     \
                    + 'MOV EAX, [EBP + 8] \n' \
                    + 'PUSH EAX \n'     \
                    + 'CALL ' + '_' + self.currentClassName + '_' + methodName + '\n'
                if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                        or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                    raise Exception()
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS)      \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                # method call with parameter that is class variable
                argName = self.GetCurrentToken().value
                if argName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + argName + ' undefined in class ' + self.currentClassName + '!')
                elif methodData.paramType != 'int':
                    raise Exception('Argument ' + argName + ' has unexpected type! Method ' + self.currentMethodName \
                            + ' expects argument of type ' + methodData.paramType)
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EBX, [EBP + 8] \n' \
                                    + 'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(argName)*4) + '] \n' \
                                    + 'PUSH EAX \n'     \
                                    + 'MOV EAX, [EBP + 8] \n' \
                                    + 'PUSH EAX \n'     \
                                    + 'CALL ' + '_' + self.currentClassName + '_' + methodName + '\n'
                if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                        or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                    raise Exception()
            elif self.Match(self.GetCurrentToken(), TokenType.C_ROUND_BRACKET):
                # method call without parameter
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EAX, [EBP + 8] \n' \
                                    + 'PUSH EAX \n'     \
                                    + 'CALL ' + '_' + self.currentClassName + '_' + methodName + '\n'
                if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                    raise Exception()
            else:
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def ObjectVarAssignOrMethodCall(self):
        try:
            objName = self.GetCurrentToken().value
            objData = self.localSymbolTable.FindSymbolGlobal(objName)
            if objName == None:
                raise Exception('Variable ' + objName + ' undefined in method ' + self.currentMethodName + '!')

            if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            varName = self.GetCurrentToken().value
            if self.definedClasses[objData.type].FindMethodInList(varName) != None:
                # varName is method
                methodData = self.definedClasses[objData.type].FindMethodInList(varName)
                if not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                    raise Exception()

                if self.Match(self.GetNextToken(), TokenType.IDENTIFIER) \
                        and self.Match(self.PeekNextToken(), TokenType.C_ROUND_BRACKET):
                    argName = self.GetCurrentToken().value
                    argData = self.localSymbolTable.FindSymbolGlobal(argName)
                    if argData == None:
                        raise Exception('Variable ' + argName + ' undefined in method ' + self.currentMethodName + '!')
                    elif methodData.paramType != argData.type:
                        raise Exception('Argument ' + argName + ' has unexpected type! Method ' + self.currentMethodName \
                                + ' expects argument of type ' + methodData.paramType)
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EAX, EBP \n' \
                                    + 'SUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(argName)) + '\n' \
                                    + 'PUSH EAX \n'     \
                                    + 'MOV EAX, EBP \n' \
                                    + 'SUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)) + ' \n'   \
                                    + 'PUSH EAX \n'     \
                                    + 'CALL ' + '_' + objData.type + '_' + methodData.name + '\n'
                    if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                            or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                        raise Exception()
                elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                        and self.Match(self.PeekNextToken(), TokenType.ACCESS):
                    rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if rightData == None:
                        raise Exception('Argument ' + rightData.name + ' in method ' + self.currentMethodName + ' is not defined earlier!')
                    
                    if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                            or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                        raise Exception()

                    rightVarName = self.GetCurrentToken().value
                    if rightVarName not in self.definedClasses[rightData.type].vars:
                        raise Exception('Variable ' + rightVarName + ' is undefined in class ' + rightData.type + '!')
               
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name) \
                        + 4*self.definedClasses[rightData.type].vars.index(rightVarName)) + '] \n' \
                        + 'PUSH EAX \n'     \
                        + 'MOV EAX, EBP \n' \
                        + 'SUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)) + ' \n'   \
                        + 'PUSH EAX \n'     \
                        + 'CALL ' + '_' + self.currentClassName + '_' + methodName + '\n'
                    if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                            or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                        raise Exception()
                elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                        and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    # method call with parameter that is class variable
                    argName = self.GetCurrentToken().value
                    if argName not in self.definedClasses[self.currentClassName].vars:
                        raise Exception('Variable ' + argName + ' is undefined in class ' + self.currentClassName + '!')
                    elif methodData.paramType != 'int':
                        raise Exception('Argument ' + argName + ' has unexpected type! Method ' + self.currentMethodName \
                                + ' expects argument of type ' + methodData.paramType)
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                        'MOV EBX, [EBP + 8] \n' \
                                        + 'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(argName)*4) + '] \n' \
                                        + 'PUSH EAX \n'     \
                                        + 'MOV EAX, EBP \n' \
                                        + 'SUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)) + ' \n'   \
                                        + 'PUSH EAX \n'     \
                                        + 'CALL ' + '_' + self.currentClassName + '_' + methodName + '\n'
                    if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                            or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                        raise Exception()
                elif self.Match(self.GetCurrentToken(), TokenType.C_ROUND_BRACKET):
                    # method call without parameter
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EAX, EBP \n' \
                                    + 'SUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)) + ' \n'   \
                                    + 'PUSH EAX \n'     \
                                    + 'CALL ' + '_' + objData.type + '_' + methodData.name + '\n'
                    if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                        raise Exception()
                else:
                    raise Exception()
            elif varName in self.definedClasses[objData.type].vars:
                # varName is class variable
                if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                    raise Exception()
                
                if self.Match(self.GetNextToken(), TokenType.NUMBER):
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(objName) \
                                + 4*self.definedClasses[objData.type].vars.index(varName)) + '], DWORD ' \
                                + str(self.GetCurrentToken().value) + '\n'
                elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                        and self.Match(self.PeekNextToken(), TokenType.SEMICOLON):
                    rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if rightData == None:
                        raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    elif rightData.type != 'int':
                        raise Exception('Variable ' + rightData.name + ' can\'t be assigned to variable ' + \
                            varName + ' as they have different types!')
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name)) + '] \n' \
                            + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)\
                            + 4*self.definedClasses[objData.type].vars.index(varName)) + '], EAX \n'
                elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER) \
                        and self.Match(self.PeekNextToken(), TokenType.ACCESS):
                    rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if rightData == None:
                        raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    
                    if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                            or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                        raise Exception()

                    rightVarName = self.GetCurrentToken().value
                    if rightVarName not in self.definedClasses[rightData.type].vars:
                        raise Exception('Variable ' + rightVarName + ' is undefined in class ' + rightData.type + '!')
                    
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name) \
                            + 4*self.definedClasses[rightData.type].vars.index(rightVarName)) + '] \n' \
                            + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)\
                            + 4*self.definedClasses[objData.type].vars.index(varName)) + '], EAX \n'
                elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                        and self.Match(self.GetNextToken(), TokenType.ACCESS)   \
                        and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    rightVarName = self.GetCurrentToken().value
                    if rightVarName not in self.definedClasses[self.currentClassName].vars:
                        raise Exception('Variable ' + rightVarName + ' undefined in class ' + self.currentClassName + '!')
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                        'MOV EBX, [EBP + 8] \n' \
                                        + 'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(rightVarName)*4) + '] \n' \
                                        + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)\
                                        + 4*self.definedClasses[objData.type].vars.index(varName)) + '], EAX \n'
                else:
                    raise Exception()

                if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                    raise Exception()
            else:
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def LocalVarAssign(self):
        try:
            varData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
            if varData == None:
                raise Exception('Variable ' + varData.name + ' undefined in method ' + self.currentMethodName + '!')

            if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                raise Exception()

            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                # local vars assigning
                # OR constructor call
                rightName = self.GetCurrentToken().value
                if rightName in self.definedClasses.keys() \
                        and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        and self.Match(self.GetNextToken(), TokenType.KEYWORD, 'CreateInstance') \
                        and self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET) \
                        and self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET):
                    # constructor call
                    # find declaration of variable in stack, init values to 0
                    if varData.type != rightName:
                        raise Exception('Can\'t cast ' + varData.name + ' to ' + rightName + '!')
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'SUB ESP, ' + str(4*len(self.definedClasses[self.currentClassName].vars)) + ' \n'
                    dwLocation = self.CalculateLocationOfVariableInStackFromTop(varData.name)
                    for i in range(0, len(self.definedClasses[self.currentClassName].vars)):
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV [EBP - ' + str(dwLocation + 4*i) + '], DWORD 0 \n'
                else:
                    # assigning
                    if self.Match(self.PeekNextToken(), TokenType.SEMICOLON):
                        rightVarData = self.localSymbolTable.FindSymbolGlobal(rightName)
                        if rightVarData == None:
                            raise Exception('Variable ' + rightName + ' undefined in method ' + self.currentMethodName + '!')
                        elif rightVarData.type != varData.type:
                            raise Exception('Variable ' + rightName + ' can\'t be assigned to variable ' + \
                                varData.name + ' as they have different types!')
                        if varData.type == 'int':
                            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightName)) + '] \n' \
                                    + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)) + '], EAX \n'
                        # need to copy all variables of the object
                        else:
                            count = len(self.definedClasses[varData.type].vars)
                            for i in range(0, count):
                                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                        'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightName)+i*4) + '] \n' \
                                        + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)+i*4) + '], EAX \n'
                    elif self.Match(self.PeekNextToken(), TokenType.ACCESS):
                        rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                        if rightData == None:
                            raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    
                        if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                                or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                            raise Exception()

                        rightVarName = self.GetCurrentToken().value
                        if rightVarName not in self.definedClasses[rightData.type].vars:
                            raise Exception('Variable ' + rightVarName + ' is undefined in class ' + rightData.type + '!')
                    
                        elif varData.type != 'int':
                            raise Exception('Variable ' + rightVarName + ' can\'t be assigned to variable ' + \
                                varData.name + ' as they have different types!')

                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightData.name) \
                                + 4*self.definedClasses[rightData.type].vars.index(rightVarName)) + '] \n' \
                                + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name))\
                                + '], EAX \n'
                    else:
                        raise Exception()

            elif self.Match(self.GetCurrentToken(), TokenType.NUMBER):
                # check if int. Assign num to local var
                if varData.type != 'int':
                    raise Exception('Local variable ' + varData.name + ' is not of type int!')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)) + '], DWORD ' \
                                + str(self.GetCurrentToken().value) + '\n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this')\
                    and self.Match(self.GetNextToken(), TokenType.ACCESS)   \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                rightVarName = self.GetCurrentToken().value
                if rightVarName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + rightVarName + ' undefined in class ' + self.currentClassName + '!')

                if varData.type != 'int':
                    raise Exception('Variable ' + rightVarName + ' can\'t be assigned to variable ' + \
                                varData.name + ' as they have different types!')

                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                    'MOV EBX, [EBP + 8] \n' \
                                    + 'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(rightVarName)*4) + '] \n' \
                                    + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name))\
                                    + '], EAX \n'
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def LocalObjectInit(self):
        try:
            objType = self.GetCurrentToken().value
            if objType not in self.definedClasses.keys():
                raise Exception('Undefined type ' + objType + '!')

            if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                raise Exception()

            objName = self.GetCurrentToken().value
            if not self.localSymbolTable.IsNameFreeInScope(objName):
                raise Exception('Variable with name ' + objName + ' has been already defined!')
            self.localSymbolTable.AddSymbol(SymbolData(objName, objType))

            if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                raise Exception()

            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                rightName = self.GetCurrentToken().value
                if rightName in self.definedClasses.keys() \
                        and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        and self.Match(self.GetNextToken(), TokenType.KEYWORD, 'CreateInstance') \
                        and self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET) \
                        and self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET):
                    # constructor call
                    # find declaration of variable in stack, init values to 0
                    if objType != rightName:
                        raise Exception('Can\'t cast ' + objType + ' to ' + rightName + '!')
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'SUB ESP, ' + str(4*len(self.definedClasses[objType].vars)) + ' \n'
                    dwLocation = self.CalculateLocationOfVariableInStackFromTop(objName)
                    for i in range(0, len(self.definedClasses[objType].vars)):
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV [EBP - ' + str(dwLocation + 4*i) + '], DWORD 0 \n'
                else:
                    rightVarData = self.localSymbolTable.FindSymbolGlobal(rightName)
                    if rightVarData == None:
                        raise Exception('Variable ' + rightName + ' undefined in method ' + self.currentMethodName + '!')
                    elif rightVarData.type != objType:
                        raise Exception('Variable ' + rightName + ' can\'t be assigned to variable ' + \
                            objType + ' as they have different types!')
                    # need to copy all variables of the object
                    count = len(self.definedClasses[objType].vars)
                    for i in range(0, count):
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rightName)+i*4) + '] \n' \
                                + 'MOV [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)+i*4) + '], EAX \n'
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()

        except Exception as ex:
            raise Exception(str(ex))


    def IfStatement(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'if') \
                    or not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            # detect left operand
            leftOperandToEAX = str()
            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                    leftData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if leftData == None:
                        raise Exception('Variable ' + leftData.name + ' undefined in method ' + self.currentMethodName + '!')
                    if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                            or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                        raise Exception()
                    leftVarName = self.GetCurrentToken().value
                    if leftVarName not in self.definedClasses[leftData.type].vars:
                        raise Exception('Variable ' + leftVarName + ' is undefined in class ' + leftData.type + '!')
                    leftOperandToEAX = 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(LeftData.name) \
                                + 4*self.definedClasses[leftData.type].vars.index(leftVarName)) + '] \n'          
                else:
                    varData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if varData == None:
                        raise Exception('Variable ' + varData.name + ' undefined in method ' + self.currentMethodName + '!')
                    elif varData.type != int:
                        raise Exception('Use integer values for comparison!')
                    leftOperandToEAX = 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)) \
                                        + '] \n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                varName = self.GetCurrentToken().value
                if varName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + varName + ' is undefined in class ' + self.currentClassName + '!')
                leftOperandToEAX = 'MOV EBX, [EBP + 8]' \
                            'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(varName)*4) \
                            + '] \n'
            else:
                raise Exception()
            
            # detect compare sign
            if not self.Match(self.GetNextToken(), TokenType.EQUAL) \
                    or not self.Match(self.GetCurrentToken(), TokenType.GREATER) \
                    or not self.Match(self.GetCurrentToken(), TokenType.GREATER_EQUAL) \
                    or not self.Match(self.GetCurrentToken(), TokenType.LESS) \
                    or not self.Match(self.GetCurrentToken(), TokenType.LESS_EQUAL):
                raise Exception()
            cmpType = self.GetCurrentToken().type

            # detect right operand
            rightOperandToEBX = str()
            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                    rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if rightData == None:
                        raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                            or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                        raise Exception()
                    leftVarName = self.GetCurrentToken().value
                    if leftVarName not in self.definedClasses[rightData.type].vars:
                        raise Exception('Variable ' + leftVarName + ' is undefined in class ' + rightData.type + '!')
                    rightOperandToEBX = 'MOV EBX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(LeftData.name) \
                                + 4*self.definedClasses[rightData.type].vars.index(leftVarName)) + '] \n'          
                else:
                    varData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if varData == None:
                        raise Exception('Variable ' + varData.name + ' undefined in method ' + self.currentMethodName + '!')
                    elif varData.type != int:
                        raise Exception('Use integer values for comparison!')
                    rightOperandToEBX = 'MOV EBX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)) \
                                        + '] \n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                varName = self.GetCurrentToken().value
                if varName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + varName + ' is undefined in class ' + self.currentClassName + '!')
                rightOperandToEBX = 'MOV EDX, [EBP + 8]' \
                            'MOV EBX, [EDX - ' + str(self.definedClasses[self.currentClassName].vars.index(varName)*4) \
                            + '] \n'
            elif self.Match(self.GetCurrentToken(), TokenType.NUMBER):
                rightOperandToEBX = 'MOV EBX, DWORD ' + str(self.GetCurrentToken().value) + '\n'
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            # first operand in eax
            # second operand in ebx
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        leftOperandToEAX    \
                        + rightOperandToEBX \
                        + 'CMP EAX, EBX \n'

            cmpInstr = str()
            if cmpType == TokenType.EQUAL:
                cmpInstr = 'E'
            elif cmpType == TokenType.GREATER:
                cmpInstr = 'G'
            elif cmpType == TokenType.GREATER_EQUAL:
                cmpInstr = 'GE'
            elif cmpType == TokenType.LESS:
                cmpInstr = 'L'
            elif cmpType == TokenType.LESS_EQUAL:
                cmpInstr = 'LE'

            jmpLabel = '_else_statement_' + str(self.GetOriginalIdNum())
            # jump to else statement (code after if statements)
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'jn' + cmpInstr + ' ' + jmpLabel + '\n'   

            self.localSymbolTable.AddNewScopeTable()

            self.Statements()

            self.localSymbolTable.RemoveLastScopeTable()

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        jmpLabel + ': \n'

            if not self.Match(self.GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception

        except Exception as ex:
            raise Exception(str(ex))


    def WhileStatement(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'while') \
                    or not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            # detect left operand
            leftOperandToEAX = str()
            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                    leftData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if leftData == None:
                        raise Exception('Variable ' + leftData.name + ' undefined in method ' + self.currentMethodName + '!')
                    if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                            or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                        raise Exception()
                    leftVarName = self.GetCurrentToken().value
                    if leftVarName not in self.definedClasses[leftData.type].vars:
                        raise Exception('Variable ' + leftVarName + ' is undefined in class ' + leftData.type + '!')
                    leftOperandToEAX = 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(LeftData.name) \
                                + 4*self.definedClasses[leftData.type].vars.index(leftVarName)) + '] \n'          
                else:
                    varData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if varData == None:
                        raise Exception('Variable ' + varData.name + ' undefined in method ' + self.currentMethodName + '!')
                    elif varData.type != int:
                        raise Exception('Use integer values for comparison!')
                    leftOperandToEAX = 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)) \
                                        + '] \n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                varName = self.GetCurrentToken().value
                if varName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + varName + ' is undefined in class ' + self.currentClassName + '!')
                leftOperandToEAX = 'MOV EBX, [EBP + 8]' \
                            'MOV EAX, [EBX - ' + str(self.definedClasses[self.currentClassName].vars.index(varName)*4) \
                            + '] \n'
            else:
                raise Exception()
            
            # detect compare sign
            if not self.Match(self.GetNextToken(), TokenType.EQUAL) \
                    or not self.Match(self.GetCurrentToken(), TokenType.GREATER) \
                    or not self.Match(self.GetCurrentToken(), TokenType.GREATER_EQUAL) \
                    or not self.Match(self.GetCurrentToken(), TokenType.LESS) \
                    or not self.Match(self.GetCurrentToken(), TokenType.LESS_EQUAL):
                raise Exception()
            cmpType = self.GetCurrentToken().type

            # detect right operand
            rightOperandToEBX = str()
            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                    rightData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if rightData == None:
                        raise Exception('Variable ' + rightData.name + ' undefined in method ' + self.currentMethodName + '!')
                    if not self.Match(self.GetNextToken(), TokenType.ACCESS) \
                            or not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                        raise Exception()
                    leftVarName = self.GetCurrentToken().value
                    if leftVarName not in self.definedClasses[rightData.type].vars:
                        raise Exception('Variable ' + leftVarName + ' is undefined in class ' + rightData.type + '!')
                    rightOperandToEBX = 'MOV EBX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(LeftData.name) \
                                + 4*self.definedClasses[rightData.type].vars.index(leftVarName)) + '] \n'          
                else:
                    varData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                    if varData == None:
                        raise Exception('Variable ' + varData.name + ' undefined in method ' + self.currentMethodName + '!')
                    elif varData.type != int:
                        raise Exception('Use integer values for comparison!')
                    rightOperandToEBX = 'MOV EBX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(varData.name)) \
                                        + '] \n'
            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                varName = self.GetCurrentToken().value
                if varName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + varName + ' is undefined in class ' + self.currentClassName + '!')
                rightOperandToEBX = 'MOV EDX, [EBP + 8]' \
                            'MOV EBX, [EDX - ' + str(self.definedClasses[self.currentClassName].vars.index(varName)*4) \
                            + '] \n'
            elif self.Match(self.GetCurrentToken(), TokenType.NUMBER):
                rightOperandToEBX = 'MOV EBX, DWORD ' + str(self.GetCurrentToken().value) + '\n'
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            # first operand in eax
            # second operand in ebx
            whileConditionLabel = '_while_condition_' + str(self.GetOriginalIdNum())
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        whileConditionLabel + ':'\
                        + leftOperandToEAX  \
                        + rightOperandToEBX \
                        + 'CMP EAX, EBX \n'

            cmpInstr = str()
            if cmpType == TokenType.EQUAL:
                cmpInstr = 'E'
            elif cmpType == TokenType.GREATER:
                cmpInstr = 'G'
            elif cmpType == TokenType.GREATER_EQUAL:
                cmpInstr = 'GE'
            elif cmpType == TokenType.LESS:
                cmpInstr = 'L'
            elif cmpType == TokenType.LESS_EQUAL:
                cmpInstr = 'LE'

            whileExitLabel = '_while_exit_' + str(self.GetOriginalIdNum())
            # jump to else statement (code after if statements)
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'jn' + cmpInstr + ' ' + whileExitLabel + '\n'   

            self.localSymbolTable.AddNewScopeTable()

            self.Statements()

            self.localSymbolTable.RemoveLastScopeTable()

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'JMP ' + whileConditionLabel + '\n' \
                        + whileExitLabel + ': \n'

            if not self.Match(self.GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception

        except Exception as ex:
            raise Exception(str(ex))


    def PrintStatement(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'print') \
                    or not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET):
                raise Exception()

            if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                pass
            if self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                    and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                    and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                pass
            else:
                raise Exception()

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET):
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def MainDef(self):
        try:
            # uses rule: MAIN_METHOD_DEF -> main() { STATEMENTS }
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'main') \
                    or not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            self.currentMethodName = 'main'
            self.currentClassName = None
            self.listingsForClasses[self.currentClassName] = dict()
            self.listingsForClasses[self.currentClassName][self.currentMethodName] = str()
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        '_start: \n' \
                        + 'MOV EBP, ESP \n'
            
            self.localSymbolTable.Clear()

            self.Statements()

            if not self.Match(self.GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception
        except Exception as ex:
            raise Exception(str(ex))


    def BuildCode(self) -> str:
        code = 'segment .text \n'    \
                + 'global _start\n\n'\

        code += self.listingsForClasses[None]['main']

        code += 'mov eax, 1       ; linux system call number (sys_exit) \n'\
                + 'int 0x80 \n\n'

        for className in self.listingsForClasses.keys():
            if className != None:
                for methodName in self.listingsForClasses[className].keys():
                    code += self.listingsForClasses[className][methodName]

        return code

    def LValue(self):
        # inspect next tokens for left value
        # after execution
        if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
            if self.Match(self.PeekNextToken, TokenType.ACCESS):
                GetNextToken()
                if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()
                return # LValue.ObjAccess
            else:
                return # LValue.Var
        elif self.Match(self.GetNextToken(), TokenType.KEYWORD, 'this') \
                and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
            return # LValue.classVar