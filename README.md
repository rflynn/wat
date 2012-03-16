# WAT

Simple expressions in mainstream programming languages that make you go "WAT?!"

## Inspiration
* Gary Bernhardt "Wat" https://www.destroyallsoftware.com/talks/wat CodeMash 2012 

## Results

```python
# python 2.7
>>> unicode() == ""
True
>>> unicode() > () > ""
True
```

```python
>>> Exception > () > "" == unicode() > type > object > Exception
True
```

```python
# many objects' ordinality is based on memory address, not value
>>> xrange(0) > xrange(0)
False
>>> xrange(0) > xrange(0)
True
```

```php
# php treats numeric strings as numeric values with unary operators,
# except for ~ which for some reason executes bitwise negation on each
# string character (wat?!)
print_r(array( +1, +"1", -1, -"1", ~1, ~"1" ));
Array
(
    [0] => 1
    [1] => 1
    [2] => -1
    [3] => -1
    [4] => -2
    [5] => �
)
```

## Reference
* "Built-in Types" http://docs.python.org/library/stdtypes.html The Python Standard Library, 2012
* "Data Model" http://docs.python.org/reference/datamodel.html The Python Standard Library, 2012
* "Standard ECMA-262" http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-262.pdf ECMAScript Language Specification Edition 5.1 (June 2011)
* "ECMA-262 5th Edition in HTML Format" http://ecma262-5.com/ELS5_HTML.htm#Section_8.5

