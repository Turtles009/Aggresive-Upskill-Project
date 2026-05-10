# Given an array of integers nums and an integer target, return the indices of the two numbers such that they add up to target.
# You may assume that each input has exactly one solution, and you may not use the same element twice.
# Examples:

# nums = [2, 7, 11, 15], target = 9 → return [0, 1] (because nums[0] + nums[1] = 2 + 7 = 9)
# nums = [3, 2, 4], target = 6 → return [1, 2]
# nums = [3, 3], target = 6 → return [0, 1]

def two_sum(nums: list[int], target: int) -> list[int]:
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

def two_sum_hash(nums: list[int], target:int) -> list[int]:
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        
        num_map[num] = i
    return []

def main():
    nums = [3, 5, 1, 4]

    print(two_sum(nums, 9))
    print(two_sum_hash(nums, 7))


if __name__ == "__main__":
    main()
