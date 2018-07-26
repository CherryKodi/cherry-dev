
dom.Node
========

Klasa `Node` opisuje węzeł HTML/XML, czyli jest to tag z zawartością.

Obiekty tej klasy są leniwe jak bardzo się da. Innymi słowy wykonują działanie jak już muszą zapamiętując wynik.  Dzięki temu są maksymalnie wydajne (węzły nie są parsowane jeśli i tak nikt nie korzysta z wyniku).

Node są konstruowane wewnątrz funkcji `dom_search()` i początkowo zwierają sam tag (np. `<a x="1">`) i jego pozycję w szukanym fragmencie HTML. Na żądanie Node parsuje atrybuty a także szuka zamykającego znacznika (np. `</a>`). Parsowanie występuje zawsze raz, niezależnie od liczy czy sposobu późniejszego dostępu.


API
---

Konstruktor jak i funkcje pomocnicze nie będą tutaj opisane.

W przykładach używany jest węzeł `<a x="1" y data-z="9">A<b>B</b></a>`.


### Atrybuty

#### Node.name

Nazwa tagu. 

Na przykład `a`.

Nie wymusza parsowania.
Korzysta ze sparsowanej zawartości jeśli jest dostępna albo uzyskuje samą nazwę tagu przy pierwszym użyciu.


#### Node.attrs

Słownik atrybutów. Jeśli atrybut nie miał wartości to w słowniku jest None.

Na przykład `{'x': '1', 'y': None, 'data-z': '9'}`.

Wymusza parsowanie atrybutów przy pierwszym dostępie.


#### Node.content

Zawartość węzła (wszytko między tagiem otwierającym a zamykającym).

Na przykład `A<b>B</b>`.

Wymusza szukanie tagu zamykającego przy pierwszym dostępie.


#### Node.text

Sam tekst zawarty w węźle.

Na przykład `AB`.

Wymusza szukanie tagu zamykającego przy pierwszym dostępie.
Usuwanie wewnętrznych tagów jest wykonywane za każdym razem.


#### Node.innerHTML

Zawartość węzła (wszytko między tagiem otwierającym a zamykającym). Tożsame z `Node.content`.

Na przykład `A<b>B</b>`.

Wymusza szukanie tagu zamykającego przy pierwszym dostępie.


#### Node.outerHTML

GCały węzła (tag otwierający, zawartośći i tag zamykający).

Na przykład `<a x="1" y data-z="9">A<b>B</b></a>`.

Wymusza szukanie tagu zamykającego przy pierwszym dostępie.


#### Node.attr

Widok atrybutów przez który jest widoczny słownik z atrybutami.

Dostęp do atrybutu węzła może być przez właściwość (np. `node.attr.x`) albo przez zawołanie (`node.attr('x')`).

Przykładowy wynik `1`.

Wymusza parsowanie atrybutów przy pierwszym dostępie.


#### Node.data

Widok atrybutów danych (`data-*`) przez który jest widoczny słownik z danymi.

Dostęp do danych węzła (atrybutów rozpoczynających się od `data-`) może być przez właściwość (np. `node.data.z`) albo przez zawołanie (`node.attr('z')`).

Wymusza parsowanie atrybutów przy pierwszym dostępie.


### Funkcje

W oficjalnym publicznym API nie ma funkcji, niemniej poprzez widoki można odnieść wrażenie ich obecności.


#### Node.attr()

```
Node.attr(ATTR)
```

Dostęp do atrybutu `ATTR`. Tak na prawdę wywołanie widoku `Node.attr`.

Na przykład: `attr('x')  # → '1'` albo `attr('data-z')  # → '9'`


Wymusza parsowanie atrybutów przy pierwszym dostępie.


#### Node.data()

```
Node.data(DATA)
```

Dostęp do danych `DATA` (czyli atrybutu `data-DATA`). Tak na prawdę wywołanie widoku `Node.data`.

Na przykład: `data('z')  # → '9'`.

Wymusza parsowanie atrybutów przy pierwszym dostępie.


### Wydajność

Koszt szukania zamykającego tagu jest około 10 razy bardziej kosztowny niż parsowanie atrybutów.

Tabela pokazuje co musi być raz parsowane przy dostęp danych.

Dostęp      | Tag zamykający | Atrybuty | Dodatkowo
----------- | -------------- | -------- | --------
`name`      | –              | –        | raz¹ pobranie nazwy
`attrs`     | –              | +        |
`content`   | +              | –        |
`text`      | +              | –        | usuwanie tagów za każdym razem 
`innerHTML` | +              | –        |
`outerHTML` | +              | –        |
`attr`      | –              | +        |
`data`      | –              | +        |

¹) jeśli wcześniej nie było atrybutów

