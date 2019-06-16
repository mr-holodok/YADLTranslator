import sys
import os
from Parser import Parser
from Parser import Token
from SyntaxAnalyzer import SyntaxAnalyzer

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python YADLTranslator.py Path/To/File.txt')
        exit()
    if not os.path.exists(sys.argv[1]):
        print('Check path to file! File doesn\'t exist!')
        exit()
    try:
        tokens = Parser.Parse(sys.argv[1])
        syntaxAnalyzer = SyntaxAnalyzer(tokens)
        syntaxAnalyzer.Analyze()
        code = syntaxAnalyzer.BuildCode()
        outFileName = sys.argv[1][0:sys.argv[1].rindex('\\')+1] + 'out.asm'
        outFile = open(outFileName, 'w')
        outFile.write(code)
        outFile.close()
        print('Succesfully translated! Location: ' + outFileName)
    except Exception as Ex:
        print(Ex)