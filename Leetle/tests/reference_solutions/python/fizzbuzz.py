def fizz_buzz(n):
    """
    Given an integer n, return a string array answer (1-indexed)
    where answer[i] == "FizzBuzz" if i is divisible by 3 and 5,
    "Fizz" if i is divisible by 3, "Buzz" if i is divisible by 5,
    answer[i] == i (as a string) otherwise.
    """
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

# Main function to handle input from stdin
if __name__ == "__main__":
    import sys
    input_data = sys.stdin.read().strip()
    n = int(input_data)
    result = fizz_buzz(n)
    print(str(result).replace(" ", ""))
