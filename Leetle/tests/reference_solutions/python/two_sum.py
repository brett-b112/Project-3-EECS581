def two_sum(nums, target):
    """
    Given an array of integers nums and an integer target,
    return indices of the two numbers such that they add up to target.
    """
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []

# Main function to handle input from stdin
if __name__ == "__main__":
    import sys
    input_data = sys.stdin.read().strip()
    lines = input_data.split('\n')

    # Parse array (first line)
    nums_str = lines[0].strip()
    import ast
    nums = ast.literal_eval(nums_str)

    # Parse target (second line)
    target = int(lines[1].strip())

    result = two_sum(nums, target)
    print(str(result).replace(' ', ''))
