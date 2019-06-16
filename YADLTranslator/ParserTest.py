import unittest
from Parser import Parser
from Token import TokenType
from Token import Token

class Test_Parser(unittest.TestCase):
    def test_Id_recognition(self):
        fileName = 'tempTest.txt'
        open(fileName, 'w+').write('clas id id5 ind i12')
        tokens = Parser.Parse(fileName)
        self.assertEqual(len(tokens), 5)
        for t in tokens:
            self.assertEquals(t.type, TokenType.IDENTIFIER)


    def test_num_recognition(self):
        fileName = 'tempTest.txt'
        open(fileName, 'w+').write('12 -5 0 12345')
        tokens = Parser.Parse(fileName)
        self.assertEqual(len(tokens), 4)
        for t in tokens:
            self.assertEquals(t.type, TokenType.NUMBER)

    def test_num_with_error(self):
        fileName = 'tempTest.txt'
        open(fileName, 'w+').write('12 -5 0 12345a')
        self.failUnlessRaises(Exception, Parser.Parse)

    def test_keywords(self):
        fileName = 'tempTest.txt'
        open(fileName, 'w+').write('class this      CreateInstance int if \n main while')
        tokens = Parser.Parse(fileName)
        self.assertEqual(len(tokens), 7)
        for t in tokens:
            self.assertEquals(t.type, TokenType.KEYWORD)

    def test_complex(self):
        fileName = 'tempTest.txt'
        open(fileName, 'w+').write('class { int a =-55; met(coco c) {c.call()}}')
        tokens = Parser.Parse(fileName)
        self.assertEqual(len(tokens), 20)
        self.assertEqual(tokens[0].type, TokenType.KEYWORD)
        self.assertEqual(tokens[1].type, TokenType.O_FIGURE_BRACKET)
        self.assertEqual(tokens[2].type, TokenType.KEYWORD)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[4].type, TokenType.ASSIGN)
        self.assertEqual(tokens[5].type, TokenType.NUMBER)
        self.assertEqual(tokens[6].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[7].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[8].type, TokenType.O_ROUND_BRACKET)
        self.assertEqual(tokens[9].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[10].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[11].type, TokenType.C_ROUND_BRACKET)
        self.assertEqual(tokens[12].type, TokenType.O_FIGURE_BRACKET)
        self.assertEqual(tokens[13].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[14].type, TokenType.ACCESS)
        self.assertEqual(tokens[15].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[16].type, TokenType.O_ROUND_BRACKET)
        self.assertEqual(tokens[17].type, TokenType.C_ROUND_BRACKET)
        self.assertEqual(tokens[18].type, TokenType.C_FIGURE_BRACKET)
        self.assertEqual(tokens[19].type, TokenType.C_FIGURE_BRACKET)


if __name__ == '__main__':
    unittest.main()