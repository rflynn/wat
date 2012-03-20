# WAT

Simple expressions in mainstream programming languages that make you go "WAT?!"

## Inspiration
* Gary Bernhardt "Wat" https://www.destroyallsoftware.com/talks/wat CodeMash 2012 

## Results

### Python
Python 2.7.2+

```python
# python appears to have a cycle in the ordinality of built-in types
>>> () > "" == unicode() > ()
True
# to be clear...
>>> () > ""
True
>>> "" == unicode()
True
>>> unicode() > ()
True
```

```python
# in python many objects' ordinality is based on memory address, not value
>>> xrange(0) > xrange(0)
False
>>> xrange(0) > xrange(0)
True
```

```python
# python range equality/ordinality appears to be an implementation artifact
>>> len(xrange(0)), len(range(0))
(0, 0)
>>> range(0) == range(0)
True
>>> xrange(0) == xrange(0)
False
>>> range(0) == xrange(0)
False
```

### Javascript
node.js v0.4.9

```javascript
> 0 >= null
true
> null >= 0
true
> null == 0
false
// WAT
```

```javascript
// null's relationship with numbers is confusing to me
> null >= 0 && null < 5e-324
true
// null must be [0, 5e-324) right?
> null > 0
false
// WAT
```

```javascript
> undefined == null
true
> null >= 0
true
> undefined >= 0
false
```

Let's see how ordinality works in general...

```javascript
> [0,-1,-2].sort()
[ -1, -2, 0 ]
// WAT
```

Even though javascript defines comparison between built-in types the spec
requires Array.sort() to force all array members toString()
http://ecma262-5.com/ELS5_HTML.htm#Section_15.4.4.11

### PHP
PHP 5.3.6

PHP is basically a big steaming pile of WTFs, so we'll try to limit ourselves.

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

### Perl

Perl is designed as a minimalist encoding of interpretable WTFs and we we will
skip it so we can stop looking for WTFs before the heat death of the Universe.

## Reference
1. "Built-in Types" http://docs.python.org/library/stdtypes.html The Python Standard Library, 2012
2. "Data Model" http://docs.python.org/reference/datamodel.html The Python Standard Library, 2012
3. "ECMA-262 5th Edition in HTML Format" http://ecma262-5.com/ELS5_HTML.htm#Section_8.5
4. "11.8.5 The Greater-than-or-equal Operator ( >= )" http://ecma262-5.com/ELS5_HTML.htm#Section_11.8.5
5. "python" http://python.org/
6. "node.js" http://nodejs.org/

