from collections import defaultdict

def describe_person(name: str, age: int) -> str:
    if(age >= 18):
        return f"{name} is {age} years old and is an adult"
    else:
        return f"{name} is {age} years old and is a minor"
    
def safe_divide(a,b):
    if b == 0:
        return None
    return a/b 

def count_chars(s:str) -> dict:
    char = {}
    for ch in s:
        char[ch] = char.get(ch, 0) + 1
    
    return char

def is_anagram(s: str, t:str) -> bool:
    return count_chars(s) == count_chars(t)

def find_duplicates(nums: list) -> list:
    seen = set()
    duplicates = set()

    for n in nums:
        if n in seen:
            duplicates.add(n)
        else:
            seen.add(n)
    
    return list(duplicates)

def total_per_customer(orders) -> dict:
    total = defaultdict(int)
    for customer_id, amount in orders:
        total[customer_id] += amount
    return dict(total)
    
def main():
    nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    dup = [1, 2, 3, 2, 4, 5, 1]
    orders = [
    (1, 250),
    (2, 100),
    (1, 75),
    (3, 500),
    (2, 200),
    (1, 50),
    ]
    print(nums)
    print(dup)
    print(orders)
    print("-" * 80)
    print(nums[2])
    print(nums[-1])
    print(nums[:5])
    print(nums[::-1])
    print(nums[1::2])

    print(count_chars("hello"))

    print(is_anagram("anagram", "nagaram"))
    print(is_anagram("rat", "car"))
    print(find_duplicates(dup))
    print(total_per_customer(orders))

if __name__ == "__main__":
    main()

#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1
#counts[ch] = counts.get(ch, 0) + 1

