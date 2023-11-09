import sys
import re
import itertools

def read_files(filepath):
    try:
        with open(filepath, 'r') as file:
            code = file.read()
        print(f"File {filepath} opened!")
        return code
    except FileNotFoundError:
        print(f"File {filepath} not found!")

# Token definitions
token_definitions = [
        ('INT', r'int'),
        ('BOOL', r'bool'),
        ('FLOAT', r'float'),
        ('CHAR', r'char'),
        ('STRING', r'string'),
        ('ARR', r'type\[\d+\]'),
        ('PRINT', r'print'),
        ('READ', r'read'),
        ('ID', r'[a-zA-Z_]\w*'),
        ('NUMBER', r'\d+'),
        ('ASSIGN', r'='),
        ('SEMICOLON', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('OPERATOR', r'[+\-*/<>=!&|]'),
    ]

# Whitespaces
# ignore = r'[ \n]+|*'

# Combined regular expression
pattern = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in token_definitions))
# + [('IGNORE', ignore)]))

def tokenize(code):
    for match in re.finditer(pattern, code):
        # if match.lastgroup == 'IGNORE':
        #     continue
        if match.lastgroup is not None:
            value = match.group(match.lastgroup)
            yield (match.lastgroup, value)
    return

# Symbol table to keep track of data types
symbol_table = {}

def parse(tokens):
    try:
        parse_code(tokens)
        print("Valid input")
    except Exception as e:
        print("Invalid input: ", e)

def parse_code(tokens):
    data_types = ['INT', 'BOOL', 'FLOAT', 'CHAR', 'STRING']

    for token in tokens:
        # Declarations
        print(f"TOKEN = {token}\n")
        if token[0] in data_types: 
            parse_datatypes(tokens, token)

        # Initializing declared variables
        elif token[0] == 'ID':
            parse_assignment(tokens, token)

        # Print statements
        elif token[0] == 'PRINT':
            parse_print(tokens)

        # Read statements
        elif token[0] == 'READ':
            parse_read(tokens)

        # If a statement does not start with the above, raise error
        else:
            raise SyntaxError(f"Unexpected start token: {token[0]}")

# Parsing datatypes - int, bool, float, char, string
def parse_datatypes(tokens, curr_token):
    # curr_token has the data type of the identifier 
    # data_type = curr_token
    # identifier = next(tokens)
    data_type = next(tokens)
    identifier = next(tokens)

    # Array with type[number]
    if data_type[0] == 'ARR':
        # number = int(data_type[1].split('[')[1][:-1])
        next_token = next(tokens)
        if next_token[0] != 'ID':
            raise SyntaxError(f"ARR: Expected an identifier, got {next_token[0]}: {next_token[1]}")
        data_type = symbol_table.get(next_token[1])
    elif data_type[0] == 'ID':
        # number = 0
        symbol_table[data_type[1]] = curr_token
        print(f"declared {data_type[1]} for {data_type[0]}")
        data_type = symbol_table.get(data_type[1])
    else:
        raise SyntaxError(f"Invalid data type: {data_type[1]}")

    # if identifier[0] != 'ID':
    #     raise SyntaxError(f"ID: Expected an identifier, got {identifier[0]}: {identifier[1]}")
    symbol_table[identifier[1]] = data_type

    if identifier[0] == 'ASSIGN':
        raise SyntaxError("Declaration and assignment at the same time.")

    if identifier[0] != 'SEMICOLON':
        raise SyntaxError(f"Declarations need to end with semicolons (;)")

    symbol_table[identifier[1]] = data_type

    # next_token = next(peek)
    # if next_token is not None and next_token[0] == 'ASSIGN':
    #     raise SyntaxError(f"Declaration and assignment at the same time.")

# Parsing all assignments (eg. a = (expression);)
def parse_assignment(tokens, curr_token):
    identifier = curr_token
    next_token = next(tokens)
    print(f"identifier = {identifier[1]}")

    declared_type = symbol_table.get(curr_token[1])
    if declared_type is None:
        raise SyntaxError(f"Variable {curr_token[1]} is not declared")

    if next_token[0] != 'ASSIGN':
        raise SyntaxError(f"Expected '='")

    parse_expression(tokens, declared_type)

# Parsing all expressions (eg. a = 4 * 5;)
def parse_expression(tokens, declared_type):
    next_token = next(tokens)

    assigned_type = symbol_table.get(next_token[1])

    # Implementing type checking
    if next_token[0] != 'NUMBER' and declared_type != assigned_type:
        raise SyntaxError(f"Inconsistent type assignments of {declared_type} and {assigned_type}")

    # If expression uses an operator and operands
    if next_token[0] == 'NUMBER':
        # First operand
        # op1 = next_token
        # print(f"TOKEN = {op1}")
        operator = next(tokens)
        if operator[0] != 'OPERATOR':
            raise SyntaxError(f"Invalid operator {operator[1]}")
        op2 = next(tokens)
        if op2[0] != 'NUMBER':
            raise SyntaxError(f"Invalid second operand {op2[0]}")

    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Statements need to end with semicolons (;)")


# Parsing the print(a); statement
def parse_print(tokens):
    next_token = next(tokens)
    if next_token[0] != 'LPAREN':
        raise SyntaxError(f"Expected '(' after keyword 'print'")
    
    # Identifier printing
    identifier = next(tokens)
    if identifier[0] != 'ID' and identifier[0] != "\"":
        raise SyntaxError(f"Expected an identifier")

    # String literal printing
    if identifier[0] == "\"":
        next_token = next(tokens)
        if next_token[0] != 'STRING':
            raise SyntaxError("No string inside of print statement")
        next_token = next(tokens)
        if next_token[0] != "\"":
            raise SyntaxError("print(string) does not have closing quotes")

    next_token = next(tokens)
    if next_token[0] != 'RPAREN':
        raise SyntaxError(f"Expected ')' to end print statement")
        
    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        print(f"token = {next_token}")
        raise SyntaxError(f"Statements need to end with semicolons (;)")

# Parsing the read(a); statement
def parse_read(tokens):
    next_token = next(tokens)
    if next_token[0] != 'LPAREN':
        raise SyntaxError(f"Expected '(' after keyword 'read'")

    identifier = next(tokens)
    if identifier[0] != 'ID':
        raise SyntaxError(f"Expected an identifier")

    declared_type = symbol_table.get(identifier[1])
    if declared_type is None:
        raise SyntaxError(f"Variable {identifier[1]} is not declared")

    next_token = next(tokens)
    if next_token[0] != 'RPAREN':
        raise SyntaxError(f"Expected ')' to end read statement")
        
    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Statements need to end with semicolons (;)")

def main(filepath):
    code = read_files(filepath)
    print("INPUT: \n")
    print(code)
    tokens = tokenize(code)
    parse(tokens)
    # print("after tokenize?")
    # print("Printing main")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py filename.txt")
    else: 
        filepath = sys.argv[1]
        main(filepath)
