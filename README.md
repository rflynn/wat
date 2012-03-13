# WAT

Looking for code that makes you go "WAT?!"

## Results

```python
>>> xrange(0) > xrange(0)
False
>>> xrange(0) > xrange(0)
True
```

```python
import sys
class ClassA: pass

class ClassB: pass

# most built-in python types have an absolute ordinality
xrange(0) > unicode() > type > object > Exception > () > "" > sys > range(1) > [] == range(0) > (lambda x:x) > Exception() > {} > ClassB > ClassA > bytearray() > help > float("inf") > sys.float_info.max > sys.maxint > True == 1 == 1L == 1.0 > sys.float_info.epsilon > sys.float_info.min > False == 0 == 0L == 0.0 > -1 == -1L == -1.0 > -sys.maxint > -float("inf") > None
# NaN is != everything
float("nan")
-float("nan")
# complex numbers can be compared to most things except themselves
0j
1j
-1j
1.0j
0.0j
-1.0j
# set ordinality is type-dependent
set()
# classes with no built-in ordinal functions seem to use `id`, which relies on memory address
ClassA() ?= ClassB()
# None is < everything
None
```

## Reference/Inspiration
* https://www.destroyallsoftware.com/talks/wat

