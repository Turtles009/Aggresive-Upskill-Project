class Book:
    id: str
    title: str
    author: str
    year: int
    tags: list[str] = []


nums = [1, 2, 3, 4]
books: dict[int, Book] = {}

[n for n in nums]

[n * 2 for n in nums]
[str(n) for n in nums]

[n for n in nums if n > 2]

[book.title for book in books.values()]
[book.title for book in books.values() if book.year > 2000]

{n: n * n for n in nums}
{book.id: book.title for book in books.values()}

{n % 3 for n in range(len(nums))}

words = ["apple", "banana", "cherry", "date", "elderberry"]

users = [
    {"name": "Ada", "age": 30, "active": True},
    {"name": "Bo", "age": 25, "active": False},
    {"name": "Cyrus", "age": 40, "active": True},
]


def main():
    print([len(word) for word in words])
    print([word for word in words if len(word) > 5])
    print([word.upper() for word in words if word[0] in ("a", "e")])
    print({word: len(word) for id, word in words})
    print({word[0] for word in words})
    print([user["name"] for user in users if user["active"]])
    print({user["name"]: user["age"] for user in users if user["age"] > 28})


if __name__ == "__main__":
    main()
