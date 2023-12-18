import sys
import re

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
        ('CHARACTER', r'\'\w\''),
        ('STRINGS', r'".*"'),
        ('FLOATS', r'(\d+\.\d*)'),
        ('NUMBER', r'\d+'),
        ('ASSIGN', r'='),
        ('SEMICOLON', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('COMMA', r',\s{0,1}'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('BOOLOP', r'[&]{2}|[|]{2}|!'),
        ('OPERATOR', r'[+\-*/<>=!&|]'),
    ]

# Combined regular expression
pattern = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in token_definitions))

def tokenize(code):
    for match in re.finditer(pattern, code):
        if match.lastgroup is not None:
            value = match.group(match.lastgroup)
            yield (match.lastgroup, value)
    return

# Symbol table to keep track of data types
symbol_table = {}

def parse(tokens):
    try:
        parse_code(tokens)
        print("VALID INPUT")
    except Exception as e:
        print("INVALID,", e)

def parse_code(tokens):
    data_types = ['INT', 'BOOL', 'FLOAT', 'CHAR', 'STRING']

    # Go through all start tokens
    for index, token in enumerate(tokens):
        # Declarations
        if token[0] in data_types: 
            parse_datatypes(tokens, token, index)

        # Initializing declared variables
        elif token[0] == 'ID':
            parse_assignment(tokens, token, index)

        # Print statements
        elif token[0] == 'PRINT':
            parse_print(tokens, index)

        # Read statements
        elif token[0] == 'READ':
            parse_read(tokens, index)

        # Else, raise an error with an unexpected start token
        else:
            raise SyntaxError(f"Unexpected start token in line {index+1}: {token[0]}")

# Parsing datatypes - int, bool, float, char, string
def parse_datatypes(tokens, curr_token, index):
    data_type = next(tokens)
    next_token = next(tokens)

    # Identifiers
    if data_type[0] == 'ID':
        # Variable with dimension = 0 (non-array)
        symbol_table[data_type[1]] = (curr_token[0], 0)

        # Array handling
        if next_token[0] != 'SEMICOLON' and next_token[0] == 'ARR':
            numbers = [int(num) for num in next_token[1].strip('[]').split('][')]
            # Setting type and dimension of given array in symbol table
            symbol_table[data_type[1]] = (curr_token[0], numbers)
            data_type = symbol_table.get(next_token[1])
            next_token = next(tokens)
        # Handling multiple declarations
        elif next_token[0] == 'COMMA':
            next_token = next(tokens)
            if next_token[0] == 'ID':
                symbol_table[next_token[1]] = (curr_token[0], 0)
            else:
                raise SyntaxError(f"Line {index+1}: Invalid multiple declaration attempt")
            next_token = next(tokens)
    else:
        raise SyntaxError(f"Line {index+1}: Invalid data type - {data_type[1]}")

    if data_type is not None:
        symbol_table[next_token[1]] = (data_type[0], 0)
    else:
        symbol_table[next_token[1]] = (data_type, 0)


    # Start raising specific syntax error messages
    if next_token[0] == 'ASSIGN':
        raise SyntaxError(f"Line {index+1}: Declaration and assignment at the same time.")


    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Line {index+1}: Declarations need to end with a semicolon (;)")

    if data_type is not None:
        symbol_table[next_token[1]] = (data_type[0], 0)
    else:
        symbol_table[next_token[1]] = (data_type, 0)

# Parsing all assignments (eg. a = (expression);)
def parse_assignment(tokens, curr_token, index):
    next_token = next(tokens)

    declared_type = symbol_table.get(curr_token[1])
    if declared_type is None:
        raise SyntaxError(f"Line {index+1}: Variable '{curr_token[1]}' is not declared")

    if next_token[0] != 'ASSIGN':
        raise SyntaxError(f"Line {index+1}: Expected '='")

    parse_expression(tokens, curr_token, index)

# Parsing all expressions (eg. a = 4 * 5;)
def parse_expression(tokens, curr_token, index):
    next_token = next(tokens)
    # Obtaining current and next tokens type
    assigned_type = symbol_table.get(next_token[1])
    if assigned_type is None:
        assigned_type = (next_token[0], 0)
    declared_type = symbol_table.get(curr_token[1])
    if declared_type is not None:
        if declared_type[0] == 'FLOAT' and assigned_type[0] == 'FLOATS':
            assigned_type = declared_type;
        elif declared_type[0] == 'STRING' and assigned_type[0] == 'STRINGS':
            assigned_type = declared_type;
        elif declared_type[0] == 'CHAR' and assigned_type[0] == 'CHARACTER':
            assigned_type = declared_type;
        elif declared_type[0] == 'BOOL' and (assigned_type[0] == 'TRUE' or assigned_type[0] == 'FALSE'):
            assigned_type = declared_type;
        elif declared_type[0] == 'INT' and assigned_type[0] == 'NUMBER':
            assigned_type = declared_type;

    # Implementing type checking
    if next_token[0] != 'LBRACE' and declared_type != assigned_type:
        raise SyntaxError(f"Line {index+1}, Inconsistent type assignment of {declared_type} and {assigned_type}")

    # Boolean expression
    elif next_token[0] == 'TRUE' or next_token[0] == 'FALSE':
        operator = next(tokens)
        if operator[0] != 'BOOLOP' and operator[0] != 'SEMICOLON':
            raise SyntaxError(f"Line {index+1}, No valid operator in boolean expression.")
        op2 = next(tokens)
        if op2[0] != 'TRUE' and op2[0] != 'FALSE':
            raise SyntaxError(f"Line {index+1}, Inconsistent operations of types {next_token} and {op2}")

    # Array initialization
    elif next_token[0] == 'LBRACE':
        next_token = next(tokens)
        value = symbol_table.get(curr_token[1])
        if value is None:
            raise SyntaxError(f"Line {index+1}, No such value initialized")
        array_type = value[0]
        if array_type == 'INT':
            array_type = 'NUMBER'
        dimension = value[1]
        array_size = len(dimension)

        # Iterating through the array size
        for i in range(array_size):
            # Iterating through the dimensions of the array
            if next_token[0] != 'LBRACE' and next_token[0] != 'NUMBER':
                raise SyntaxError(f"Line {index+1}, Array initialization out of bounds")
            for j in range(dimension[i]):
                next_token = next(tokens)
                if next_token[0] != 'COMMA' and next_token[0] != array_type :
                    raise SyntaxError(f"Line {index+1}, Inconsistent type assignments for {array_type} array")

                # Comma
                if next_token[0] == 'COMMA':
                    continue
                next_token = next(tokens) 
                if j != dimension[i]-1 and next_token[0] != 'COMMA':
                   raise SyntaxError(f"Line {index+1}, Array dimensions do not match")
            if next_token[0] != 'RBRACE':
                raise SyntaxError(f"Line {index+1}, Array dimensions do not match")
            
            next_token = next(tokens)
            next_token = next(tokens)
            if i != array_size-1 and next_token[0] != 'LBRACE':
                raise SyntaxError(f"Line {index+1}, Dimension of array = {array_size}")
            if next_token[0] != 'SEMICOLON':
                next_token = next(tokens)

    # Character assignments
    elif next_token[0] == 'CHARACTER':
        next_token = next(tokens)

    # String assignments
    elif next_token[0] == 'STRINGS':
        next_token = next(tokens)

    # Float assignments
    elif next_token[0] == 'FLOATS':
        next_token = next(tokens)


    # Type-checking assignment of two variables
    elif next_token[0] == 'ID':
        if declared_type != assigned_type:
            raise SyntaxError(f"Line {index+1}, Inconsistent type assignment of {declared_type} and {assigned_type}")

    # If expression uses an operator and operands
    elif next_token[0] == 'NUMBER':
        operator = next(tokens)
        if operator[0] == 'SEMICOLON':
            return
        if operator[0] != 'OPERATOR':
            raise SyntaxError(f"Line {index+1}, Invalid operator {operator[1]}")
        op2 = next(tokens)
        if op2[0] != 'NUMBER':
            raise SyntaxError(f"Line {index+1}, Invalid second operand {op2[0]}")

    # Character expressions
    elif next_token[0] == 'CHAR':
        operator = next(tokens)
        if operator[0] == 'SEMICOLON':
            return
        if operator[0] != 'OPERATOR':
            raise SyntaxError(f"Line {index+1}, Invalid operator {operator[1]}")
        op2 = next(tokens)
        if op2[0] != 'NUMBER':
            raise SyntaxError(f"Line {index+1}, Invalid second operand {op2[0]}")

    # Statements have to end with a semicolon
    if next_token is not None and next_token[0] != 'SEMICOLON':
        next_token = next(tokens)

    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Line {index+1}, Statements need to end with a semicolon (;)")


# Parsing the print(a); statement
def parse_print(tokens, index):
    next_token = next(tokens)
    if next_token[0] != 'LPAREN':
        raise SyntaxError(f"Line {index+1}, Expected '(' after keyword 'print'")
    
    # Identifier and string literal printing
    identifier = next(tokens)
    if identifier[0] != 'STRINGS':
        if identifier[0] != 'ID':
            raise SyntaxError(f"Line {index+1}, Expected an identifier or string literal")
        if symbol_table.get(identifier[1]) is None:
            raise SyntaxError(f"Line {index+1}, Variable '{identifier[1]}' is not declared")

    next_token = next(tokens)
    if next_token[0] != 'RPAREN':
        raise SyntaxError(f"Line {index+1}, Expected ')' to end print statement")
        
    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Line {index+1}, Statements need to end with semicolons (;)")

# Parsing the read statement
def parse_read(tokens, index):
    next_token = next(tokens)
    if next_token[0] != 'LPAREN':
        raise SyntaxError(f"Line {index+1}, Expected '(' after keyword 'read'")

    identifier = next(tokens)
    if identifier[0] != 'ID':
        raise SyntaxError(f"Line {index+1}, Expected an identifier")
    if symbol_table.get(identifier[1]) is None:
        raise SyntaxError(f"Line {index+1}, Variable '{identifier[1]}' is not declared")

    declared_type = symbol_table.get(identifier[1])
    if declared_type is None:
        raise SyntaxError(f"Line {index+1}, Variable '{identifier[1]}' is not declared")

    next_token = next(tokens)
    if next_token[0] != 'RPAREN':
        raise SyntaxError(f"Line {index+1}, Expected ')' to end read statement")
        
    next_token = next(tokens)
    if next_token[0] != 'SEMICOLON':
        raise SyntaxError(f"Line {index+1}, Statements need to end with semicolons (;)")

def main(filepath):
    code = read_files(filepath)
    tokens = tokenize(code)
    parse(tokens)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py filename.txt")
    else: 
        filepath = sys.argv[1]
        main(filepath)
