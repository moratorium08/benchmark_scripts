import re
import sys

def conv(expression: str) -> str:
    converted_expression = re.sub(r'\(declare-fun\s+\|(([^|]+))\|', r'(declare-fun \1', expression)
    return converted_expression

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        content = f.read()

    converted_content = conv(content)

    with open(output_file, 'w') as f:
        f.write(converted_content)

s_expression = """
(set-logic HORN)

(declare-datatypes ((Nat_0 0)) (((Z_0 ) (S_0  (projS_0 Nat_0)))))

(declare-fun   |diseq_%Nat_0| ( Nat_0 Nat_0 ) Bool)
(declare-fun\t


|x_0| ( Nat_0 Nat_0 Nat_0 ) Bool)

(assert
  (forall ( (A Nat_0) (B Nat_0) (v_2 Nat_0) )
    (=>
      (and
        (and (= A (S_0 B)) (= v_2 Z_0))
      )
      (diseqNat_0 v_2 A)
    )
  )
)
(assert
  (forall ( (A Nat_0) (B Nat_0) (v_2 Nat_0) )
    (=>
      (and
        (and (= A (S_0 B)) (= v_2 Z_0))
      )
      (diseqNat_0 A v_2)
    )
  )
)
"""

# converted_expression = conv(s_expression)
# print(converted_expression)
