# WAT

Simple expressions in mainstream programming languages that make you go "WAT?!"

## Inspiration
* Gary Bernhardt "Wat" https://www.destroyallsoftware.com/talks/wat CodeMash 2012 

## Results

```python
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

## Reference
* http://docs.python.org/library/stdtypes.html
* http://docs.python.org/reference/datamodel.html
* Standard ECMA-262 ECMAScript Language Specification Edition 5.1 (June 2011) http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-262.pdf

