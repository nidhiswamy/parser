import sys
import re
import numpy as np

def read_files(filepath):
    try:
        with open(filepath, 'r') as file:
            code = file.read()
        print(f"\nInput from {filepath}:\n\n{code}")
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
        ('ARR', r'(\[\d+\])+'),
        ('PRINT', r'print'),
        ('READ', r'read'),
        ('TRUE', r'true'),
        ('FALSE', r'false'),
        ('ID', r'[a-zA-Z_]\w*'),
        ('NUMBER', r'\d+'),
        ('ASSIGN', r'='),
        ('SEMICOLON', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('COMMA', r',\s{0,1}'),
        ('BOOLOP', r'[&]{2}|[|]{2}|!'),
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
        # if token[0] == 'ARR':
        #     parse_arrays(tokens)

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
    data_type = next(tokens)
    next_token = next(tokens)

    # Identifiers
    if data_type[0] == 'ID':
        print(f"Token ID = {data_type}")
        # Variable with dimension = 0 (non-array)
        symbol_table[data_type[1]] = (curr_token[0], 0)
        # print(f"TOKEN = {symbol_table.get(data_type[1])}")
        # data_type = symbol_table.get(data_type[1])

        # Array handling
        if next_token[0] != 'SEMICOLON' and next_token[0] == 'ARR':
            numbers = [int(num) for num in next_token[1].strip('[]').split('][')]
            symbol_table[data_type[1]] = (curr_token[0], numbers)
            # print(f"TOKEN in symbol table = {symbol_table.get(next_token[1])}")
            data_type = symbol_table.get(next_token[1])
        # TODO: This is not considering next_token from line -16
            next_token = next(tokens)
        print(f"Next token = {next_token}")
    else:
        raise SyntaxError(f"Invalid data type: {data_type[1]}")

    symbol_table[next_token[1]] = data_type

    if next_token[0] == 'ASSIGN':
        raise SyntaxError("Declaration and assignment at the same time.")

    if next_token[0] != 'SEMICOLON':
        print(f"TOKEN = {next_token[0]}")
        raise SyntaxError(f"Declarations need to end with a semicolon (;)")

    symbol_table[next_token[1]] = data_type

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

    parse_expression(tokens, curr_token)

# Parsing all expressions (eg. a = 4 * 5;)
def parse_expression(tokens, curr_token):
    next_token = next(tokens)
    assigned_type = symbol_table.get(next_token[1])
    declared_type = symbol_table.get(curr_token[1])

    # Implementing type checking
    if (next_token[0] != 'NUMBER' and next_token[0] != 'TRUE' and next_token[0] != 'FALSE' and next_token[0] != 'LBRACE') and declared_type != assigned_type:
        print(f"Token = {next_token}")
        raise SyntaxError(f"Inconsistent type assignments of {declared_type} and {assigned_type}")

    # Boolean expression
    elif next_token[0] == 'TRUE' or next_token[0] == 'FALSE':
        print(f"Token here = {next_token}")
        operator = next(tokens)
        print(f"Operator = {operator}")
        if operator[0] != 'BOOLOP' and operator[0] != 'SEMICOLON':
            print(f"Operator = {operator}")
            raise SyntaxError("No valid operator in boolean expression.")
        op2 = next(tokens)
        print(f"OP2 = {op2}")
        if op2[0] != 'TRUE' and op2[0] != 'FALSE':
            raise SyntaxError(f"Inconsistent operations of types {next_token} and {op2}")

    # Array initialization
    elif next_token[0] == 'LBRACE':
        next_token = next(tokens)
        # array_size = array_table[next_token[0]]
        value = symbol_table.get(curr_token[1])
        if value is None:
            raise SyntaxError("No such value initialized")
        print(f"Current token's symbol = {value[1]}")
        array_type = value[0]
        dimension = value[1]
        print(f"New array = {dimension}")
        array_size = len(dimension)
        print(f"Array size = {array_size}")

        # Iterating through array sizes
        for i in range(array_size):
            # Iterating through the dimensions
            next_token = next(tokens)
            print(f"Next token = {next_token}")
            if next_token[0] != 'LBRACE' and next_token[0] != 'NUMBER':
                raise SyntaxError("Expected {.")
            for num in dimension:
                next_token = next(tokens)
                print(f"Next token type = {next_token[0]}")
                print(f"Array type = {array_type}")
                if next_token[0] != array_type:
                    raise SyntaxError(f"Inconsistent type assignments for {array_type} array")

                # Comma
                next_token = next(tokens) 
                print(f"Next token = {next_token}")
                if next_token[0] != 'COMMA':
                   raise SyntaxError(f"Array dimensions do not match")
            next_token = next(tokens)
            print(f"Next token = {next_token}")
            if next_token[0] != 'RBRACE':
                raise SyntaxError("Array dimensions do not match")
            next_token = next(tokens)
            print(f"Next token = {next_token}")
            if next_token[0] != 'COMMA':
                raise SyntaxError(f"Dimension of array = {array_size}")

    # Type-checking assignment of two variables
    elif next_token[0] == 'ID':
        print(f"Token here = {next_token}")
        if declared_type != assigned_type:
            raise SyntaxError(f"Inconsistent type assignments of {declared_type} and {assigned_type}")

    # If expression uses an operator and operands
    elif next_token[0] == 'NUMBER':
        print(f"Token here = {next_token}")
        operator = next(tokens)
        if operator[0] == 'SEMICOLON':
            return
        if operator[0] != 'OPERATOR':
            raise SyntaxError(f"Invalid operator {operator[1]}")
        op2 = next(tokens)
        if op2[0] != 'NUMBER':
            raise SyntaxError(f"Invalid second operand {op2[0]}")

    # Statements have to end with a semicolon
    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        print(f"TOKEN at semicolon = {next_token}")
        raise SyntaxError(f"Statements need to end with a semicolon (;)")


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
        print(f"RPAREN = {next_token}")
        raise SyntaxError(f"Expected ')' to end read statement")
        
    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        print(f"TOKEN = {next_token}")
        raise SyntaxError(f"Statements need to end with semicolons (;)")

def main(filepath):
    code = read_files(filepath)
    tokens = tokenize(code)
    parse(tokens)
    print(f"SYMBOL TABLE = {symbol_table}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py filename.txt")
    else: 
        filepath = sys.argv[1]
        main(filepath)
