def is_palindrome(x):
    """
    Given an integer x, return true if x is palindrome integer.
    """
    if x < 0:
        return False
    return str(x) == str(x)[::-1]

# Main function to handle input from stdin
if __name__ == "__main__":
    import sys
    input_data = sys.stdin.read().strip()
    x = int(input_data)
    result = is_palindrome(x)
    print("true" if result else "false")
