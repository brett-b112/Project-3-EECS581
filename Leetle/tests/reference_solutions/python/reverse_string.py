def reverse_string(s):
    """
    Write a function that reverses a string. The input string is given as an array of characters s.
    You must do this by modifying the input array in-place.
    """
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1

# Main function to handle input from stdin
if __name__ == "__main__":
    import sys
    import ast
    input_data = sys.stdin.read().strip()
    s = ast.literal_eval(input_data)
    reverse_string(s)
    print(str(s).replace(" ", ""))
