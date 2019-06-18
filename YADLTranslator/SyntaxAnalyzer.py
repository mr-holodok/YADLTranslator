from Token import TokenType
from Token import Token
from YADLSyntaxStructures import YADLClassData
from YADLSyntaxStructures import YADLMethodData
from SymbolTable import SymbolTable
from SymbolTable import SymbolData
from VariableTypes import LValue
from VariableTypes import LValueType
from VariableTypes import RValue
from VariableTypes import RValueType


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
        # for strings declarations
        self.dataSection = 'section .data \n'     \
                + "NumFormat: db '%d', 0xA, 0 \n" \
    

    def Analyze(self):
        # main method; uses rule START -> CLASSES_DEFS MAIN_METHOD_DEF
        try:
            self.ClassDefs()
            self.MainDef()
        except Exception as ex:
            raise Exception(str(ex) + 'Unexpected syntax token at line: ' + str(self.tokens[self.currTokenIndex].line) \
                + ' and position: ' + str(self.tokens[self.currTokenIndex].pos))


    def GetOriginalIdNum(self) -> int:
        # return original number for asm labels
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
            # check if field name free in current class
            if fieldName in self.definedClasses[self.currentClassName].vars:
                raise Exception('Class variable ' + fieldName + ' has been already defined!')
            
            self.definedClasses[self.currentClassName].vars.append(fieldName)
            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception
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
                    raise Exception('Class method definitinon expected! Class should contain at least 1 method definition!')
        
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
            # create new stack frame
            self.listingsForClasses[self.currentClassName][self.currentMethodName] = str()
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            '_' + self.currentClassName + '_' + self.currentMethodName + ':\n' \
                            + 'PUSH EBP \n' \
                            + 'MOV EBP, ESP \n' 
            
            self.Statements()

            # cleans up the stack
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'ADD ESP, ' + str(self.GetLocalVarsSize()) + '\n'
            # restore EBP
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV ESP, EBP \n'   \
                            + 'POP EBP \n'      \
                            + 'RET \n'
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
            if self.PredictVarInit():
                self.VarInit()
            elif self.PredictAssigning():
                self.Assigning()
            elif self.PredictMethodCall():
                self.MethodCall()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'if'):
                self.IfStatement()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'while'):
                self.WhileStatement()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'print'):
                self.PrintStatement()
            elif self.Match(self.PeekNextToken(), TokenType.KEYWORD, 'prints'):
                self.PrintStringStatement()
            else:
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    # PREDICT methods peek next tokens to find out if their sequence match to specified rules
    def PredictMethodCall(self) -> bool:
        i = self.currTokenIndex
        if i + 4 <= len(self.tokens)-1 \
                and self.tokens[i+1].type == TokenType.IDENTIFIER \
                and self.tokens[i+2].type == TokenType.ACCESS \
                and self.tokens[i+3].type == TokenType.IDENTIFIER \
                and self.tokens[i+4].type == TokenType.O_ROUND_BRACKET:
            return True
        if i + 2 <= len(self.tokens)-1 \
                and self.tokens[i+1].type == TokenType.IDENTIFIER \
                and self.tokens[i+2].type == TokenType.O_ROUND_BRACKET:
            return True
        return False


    def PredictAssigning(self) -> bool:
        i = self.currTokenIndex
        if i + 2 <= len(self.tokens)-1 \
                and self.tokens[i+1].type == TokenType.IDENTIFIER \
                and self.tokens[i+2].type == TokenType.ASSIGN:
            return True
        elif i + 4 <= len(self.tokens)-1 \
                and self.tokens[i+1].type == TokenType.IDENTIFIER \
                and self.tokens[i+2].type == TokenType.ACCESS \
                and self.tokens[i+3].type == TokenType.IDENTIFIER \
                and self.tokens[i+4].type == TokenType.ASSIGN:
            return True
        elif i + 4 <= len(self.tokens)-1 \
                and self.tokens[i+1].value == 'this' \
                and self.tokens[i+2].type == TokenType.ACCESS \
                and self.tokens[i+3].type == TokenType.IDENTIFIER \
                and self.tokens[i+4].type == TokenType.ASSIGN:
            return True
        return False


    def PredictVarInit(self) -> bool:
        i = self.currTokenIndex
        if i + 1 <= len(self.tokens)-1 \
                and self.tokens[i+1].value == 'int':
            return True
        if i + 1 <= len(self.tokens)-1 \
                and self.tokens[i+1].value == 'str':
            return True
        if i + 2 <= len(self.tokens)-1 \
                and self.tokens[i+1].type == TokenType.IDENTIFIER \
                and self.tokens[i+2].type == TokenType.IDENTIFIER:
            return True
        return False


    def CalculateLocationOfVariableInStackFromTop(self, varName:str):
        # calculates distance between variable varName in stack and 
        # start of stack frame (in EBP register) in bytes.
        # Uses to get or set value of a variable, ex. [ebp - 8]
        localTable = self.localSymbolTable
        data = localTable.FindSymbolGlobal(varName)
        if data == None:
            raise Exception('Unexpected variable!')
        dwLength = 4 # length in double words (4 bytes)
        for symbolData in localTable.symbolsData:
            if symbolData == data:
                return dwLength
            else:
                if symbolData.type == 'int':
                    dwLength += 4
                elif symbolData.type == 'str':
                    continue
                else: 
                    dwLength += 4 * len(self.definedClasses[symbolData.type].vars)
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
                    elif symbolData.type == 'str':
                        continue
                    else: 
                        dwLength += 4 * len(self.definedClasses[symbolData.type].vars)


    def VarInit(self):
        try:
            self.GetNextToken()
            if self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'int'):
                # int var init
                localVarName = self.GetNextToken().value
                # check if var name is available
                if not self.localSymbolTable.IsNameFreeInScope(localVarName):
                    raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
                elif localVarName in self.definedClasses.keys():
                    raise Exception('Variable with name ' + localVarName + " can't be declared, because this name has been already occupied by class!")
                
                self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'int'))

                if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                    raise Exception()

                rvalue = self.GetRValueWithExpectedType('int')
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                        'SUB ESP, 4 \n' \
                                        + rvalue.codeWithAddressOrValueInEAX \
                                        + 'MOV [ESP], EAX \n'

            elif self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER):
                # local complex var init
                objType = self.GetCurrentToken().value
                if objType not in self.definedClasses.keys():
                    raise Exception('Undefined type ' + objType + '!')

                if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()

                objName = self.GetCurrentToken().value
                if not self.localSymbolTable.IsNameFreeInScope(objName):
                    raise Exception('Variable with name ' + objName + ' has been already defined!')
                elif objName in self.definedClasses.keys():
                    raise Exception('Variable with name ' + objName + " can't be declared, because this name has been already occupied by class!")
                
                self.localSymbolTable.AddSymbol(SymbolData(objName, objType))

                if not self.Match(self.GetNextToken(), TokenType.ASSIGN) \
                        or not self.Match(self.PeekNextToken(), TokenType.IDENTIFIER):
                    # peek because self.GetRValue will read next token and it expects IDENTIFIER
                    raise Exception()

                rightName = self.PeekNextToken().value
                # peek because self.GetRValue will read next token and expect IDENTIFIER
                if rightName in self.definedClasses.keys() \
                        and self.Match(self.GetNextToken(), TokenType.IDENTIFIER) \
                        and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                        and self.Match(self.GetNextToken(), TokenType.KEYWORD, 'CreateInstance') \
                        and self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET) \
                        and self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET):
                    # constructor call
                    # check types
                    if objType != rightName:
                        raise Exception('Can\'t cast ' + objType + ' to ' + rightName + '!')
                    # allocate space in stack and set 0
                    for i in range(0, len(self.definedClasses[objType].vars)):
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'SUB ESP, 4 \n' \
                            + 'MOV [ESP], DWORD 0 \n'
                else:
                    rvalue = self.GetRValueWithExpectedType(objType)
                    # copy all variables of the right var
                    objLocation = self.CalculateLocationOfVariableInStackFromTop(objName)
                    rightLocation = self.CalculateLocationOfVariableInStackFromTop(rightName)
                    # EAX contains address of first variable of object
                    for i in range(0, len(self.definedClasses[objType].vars)):
                        self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                                'MOV EDX, [EAX - ' + str(rightLocation + i*4) + '] \n' \
                                + 'MOV [EBP - ' + str(objLocation + i*4) + '], EDX \n'

            elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'str'):
                # str var init
                localVarName = self.GetNextToken().value
                # check if var name is available
                if not self.localSymbolTable.IsNameFreeInScope(localVarName):
                    raise Exception('Variable with name ' + localVarName + ' has been already defined in local scope!')
                elif localVarName in self.definedClasses.keys():
                    raise Exception('Variable with name ' + localVarName + " can't be declared, because this name has been already occupied by class!")
                
                self.localSymbolTable.AddSymbol(SymbolData(localVarName, 'str'))

                if not self.Match(self.GetNextToken(), TokenType.ASSIGN) \
                        or not self.Match(self.GetNextToken(), TokenType.STRING_LITERAL):
                    raise Exception()

                self.dataSection += str(self.currentClassName) + '_' + self.currentMethodName + '_' + localVarName \
                            + ': db "' + self.GetCurrentToken().value[1:-1] + '", 0xA, 0 \n'

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def Assigning(self):
        try:
            lvalue = self.GetLValue()

            if not self.Match(self.GetNextToken(), TokenType.ASSIGN):
                raise Exception()

            if lvalue.lvalueType == LValueType.OBJECT_WITH_INT_VARIABLE:
                lvalueType = 'int'
            else:
                lvalueType = lvalue.varType

            if self.localSymbolTable.IsItMethodParamName(lvalue.varName) and lvalue.varType == 'int':
                raise Exception('It is prohibited to set value to method parameter of type <int>!')

            rvalue = self.GetRValueWithExpectedType(lvalueType)
            if lvalueType == 'int':
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            lvalue.codeWithAddressInEBX \
                            + rvalue.codeWithAddressOrValueInEAX \
                            + 'MOV [EBX], EAX \n'
            else:
                leftLocation = self.CalculateLocationOfVariableInStackFromTop(lvalue.varName)
                rightLocation = self.CalculateLocationOfVariableInStackFromTop(rvalue.varName)
                # EAX contains address of first variable of object
                for i in range(0, len(self.definedClasses[lvalue.varType].vars)):
                    self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                            'MOV EDX, [EAX - ' + str(rightLocation + i*4) + '] \n' \
                            + 'MOV [EBP - ' + str(leftLocation + i*4) + '], EDX \n'

            if not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                    raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def MethodCall(self):
        try:
            self.GetNextToken() # TokenType.IDENTIFIER                
            if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                # method defined in another class
                isMethodOfCurrentClass = False

                objName = self.GetCurrentToken().value
                objData = self.localSymbolTable.FindSymbolGlobal(objName)
                if objName == None:
                    raise Exception('Variable ' + objName + ' undefined in method ' + self.currentMethodName + '!')
                parentClass = objData.type

                self.GetNextToken() # TokenType.ACCESS
                self.GetNextToken() # TokenType.IDENTIFIER
            else:
                # next token O_ROUND_BRACKET, method definded in current class
                isMethodOfCurrentClass = True
                parentClass = self.currentClassName

            methodName = self.GetCurrentToken().value
            methodData = self.definedClasses[parentClass].FindMethodInList(methodName)
            if methodData == None:
                raise Exception('Method does not defined in class ' + parentClass + '!')
                    
            if not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            if methodData.paramName != None:
                rvalue = self.GetRValueWithExpectedType(methodData.paramType)
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        rvalue.codeWithAddressOrValueInEAX \
                        + 'PUSH EAX \n' 

            if isMethodOfCurrentClass:
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'PUSH DWORD [EBP + 8] \n' 
            else:
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'MOV EBX, EBP \n' \
                        + 'SUB EBX, ' + str(self.CalculateLocationOfVariableInStackFromTop(objName)) + '\n' \
                        + 'PUSH EBX \n'

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'CALL ' + '_' + parentClass + '_' + methodName + '\n'

            if methodData.paramName == None:
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'ADD ESP, 4 \n'
            else:
                self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'ADD ESP, 8 \n'

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()
            
        except Exception as ex:
            raise Exception(str(ex))


    def IfStatement(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'if') \
                    or not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            leftRValue = self.GetRValueWithExpectedType('int')
            
            # detect compare sign
            self.GetNextToken()
            if not (self.Match(self.GetCurrentToken(), TokenType.EQUAL) \
                    or self.Match(self.GetCurrentToken(), TokenType.GREATER) \
                    or self.Match(self.GetCurrentToken(), TokenType.GREATER_EQUAL) \
                    or self.Match(self.GetCurrentToken(), TokenType.LESS) \
                    or self.Match(self.GetCurrentToken(), TokenType.LESS_EQUAL)):
                raise Exception()
            cmpType = self.GetCurrentToken().type

            rightRValue = self.GetRValueWithExpectedType('int')

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        rightRValue.codeWithAddressOrValueInEAX \
                        + 'MOV EBX, EAX \n' \
                        + leftRValue.codeWithAddressOrValueInEAX \
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

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'ADD ESP, ' + str(len(self.localSymbolTable.GetLastTable().symbolsData)) + '\n'
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

            leftRValue = self.GetRValueWithExpectedType('int')
            
            # detect compare sign
            self.GetNextToken()
            if not (self.Match(self.GetCurrentToken(), TokenType.EQUAL) \
                    or self.Match(self.GetCurrentToken(), TokenType.GREATER) \
                    or self.Match(self.GetCurrentToken(), TokenType.GREATER_EQUAL) \
                    or self.Match(self.GetCurrentToken(), TokenType.LESS) \
                    or self.Match(self.GetCurrentToken(), TokenType.LESS_EQUAL)):
                raise Exception()
            cmpType = self.GetCurrentToken().type

            rightRValue = self.GetRValueWithExpectedType('int')

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.O_FIGURE_BRACKET):
                raise Exception()

            whileConditionLabel = '_while_condition_' + str(self.GetOriginalIdNum())
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        whileConditionLabel + ':'\
                        + rightRValue.codeWithAddressOrValueInEAX \
                        + 'MOV EBX, EAX \n' \
                        + leftRValue.codeWithAddressOrValueInEAX \
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

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'ADD ESP, ' + str(len(self.localSymbolTable.GetLastTable().symbolsData)) + '\n'

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
                    or not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            rvalue = self.GetRValueWithExpectedType('int')

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                rvalue.codeWithAddressOrValueInEAX \
                + 'PUSH EAX \n' \
                + 'CALL _Print \n' \
                + 'ADD ESP, 4 \n'

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
                raise Exception()
        except Exception as ex:
            raise Exception(str(ex))


    def PrintStringStatement(self):
        try:
            if not self.Match(self.GetNextToken(), TokenType.KEYWORD, 'prints') \
                    or not self.Match(self.GetNextToken(), TokenType.O_ROUND_BRACKET):
                raise Exception()

            self.GetNextToken()
            if self.Match(self.GetCurrentToken(), TokenType.IDENTIFIER):
                varName = self.GetCurrentToken().value
                varData = self.localSymbolTable.FindSymbolGlobal(varName)
                if varData.type != 'str':
                    raise Exception('String type expected!')
                strIdentifier = str(self.currentClassName) + '_' + self.currentMethodName + '_' + varName
            elif self.Match(self.GetCurrentToken(), TokenType.STRING_LITERAL):
                strIdentifier = str(self.currentClassName) + '_' + self.currentMethodName + '_' \
                        + str(self.GetOriginalIdNum())
                self.dataSection += strIdentifier + ': db "' + self.GetCurrentToken().value[1:-1] \
                        + '", 0xA, 0 \n'
            else:
                raise Exception('String type expected!')

            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'PUSH DWORD ' + strIdentifier + '\n' \
                        + 'CALL _PrintString \n' \
                        + 'ADD ESP, 4 \n'

            if not self.Match(self.GetNextToken(), TokenType.C_ROUND_BRACKET) \
                    or not self.Match(self.GetNextToken(), TokenType.SEMICOLON):
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
                        '_main: \n' \
                        + 'MOV EBP, ESP \n'
            
            self.localSymbolTable.Clear()

            self.Statements()

            # cleans up the stack
            self.listingsForClasses[self.currentClassName][self.currentMethodName] += \
                        'ADD ESP, ' + str(self.GetLocalVarsSize()) + '\n'

            if not self.Match(self.GetNextToken(), TokenType.C_FIGURE_BRACKET):
                raise Exception
        except Exception as ex:
            raise Exception(str(ex))


    def BuildCode(self) -> str:
        code = 'extern _printf \n\n'    \
                + self.dataSection + '\n'\
                + 'section .text \n'    \
                + 'global _main\n\n'    \
                + '_Print: \n'          \
                + 'PUSH EBP \n'         \
                + 'MOV EBP, ESP \n'     \
                + 'MOV EAX, [EBP+8] \n' \
                + 'PUSH EAX \n'         \
                + 'PUSH NumFormat \n'   \
                + 'CALL _printf \n'     \
                + 'SUB ESP, 8 \n'       \
                + 'MOV ESP, EBP \n'     \
                + 'POP EBP \n'          \
                + 'RET \n\n'            \
                + '_PrintString: \n'    \
                + 'PUSH EBP \n'         \
                + 'MOV EBP, ESP \n'     \
                + 'MOV EAX, [EBP+8] \n' \
                + 'PUSH EAX \n'         \
                + 'CALL _printf \n'     \
                + 'SUB ESP, 4 \n'       \
                + 'MOV ESP, EBP \n'     \
                + 'POP EBP \n'          \
                + 'RET \n\n'
        # place function for printing numbers at code start

        code += self.listingsForClasses[None]['main']

        code += 'XOR EAX, EAX \n'\
                + 'RET \n\n' # exit sequence

        for className in self.listingsForClasses.keys():
            if className != None:
                for methodName in self.listingsForClasses[className].keys():
                    code += self.listingsForClasses[className][methodName] 

        return code


    def GetLValue(self):
        # inspect next tokens for left value
        if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
            if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                lobjectData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if lobjectData == None:
                    raise Exception('Variable ' + self.GetCurrentToken().value + ' is undefined in method ' + self.currentMethodName + '!')
                lvalue = LValue(lobjectData.name, lobjectData.type, LValueType.OBJECT_WITH_INT_VARIABLE)
                self.GetNextToken()
                if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()
                lobjectVarName = self.GetCurrentToken().value
                if lobjectVarName not in self.definedClasses[lobjectData.type].vars:
                    raise Exception('Variable ' + lobjectVarName + ' is undefined in class ' + lobjectData.type + '!')
                lvalue.childVarName = lobjectVarName
            else:
                lvalueData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if lvalueData == None:
                    raise Exception('Variable ' + self.GetCurrentToken().value + ' is undefined in method ' + self.currentMethodName + '!')
                lvalue = LValue(lvalueData.name, lvalueData.type, LValueType.VARIABLE)
        elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
            lvalueName = self.GetCurrentToken().value
            if lvalueName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + lvalueName + ' is undefined in class ' + self.currentClassName + '!')
            lvalue = LValue(lvalueName, 'int', LValueType.VARIABLE_OF_CURRENT_CLASS)
        else:
            raise Exception()
        try:
            lvalue.codeWithAddressInEBX = self.PushVarAddressToEBX(lvalue)
            return lvalue
        except Exception as ex:
            raise Exception(str(ex))

    
    def GetRValueWithExpectedType(self, expType:str):
        # inspect next tokens for right value
        if self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
            if self.Match(self.PeekNextToken(), TokenType.ACCESS):
                robjectData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if robjectData == None:
                    raise Exception('Variable ' + self.GetCurrentToken().value + ' is undefined in method ' + self.currentMethodName + '!')
                rvalue = RValue(robjectData.name, robjectData.type, RValueType.OBJECT_WITH_INT_VARIABLE)
                self.GetNextToken()
                if not self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
                    raise Exception()
                robjectVarName = self.GetCurrentToken().value
                if robjectVarName not in self.definedClasses[robjectData.type].vars:
                    raise Exception('Variable ' + robjectVarName + ' is undefined in class ' + robjectData.type + '!')
                rvalue.childVarName = robjectVarName
                if expType != 'int':
                    raise Exception('Type ' + expType + ' expected! Got type int!')
            else:
                rvalueData = self.localSymbolTable.FindSymbolGlobal(self.GetCurrentToken().value)
                if rvalueData == None:
                    raise Exception('Variable ' + self.GetCurrentToken().value + ' is undefined in method ' + self.currentMethodName + '!')
                if rvalueData.type != expType:
                    raise Exception('Type ' + expType + ' expected! Got type ' + rvalueData.type + '!')
                rvalue = RValue(rvalueData.name, rvalueData.type, RValueType.VARIABLE)
        elif self.Match(self.GetCurrentToken(), TokenType.KEYWORD, 'this') \
                and self.Match(self.GetNextToken(), TokenType.ACCESS) \
                and self.Match(self.GetNextToken(), TokenType.IDENTIFIER):
            rvalueName = self.GetCurrentToken().value
            if rvalueName not in self.definedClasses[self.currentClassName].vars:
                    raise Exception('Variable ' + rvalueName + ' is undefined in class ' + self.currentClassName + '!')
            if expType != 'int':
                    raise Exception('Type ' + expType + ' expected! Got type int!')
            rvalue = RValue(rvalueName, 'int', RValueType.VARIABLE_OF_CURRENT_CLASS)
        elif self.Match(self.GetCurrentToken(), TokenType.NUMBER):
            if expType != 'int':
                    raise Exception('Type ' + expType + ' expected! Got type int!')
            rvalue = RValue(self.GetCurrentToken().value, 'int', RValueType.NUMBER)
        else:
            raise Exception()
        try:
            rvalue.codeWithAddressOrValueInEAX = self.PushVarAddressOrValueToEAX(rvalue)
            return rvalue
        except Exception as ex:
            raise Exception(str(ex))


    def GetLocalVarsSize(self) -> int:
        # returns size in bytes of local variables
        size = 0
        for varData in self.localSymbolTable.GetLastTable().symbolsData:
            if varData.type == 'int':
                size += 4
            elif varData.type == 'str':
                continue
            else:
                size += len(4*self.definedClasses[varData.type].vars)
        return size


    def PushVarAddressToEBX(self, lvalue:LValue) -> str:
        if lvalue.lvalueType == LValueType.VARIABLE:
            if self.localSymbolTable.IsItMethodParamName(lvalue.varName):
                return 'MOV EBX, [EBP + 12]\n'
            else:
                return 'MOV EBX, EBP\nSUB EBX, ' + str(self.CalculateLocationOfVariableInStackFromTop(lvalue.varName)) + '\n'
        elif lvalue.lvalueType == LValueType.OBJECT_WITH_INT_VARIABLE:
            if self.localSymbolTable.IsItMethodParamName(lvalue.varName):
                return 'MOV EBX, [EBP + 12]\n SUB EBX, ' \
                    + str(4*self.definedClasses[lvalue.varType].vars.index(lvalue.childVarName)) + '\n'
            else:
                return 'MOV EBX, EBP\nSUB EBX, ' + str(self.CalculateLocationOfVariableInStackFromTop(lvalue.varName) \
                    + 4*self.definedClasses[lvalue.varType].vars.index(lvalue.childVarName)) + '\n'
        elif lvalue.lvalueType == LValueType.VARIABLE_OF_CURRENT_CLASS:
            return 'MOV EBX, [EBP + 8] \nSUB EBX, ' \
                    + str(4*self.definedClasses[self.currentClassName].vars.index(lvalue.varName)) + '\n'
        else:
            raise Exception()


    def PushVarAddressOrValueToEAX(self, rvalue:RValue) -> str:
        if rvalue.rvalueType == RValueType.VARIABLE:
            if self.localSymbolTable.IsItMethodParamName(rvalue.varName):
                if rvalue.varType == 'int':
                    return 'MOV EAX, [EBP + 12] \n'
                else:
                    return 'MOV EAX, [EBP + 12] \n'
            else:
                if rvalue.varType == 'int':
                    return 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rvalue.varName)) + ']\n'
                else:
                    return 'MOV EAX, EBP\nSUB EAX, ' + str(self.CalculateLocationOfVariableInStackFromTop(rvalue.varName)) + '\n'
        elif rvalue.rvalueType == RValueType.OBJECT_WITH_INT_VARIABLE:
            if self.localSymbolTable.IsItMethodParamName(rvalue.varName):
                return 'MOV EAX, [EBP + 12]\nMOV EAX, [EAX - ' \
                    + str(4*self.definedClasses[rvalue.varType].vars.index(rvalue.childVarName)) + ']\n'
            else:
                return 'MOV EAX, [EBP - ' + str(self.CalculateLocationOfVariableInStackFromTop(rvalue.varName) \
                    + 4*self.definedClasses[rvalue.varType].vars.index(rvalue.childVarName)) + ']\n'
        elif rvalue.rvalueType == RValueType.VARIABLE_OF_CURRENT_CLASS:
            return 'MOV EAX, [EBP + 8] \nMOV EAX, [EAX - ' \
                    + str(4*self.definedClasses[self.currentClassName].vars.index(rvalue.varName)) + ']\n'
        elif rvalue.rvalueType == RValueType.NUMBER:
            return 'MOV EAX, DWORD ' + self.GetCurrentToken().value + '\n'
        else:
            raise Exception()   
