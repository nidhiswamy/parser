import re

# Token definitions
tokens = [
        ('INT', r'int'),
        ('BOOL', r'bool'),
        ('FLOAT', r'float'),
        ('CHAR', r'char'),
        ('STRING', r'string'),
        ('ARR', r'type\[\d+\]'),
        ('ID', r'[a-zA-Z_]\w*'),
        ('NUMBER', r'\d+'),
        ('PRINT', r'print'),
        ('READ', r'read'),
        ('ASSIGN', r'='),
        ('SEMICOLON', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('OPERATOR', r'[+\-*/<>=!&|]'),
    ]

# Whitespaces
ignore = r'[ \n]+|*'

# Combined regular expression
pattern = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in tokens + [('IGNORE', ignore)]))

# def isKeyword(token):
#     keywords = r'(int|float|bool|char|string|print|read)[0-9]*'
#     return re.match(keywords, token) is not None
#
# def isIdentifier(token):
#     identifiers = r'([a-z]|[A-z}|_)+[0-9]*([a-z]|[A-Z]|_)*'
#     return re.match(identifiers, token) is not None
#
# def isOperator(token):
#     operators = ["+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!=", "&&", "||", "!"]
#     # operators = r'(+|-|*|/|<|<=|>|>=|==|!=|&&|\|\||!)'
#     return token in operators
#
# def isLiteral(token):
#     # literals = r'[0-9]*'
#     return token.isdigit()
#
# def isDelim(token):
#     delimiters = ["\n"]
#     return token in delimiters

def tokenize(code):
    # lines = code.split("\n")
    # words = []
    # 
    # tokens = []
    # for line in lines:
    #     words = line.split(" ")

    for match in re.finditer(pattern, code):
        if match.lastgroup == 'IGNORE':
            continue
        if match.lastgroup is not None:
            value = match.group(match.lastgroup)
            yield (match.lastgroup, value)

import re

# Token definitions
tokens = [
    ('INT', r'int'),
    ('BOOL', r'bool'),
    ('FLOAT', r'float'),
    ('CHAR', r'char'),
    ('STRING', r'string'),
    ('TYPE', r'type\[\d+\]'),
    ('ID', r'[a-zA-Z_]\w*'),
    ('NUMBER', r'\d+'),
    ('STRING_LITERAL', r'"(\\.|[^"])*"'),
    ('PRINT', r'print'),
    ('READ', r'read'),
    ('ASSIGN', r'='),
    ('SEMICOLON', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('OPERATOR', r'[+\-*/<>=!&|]'),
]

# Regular expression for white space and comments
ignore = r'[ \t\r\n]+|//.*'

# Combined regex pattern
pattern = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in tokens + [('IGNORE', ignore)]))

# Tokenizer function
def tokenize(program):
    for match in re.finditer(pattern, program):
        if match.lastgroup == 'IGNORE':
            continue
        value = match.group(match.lastgroup)
        yield (match.lastgroup, value)

# Parser
def parse(program):
    tokens = tokenize(program)
    try:
        parse_program(tokens)
        print("Valid input")
    except Exception as e:
        print("Invalid input:", e)

def parse_program(tokens):
    for token in tokens:
        if token[0] in ['INT', 'BOOL', 'FLOAT', 'CHAR', 'STRING']:
            parse_declaration(tokens)
        elif token[0] == 'ID':
            parse_assignment(tokens)
        elif token[0] == 'PRINT':
            parse_print_statement(tokens)
        elif token[0] == 'READ':
            parse_read_statement(tokens)
        else:
            raise SyntaxError(f"Unexpected token: {token[0]}")

def parse_declaration(tokens):
    data_type = next(tokens)
    identifier = next(tokens)
    if data_type[0] == 'TYPE':
        number = int(data_type[1].split('[')[1][:-1])
        parse_data_type(tokens)
    elif data_type[0] == 'ID':
        number = None
    else:
        raise SyntaxError(f"Invalid data type: {data_type[1]}")
    
    if identifier[0] != 'ID':
        raise SyntaxError(f"Expected an identifier, got {identifier[0]}: {identifier[1]}")
    
    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Expected ';', got {next_token[0]}: {next_token[1]}")

def parse_data_type(tokens):
    next_token = next(tokens)
    if next_token[0] != 'ID':
        raise SyntaxError(f"Expected an identifier, got {next_token[0]}: {next_token[1]}")

def parse_assignment(tokens):
    identifier = next(tokens)
    if identifier[0] != 'ID':
        raise SyntaxError(f"Expected an identifier, got {identifier[0]}: {identifier[1]}")
    
    next_token = next(tokens)
    if next_token[0] != 'ASSIGN':
        raise SyntaxError(f"Expected '=', got {next_token[0]}: {next_token[1]}")
    
    parse_expression(tokens)

def parse_expression(tokens):
    # Implement expression parsing logic here
    pass

def parse_print_statement(tokens):
    next_token = next(tokens)
    if next_token[0] != 'LPAREN':
        raise SyntaxError(f"Expected '(', got {next_token[0]}: {next_token[1]}")
    
    parse_expression(tokens)
    
    next_token = next(tokens)
    if next_token[0] != 'RPAREN':
        raise SyntaxError(f"Expected ')', got {next_token[0]}: {next_token[1]}")

def parse_read_statement(tokens):
    next_token = next(tokens)
    if next_token[0] != 'LPAREN':
        raise SyntaxError(f"Expected '(', got {next_token[0]}: {next_token[1]}")
    
    identifier = next(tokens)
    if identifier[0] != 'ID':
        raise SyntaxError(f"Expected an identifier, got {identifier[0]}: {identifier[1]}")
    
    next_token = next(tokens)
    if next_token[0] != 'RPAREN':
        raise SyntaxError(f"Expected ')', got {next_token[0]}: {next_token[1]}")

# Test the parser
input_text = """
int a;
bool b;
float arr[3] = 1.0;
char c;
string s;
int arr2[2][2] = 1;
x = 10;
print("Hello, World!");
read(y);
"""
parse(input_text)
