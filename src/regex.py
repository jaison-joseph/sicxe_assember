import re

foo = ["C'eof'", "X'asd'", "C'_ER'", "C'ASS'", "C'RER'F"]

def checker(input):
    pattern = "^[CX]'(\w{0,3})'$"
    pattern_2 = '^[CX]"(\w{0,3})"$'
    result = re.search(pattern, input)
    if result is None:
        result = re.search(pattern_2, input)
        if result is None:
            print(input, " does not match")
            return
    print("input: ", input, "| captured:", result.group(1))

for test in foo:
    checker(test)
