# Edge cases

# Example with multiple levels missing on original

## Original

```python

N = 0
def wrapper(fn):
    def counter(*args, **kwargs):
        global N
        N+=1
        return fn(*args, **kwargs)
    return counter
```

## Marks

verdict address a0 add "This is the module doc string"

verdict address f0 add "The No-License"

verdict address b1 add
"The counter total for all function calls
if this wasn't python and if it was a big
system this might overflow"

verdict address c1 add "The counted function calls"
verdict address a1 add "The docstring for the wrapper function"
verdict address b2 add "I built a closure function it gets a function"
verdict address c2 add "I forgot that it is a callable"

verdict address a2 add "The counter docstring"
verdict address b3 add "There is documentation above the counter"
verdict address c3 add "The comment after the counter"

verdict address b4 add "Have to declare global to get N"
verdict address c4 add "N is the function counts"

That should transform into

```python
# The No-License
"""This is the module docstring"""

# The counter total for all function calls
# if this wasn't python and this was a big
# system this might overflow
N=1 # The counted function calls
# I built a closure function it gets a function
def wrapper(fn): # I forgot that it is callable
    """The docstring for the function wrapper"""
    # There is documentation above the counter
    def counter(*args, **kwargs): # The comment after the counter
        """The counter docstring"""
        # Have to declare global to get N
        global N # N is the function counts
        N+=1
        return fn(*args, **kwargs)
    return counter

```
