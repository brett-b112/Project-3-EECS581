def search(nums, target):
    """
    Given an array of integers nums which is sorted in ascending order,
    and an integer target, write a function to search target in nums.
    If target exists, then return its index. Otherwise, return -1.
    """
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Main function to handle input from stdin
if __name__ == "__main__":
    import sys
    import ast
    input_data = sys.stdin.read().strip()
    lines = input_data.split('\n')

    # Parse array (first line)
    nums_str = lines[0].strip()
    nums = ast.literal_eval(nums_str)

    # Parse target (second line)
    target = int(lines[1].strip())

    result = search(nums, target)
    print(result)
