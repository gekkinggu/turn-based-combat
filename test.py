names = ["John", "Alice", "Bob", "Eve"]

names.pop()
print(names)  # Output: ['John', 'Alice', 'Bob']
print(names.pop())
names.append("Charlie")
names.pop()
print(names)  # Output: ['John', 'Alice', 'Charlie']