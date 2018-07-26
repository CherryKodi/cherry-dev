
New DOM support
===============

dom.search()
============

Function parses HTML/XML, finds tags with attribites
and returns matching tags content or attribute or Node().


dom.select()
============

Find data in HTML by CSS / jQuery simplified selector.


### Examples

Most examples use this pattern.

```python
# HTML like  A ( B C ) A ( B )
html = '<a x="11" y="12">A1<b>B1</b><c>C1</c></a> <a x="21" y="22">A2<b>B2</b></a>'
```


Selectors
---------

### Supported selectors

Selector     | Description
-------------|------------
\*           | All elements
\#id         | The element with id
.class       | All elements with class
tag          | All <tag> elements
E1, E2       | Or, all E1 and all E2 matched elements
E1 E2        | Parent descendant, all E2 elements that are descendants of a E1 element
[attr]       | All elements with a attribute `attr`
[attr=val]   | All elements with a attribute value equal `val`
[attr^=val]  | All elements with a attribute value starting with `val`
[attr$=val]  | All elements with a attribute value ending with `val`
[attr~=val]  | All elements with a attribute value containing word `val`
[attr\|=val]  | All elements with a attribute value containing word starting with`val`
[attr*=val]  | All elements with a attribute value containing `val`

#### Examples

##### Single node

```python
for b in dom_select(html, 'a b'):
    print('Result:', b.text)
# Result: B1
# Result: B2
```

Match all tag B inside tag A.



### Extra selectors

Selector     | Description
-------------|------------
{ E1, E2 }   | Alternative, E1 and E2 elements as sublist.
E1?          | Optional element, None is returned if element is missing.

Alternative selector returns a sublist and can select many elements inside given parent.
If some optional element doesn't exists None is returned.

Optional element is usefull in alternatives. You get None insteed of missing element
but rest of alternative elements are returned.


#### Examples

##### Attributes

```python
for b in dom_select(html, 'a b'):
    print('Result:', b.text)
# Result: B1
# Result: B2
```

Match all tag B inside tag A.


##### Alternatives

```python
for b, c in dom_select(html, 'a {b, c}'):
    print('Result:', b.text, c.text)
# Result: B1 C1
```

Tag A has to contains B and C, both are returned. Second A tag are omitedd because C is missing.


##### Alternatives and optional

```python
for b, c in dom_select(html, 'a {b, c?}'):
    print('Result:', b.text, c and c.text)
# Result: B1 C1
# Result: B2 None
```

Tag A has to contains B and C, both are returned but C is optional.
First line match A with B and C (like in example above).
Second line matched A with B and returned None in place of missing C.


### Node pseudo-elements

Selector              | Description
----------------------|------------
:contains(S)          | Match if text `S` in *text* content
:content-contains(S)  | Match if text `S` in innerHTML content
:regex(R)             | Match regex pattern `R` in outerHTML
:has(T)               | Match if node has tag `T`
:empty                | March if node has no any text or tag

Those pseudo-elements are slower because thay have to find closing tag first.

`:has` uses simple searching and can find tag `T` even in attribute value. It will be fixed.


#### Examples

##### :contains(S)

```python
for a in dom_select(html, 'a:contains("2B2")'):
    print('Result:', a.text)
# Result: A2B2
```

##### :empty(S)

```python
for a in dom_select('<a></a><b/><c>C</c>', ':empty'):
    print('Result:', a.name)
# Result: a
# Result: b
```


### Result pseudo-elements

Selector     | Description
-------------|------------
::node       | Returns Node(), it's default on last node
::text       | Returns note text (without tags), e.g. `AB`
::content    | Returns node content, e.g. `A<b>B</b>`
::innerHTML  | The same.
::outerHTML  | Returns whole node (tag and content), e.g. `<a>A<b>B</b></a>`
::attr(A)    | Returns attribute `A`, comma separated list can be used
(A)          | Shortcut for `::attr(A)`
::none       | Do not return anything, but node has to exist
::DomMatch   | Returns DomMatch nodes, for backward compability


#### Examples

##### Parent node with alternatives and optional

```python
for (a,), b, c in dom_select(html, 'a::node {b, c?}'):
    print('Result:', a.text b.text, c and c.text)
# Result: A1B1C1 B1 C1
# Result: A2B2 B2 None
```

Tag A has to contains B and C, both are returned but C is optional. We also reqests return A node.
Extra brackets are used, because all pseudo elements are returned as sublist (even if it's only one).

First line match A and its content B and C.
Second line matched next A in the same way but we've got None instead missing C.


