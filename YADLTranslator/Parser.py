from enum import Enum
from Token import Token
from Token import TokenType

class ParseState(Enum):
    """Enum of states for finite state machine in Parser"""
    INITIAL = 1
    ID = 2
    NUM = 3


class Parser(object):
    """Class that performs parsing of an input file that contains YADL
    language and returns recognized tokens if no errors were found"""

    @staticmethod
    def Parse(filePath:str):
        try: 
            srcFile = open(filePath).read();
        except Exception:
            raise IOError()
        state = ParseState.INITIAL
        currLineNum = 1
        currCharNum = 0
        tokenValue = ''
        tokens = list()
        keywords = set(['class', 'int', 'main', 'CreateInstance', 'this', 'if', 'while', 'print'])
        i = 0
        while (i < len(srcFile)):
            c = srcFile[i]
            currCharNum += 1
            if state == ParseState.INITIAL:
                if c.isalpha():
                    state = ParseState.ID
                    tokenValue = c
                elif c.isnumeric() or c == '-':
                    state = ParseState.NUM
                    tokenValue = c
                elif c == '\n':
                    currLineNum += 1
                    currCharNum = 0
                elif c == ' ' or c == '\r':
                    pass
                elif c == '\t':
                    currCharNum += 2
                elif c == '{':
                    tokens.append(Token(TokenType.O_FIGURE_BRACKET, '{', currLineNum, currCharNum))
                elif c == '}':
                    tokens.append(Token(TokenType.C_FIGURE_BRACKET, '}', currLineNum, currCharNum))
                elif c == '(':
                    tokens.append(Token(TokenType.O_ROUND_BRACKET, '(', currLineNum, currCharNum))
                elif c == ')':
                    tokens.append(Token(TokenType.C_ROUND_BRACKET, ')', currLineNum, currCharNum))
                elif c == '=':
                    if i+1 < len(srcFile) and srcFile[i+1] == '=':
                        tokens.append(Token(TokenType.EQUAL, '==', currLineNum, currCharNum))
                        i += 1
                        currCharNum += 1
                    else:
                        tokens.append(Token(TokenType.ASSIGN, '=', currLineNum, currCharNum))
                elif c == '>':
                    if i+1 < len(srcFile) and srcFile[i+1] == '=':
                        tokens.append(Token(TokenType.GREATER_EQUAL, '>=', currLineNum, currCharNum))
                        i += 1
                        currCharNum += 1
                    else:
                        tokens.append(Token(TokenType.GREATER, '>', currLineNum, currCharNum))
                elif c == '<':
                    if i+1 < len(srcFile) and srcFile[i+1] == '=':
                        tokens.append(Token(TokenType.LESS_EQUAL, '<=', currLineNum, currCharNum))
                        i += 1
                        currCharNum += 1
                    else:
                        tokens.append(Token(TokenType.LESS, '<', currLineNum, currCharNum))
                elif c == ';':
                    tokens.append(Token(TokenType.SEMICOLON, ';', currLineNum, currCharNum))
                elif c == '.':
                    tokens.append(Token(TokenType.ACCESS, '.', currLineNum, currCharNum))
                else:
                    raise Exception('Unsupported character at line: ' + str(currLineNum) +\
                                    ' and position: ' + str(currCharNum))
            elif state == ParseState.ID:
                if c.isalnum():
                    tokenValue += c
                elif tokenValue in keywords:
                    tokens.append(Token(TokenType.KEYWORD, tokenValue, currLineNum, currCharNum-len(tokenValue)))
                    state = ParseState.INITIAL
                    i -= 1    # handle this char in INITIAL block
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, tokenValue, currLineNum, currCharNum-len(tokenValue)))
                    state = ParseState.INITIAL
                    i -= 1    # handle this char in INITIAL block
            elif state == ParseState.NUM:
                if c.isnumeric():
                    tokenValue += c
                elif c == ';' or c == ' ' or c == '\n' or c == '\t':
                    num = int(tokenValue)
                    if num < -2147483648 or num > 2147483647:
                        raise Exception('Number should be in such bounds: [-2147483648 - 2147483647] !')
                    tokens.append(Token(TokenType.NUMBER, tokenValue, currLineNum, currCharNum-len(tokenValue)))
                    state = ParseState.INITIAL
                    i -= 1    # handle this char in INITIAL block
                else:
                    raise Exception('Unexpected char near the number token at line: ' + str(currLineNum) \
                                    + ' and position: ' + str(currCharNum))

            i += 1

        if state != ParseState.INITIAL:
            if state == ParseState.ID and tokenValue in keywords:
                tokens.append(Token(TokenType.KEYWORD, tokenValue, currLineNum, currCharNum-len(tokenValue)))
            elif state == ParseState.ID:
                tokens.append(Token(TokenType.IDENTIFIER, tokenValue, currLineNum, currCharNum-len(tokenValue)))
            elif state == ParseState.NUM:
                tokens.append(Token(TokenType.NUMBER, tokenValue, currLineNum, currCharNum-len(tokenValue)))
        
        return tokens


if __name__ == '__main__':
    try:
        tokens = Parser.Parse(r"E:\KNU\Object oriented program construction\Translator\yadl_test1.txt")
        for t in tokens:
            print(t.value + '\t')
    except Exception as e:
        print('Parser exception:')
        print(e)