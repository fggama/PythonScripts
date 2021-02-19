# Tipo de iteradores
iter('foobar')                             # String
iter(['foo', 'bar', 'baz'])                # List
iter(('foo', 'bar', 'baz'))                # Tuple
iter({'foo', 'bar', 'baz'})                # Set
iter({'foo': 1, 'bar': 2, 'baz': 3})       # Dict

# Iterando
a = ['foo', 'bar', 'baz']
itr = iter(a)
itr
next(itr)
next(itr)
next(itr)

# Iterator to list
a = ['foo', 'bar', 'baz']
itr = iter(a)
list(itr)

# Dictionary
d = {'foo': 1, 'bar': 2, 'baz': 3}
for k, v in d.items():
    print('k =', k, ', v =', v)
    
# Using list comprehension 'new_list = [expression for member in iterable (if conditional)]'
squares = [i * i for i in range(10)]
squares

sentence = 'the rocket came back from mars'
vowels = [i for i in sentence if i in 'aeiou']

# 'new_list = [expression (if conditional) for member in iterable]'
original_prices = [1.25, -9.45, 10.22, 3.78, -5.92, 1.16]
prices = [i if i > 0 else 0 for i in original_prices]
prices
# >>> [1.25, 0, 10.22, 3.78, 0, 1.16]

# set comprehension (no duplicates)
quote = "life, uh, finds a way"
unique_vowels = {i for i in quote if i in 'aeiou'}

# Dictionary comprehensions
squares = {i: i * i for i in range(10)}
squares

# map
txns = [1.09, 23.56, 57.84, 4.56, 6.78]
TAX_RATE = .08
def get_price_with_tax(txn):
    return txn * (1 + TAX_RATE)
final_prices = map(get_price_with_tax, txns)  # return map object
list(final_prices)

final_prices = [get_price_with_tax(i) for i in txns] # return list
final_prices

# walrus operator 
import random
def get_weather_data():
    return random.randrange(90, 110)
hot_temps = [temp for _ in range(20) if (temp := get_weather_data()) >= 100]
# >>> [107, 102, 109, 104, 107, 109, 108, 101, 104]

# Nested Comprehensions
cities = ['Austin', 'Tacoma', 'Topeka', 'Sacramento', 'Charlotte']
temps = {city: [0 for _ in range(7)] for city in cities}

# {
    # 'Austin': [0, 0, 0, 0, 0, 0, 0],
    # 'Tacoma': [0, 0, 0, 0, 0, 0, 0],
    # 'Topeka': [0, 0, 0, 0, 0, 0, 0],
    # 'Sacramento': [0, 0, 0, 0, 0, 0, 0],
    # 'Charlotte': [0, 0, 0, 0, 0, 0, 0]
# }

matrix = [[i for i in range(5)] for _ in range(6)]

# [
    # [0, 1, 2, 3, 4],
    # [0, 1, 2, 3, 4],
    # [0, 1, 2, 3, 4],
    # [0, 1, 2, 3, 4],
    # [0, 1, 2, 3, 4],
    # [0, 1, 2, 3, 4]
# ]

# generator
sum(i * i for i in range(1000000000))

