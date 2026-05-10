import logging

def main():
    a = [1, 2, 3]
    b = a
    c = a.copy()
    b.append(4)
    c.append(5)
    # print(a)
    # print(b)
    # print(c)
    # print(append_to(1))
    # print(append_to(2))
    # print(append_to(3, []))
    # print(append_to(4))

    # words = ["python", "java", "rust", "go", "javascript"]
    # nums = [1, 2, 3, 4, 5]
    orders = [
    (1, 250),
    (2, 100),
    (1, 75),
    (3, 500),
    (2, 200),
    (1, 50),
    ]

    # print([n for n in range(20) if n%3 == 0])
    # print([word.upper() for word in words if len(word) <= 4])
    # print(["even" if num % 2 == 0 else "odd" for num in nums])

    # print([amount for _, amount in orders])
    # print([amount for _, amount in orders if amount > 100])
    # print([customer_id for customer_id, amount in orders if amount > 100])
    # print({customer_id for customer_id, _ in orders})
    # print(count_chars("hello", {}))
    print({i: amount for i, (_, amount) in enumerate(orders)})

    nums = [10, 20, 30, 40, 50]
    products = ["apple", "bread", "cheese", "donut"]
    prices = [120, 40, 350, 25]
    scores = [78, 92, 64, 88, 71, 95, 80]

    for i, num in enumerate(nums):
        print(f"{i}: {num}")

    print({product: price for product, price in zip(products, prices) if price > 50})
    print(top_scorers(scores, 80))
    print(parse_int_list(["1", "2", "abc", "4", "5.5", "7"]))
    print(parse_int_list_alt(["1", "2", "abc", "4", "5.5", "7"]))

def parse_int_list(strings):
    parsed = []
    for string in strings:
        try:
            parsed.append(int(string))
        except ValueError:
            logging.warning(f"Could not parse {string}")
    
    return parsed

def parse_int_list_alt(strings):
    return [int(string) for string in strings if string.isdigit()]


def top_scorers(scores, threshold) -> list[tuple[int, int]]:
    return [(rank, score) for rank, score in enumerate(scores, start=1) if score > threshold ]
    

def count_chars(s: str, char = {}) -> dict:
    return {ch: char.get(ch, 0) + 1 for ch in s}

def append_to(item, target=[]):
    target.append(item)
    return target


if __name__ == "__main__":
    main()