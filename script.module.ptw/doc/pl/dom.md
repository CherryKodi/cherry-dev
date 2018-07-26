
Nowa obsługa DOM
================

Klasy i typy
============

[`Node`](dom-node.md) – opisuje węzeł HTML/XML, czyli jest to tag z zawartością.


dom.search()
============

Funkcja parsuje HTML/XML, znajduje tagi z atrybutami
i zwraca te pasujące wraz z żadaną zawartością 
czy to tekst, atrybuty, czy węzeł Node().


dom.select()
============

Przeszukiwanie (wybieranie) danych z HTML na wzór uproszczonych 
selektorów, podobnych do tych z CSS czy jQuery.


### Przykłady

Większość przykładów używa poniższego źródła HTML.

```python
# HTML w stylu  A ( B C ) A ( B )
html = '<a x="11" y="12">A1<b>B1</b><c>C1</c></a> <a x="21" y="22">A2<b>B2</b></a>'
```


Selektory
---------

Pierwszy z brzegu kurs, gdzie wyjaśnione są selektory CSS – http://www.kurshtml.edu.pl/css/selektory.html

Tutaj jest tylko namiasta tych mozliowści ale i tak pozwala to w miarę sprawnie wyłuskiwać dane.


### Obsługiwanie selektory

Selektor     | Opis
-------------|------------
\*           | Każdy element.
\#id         | Każdy element z podanym `id`.
.class       | Każdy element z podaną klasą `class`.
tag          | Wskazany `<tag>`.
E1, E2       | Grupa, znajdywana są wszystkie E1 oraz E2.
E1 E2        | Potomek, każdy E2 które są potomkiem E1.
[attr]       | Każdy element, który posiada atrybut `attr`.
[attr=val]   | Każdy element, z atrybutem `attr` równym `val`.
[attr^=val]  | Każdy element, z atrybutem `attr` rozpoczęty od `val`.
[attr$=val]  | Każdy element, z atrybutem `attr` zakończony na `val`.
[attr~=val]  | Każdy element, z atrybutem `attr` ze słowem¹ `val`.
[attr\|=val] | Każdy element, z atrybutem `attr` ze słowem¹ rozpoczętym od `val`.
[attr*=val]  | Każdy element, z atrybutem `attr` zawierający tekst `val`.

¹) Słowo to ciąg znaków (bez spacji).


#### Przykłady

##### Pojedynczy węzeł

```python
for b in dom_select(html, 'a b'):
    print('Result:', b.text)
# Result: B1
# Result: B2
```

Łapie wszystkie tagi `b`, które są zawarte w tagu `a`.



### Dodatkowe selektory

Poniższe selektory wychodzą poza standard CSS i jQuery.

Selektor     | Opis
-------------|------------
{ E1, E2 }   | Alternatywa, zarówno E1 jaki i E2.
E1?          | Opcja, E1 albo None, gdy nie istnieje.

Selektor alternatywy zwraca podlistę i dzięki temu pozwala złapać wiele elementów,
które są zawarte w nadrzędnym za pomocą jednego zapytania. 
Jeśli któryś z elementów w selektorze alternatywnym jest opcjonalny, to zwrócone
zostanie None w tej samej pozycji, w której brakuje elementu.

Element opcjonalny jest użyteczny w selektorze alternatywnym. 
Zwracane jest None na odpowiedniej pozycji dzięki czemu łatwiej takie zapytanie
przetwarzać w pętli for.


#### Przykłady

##### Alternatywa

```python
for b, c in dom_select(html, 'a {b, c}'):
    print('Result:', b.text, c.text)
# Result: B1 C1
```

Łapie tagi `b` i `c`, które są zawarte w `a`.
Złapało tylko jedną linię, bo drugi tag `a` nie posiada `c`.


##### Alternatywa z opcją

```python
for b, c in dom_select(html, 'a {b, c?}'):
    print('Result:', b.text, c and c.text)
# Result: B1 C1
# Result: B2 None
```

Jak wyżej, łapie tagi `b` i `c`, które są zawarte w `a`, z tym, że `c` jest opcjonalny.
Pierwsza linia trafiła w `b` i `c` z pierwszego `a` (jak wyżej).
Druga linia też trafiła (w drugie `a`) tylko zwróciła `b` i None (bo nie ma tam `c`).


### Pseudo-klasy węzła

Selektor              | Opis
----------------------|------------
:contains(S)          | Łapie jeśli tekst `S` zawiera się w *tekście* węzła.
:content-contains(S)  | Łapie jeśli tekst `S` zawiera się w zawartości węzła (innerHTML).
:regex(R)             | Łapie jeśli wyrażenie regularne `R` trafi w outerHTML.
:has(T)               | Łapie jeśli węzeł posiada w zawartości tag `T`.
:empty                | Łapie tylko puste tagi (bez tekstu czy tagów w zawartości).

Powyższe pseudo-klasy są wyraźnie wolniejsze ponieważ do sprawdzenia muszą znaleźć tag zamykający.

`:has` używa uproszczonego wyszukiwania i może znaleźć tag `T` nawet w wartości atrybutu.
To zostanie naprawione. Kiedyś...


#### Przykłady

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


### Pseudo-elementy wyniku

Selektor     | Opis
-------------|------------
::node       | Zwraca węzeł Node (domyślne dla ostatniego tagu z selektorze).
::text       | Zwraca test z węzła (bez tagów), np.  `AB`
::content    | Zwraca zawartość węzła, np. `A<b>B</b>`
::innerHTML  | Jak wyżej.
::outerHTML  | Zwraca cały węzeł (tag i zawartość), np. `<a>A<b>B</b></a>`
::attr(A)    | Zwraca atrybut `A`. Można użyć listy atrybutów rozdzielonych przecinkami.
(A)          | Skrót dla `::attr(A)`.
::none       | Nic nie zwraca. Węzeł musi istnieć.
::DomMatch   | Zwraca węzły DomMatch, dla kompatybilności.

Jeśli żaden z pseudo-element wyniku nie jest użyty, to zwracany jest Node.
Jeśli jest użyty choć jeden zwracana jest lista z żądanymi rzeczami.

1. `A` → `Node(A)`

2. `A::node` → `[Node(A)]`

3. `A(x,y)::content` → `[x, y, 'A']`

4. `A(x)` → `[x]`


To dlatego gdy pobierany jest jeden atrybut potrzeba dodatkowego wyłuskiwania. 
Poniżej porównanie przypadków 1 i 4 i wypisania atrybutu *x*.

```python
# 1.
for a in dom.select(html, 'a'):
    print(a.x)

# 4.
for (x,) in dom.select(html, 'a(x)'):
    print(x)
```


#### Przykłady

##### Węzeł rodzica z dwoma potomkami (alternatywa) z czego jeden opcjonalny

```python
for (a,), b, c in dom_select(html, 'a::node {b, c?}'):
    print('Result:', a.text b.text, c and c.text)
# Result: A1B1C1 B1 C1
# Result: A2B2 B2 None
```

Tag `a` powinien posiadać `b` i `c` i zawsze oba są zwracane. Przy czym `c` jest opcjonalne, 
czyli jeśli go nie ma, w jego miejsce zwracane jest None. 
Dodatkowe nawiasy wokół *a* są z powodu listy, co zostało wyjaśnione wyżej.

Pierwsza linia trafiła w pierwsze `a` oraz potomków `b` i `c`.
Druga linia też trafiła (w drugie `a`) tylko zwróciła `b` i None (bo nie ma tam `c`).


