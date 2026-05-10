from collections import Counter

def contains_duplicate(nums: list[int]) -> bool:
    seen = set()
    # return len(nums) != len(set(nums))  ## One liner
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t): return False
    characters = {}
    for charS in s:
        characters[charS] = characters.get(charS, 0) + 1
    for charT in t:
        characters[charT] = characters.get(charT, 0) - 1

    return all(char == 0 for char in characters.values())

def is_anagram_counter(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)

def is_anagram_sorted(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)

def is_palindrome(s:str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while right > left and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True

def main():
    # print(contains_duplicate([1, 2, 3, 1]))
    # print(contains_duplicate([1, 2, 3, 4]))
    # print(contains_duplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2]))
    # print(contains_duplicate([]))
    # print(contains_duplicate([-1, 2, 1, 4, -1]))
    # print(is_anagram("anagram", "nagaram"))
    # print(is_anagram("rat", "car"))
    # print(is_anagram("a", "ab"))
    # print(is_anagram("a b#", "ab #"))
    # print(is_anagram("a B#", "ab #"))
    print(is_palindrome("A man, a plan, a canal: Panama"))
    print(is_palindrome("race a car"))
    print(is_palindrome(" "))
    print(is_palindrome(""))
    print(is_palindrome("-211121112-"))

if __name__ == "__main__":
    main()