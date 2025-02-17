import sys
import re

def parse_text_a(text_a):
    data_a = []
    for line in text_a.splitlines():
        match = re.match(r"\d+ :([0-9A-F]+)", line)
        if match:
            data_a.append(match.group(1))
    return data_a

def parse_text_b(text_b):
    data_b = "".join(re.findall(r"[0-9A-F]+", text_b))
    return data_b

def check_consistency(text_a, text_b):
    data_a = parse_text_a(text_a)
    data_b = parse_text_b(text_b)
    
    for i, line in enumerate(data_a, 1):
        if line not in data_b:
            print(f"Mismatch at line {i}: {line} not found in text B")
    
    print("Check complete.")


if len(sys.argv) < 3:
    print("need 2 files")
    exit()

f1 = open(sys.argv[1], "r")
f2 = open(sys.argv[2], "r")

text_a = f1.read()
text_b = f2.read()

check_consistency(text_a, text_b)

f1.close()
f2.close()
