# Descripción 
El idioma que elegí es el hausa, una de las lenguas chádicas más habladas en África Occidental (concentra hablantes en Nigeria, Níger, Camerún y países vecinos). El hausa posee un sistema de palabras relativamente simple—sin artículos definidos o indefinidos en la forma que conocemos en idiomas romances—y muestra concordancias de número y género menos rígidas que el español. Además, su sintaxis destaca por construir oraciones básicas con orden Sujeto-Verbo-Objeto (SVO), aunque permite coordinaciones flexibles mediante la conjunción “da” (“y”).

En este proyecto modelamos un subconjunto del hausa: oraciones declarativas simples que constan de

- Sintagmas nominales (NP), formados por un sustantivo (por ejemplo, mutum = “hombre”, zomo = “conejo”, *ni elemento coordinado…”) y opcionalmente una o varias coordinaciones con “da”.

- Sintagmas verbales (VP), con un verbo elemental (por ejemplo, suna = “corren”, hauji = “saltan”, ganowa = “encontró”) seguido de un NP que funciona como objeto.

- Coordinaciones (NP_Aux), usando “da” para unir múltiples sustantivos en un mismo sintagma nominal, siempre con asociación forzada hacia la derecha (p. ej. “mutum da zomo da kare”).

El objetivo es reconocer oraciones como:

```
“mutum da zomo ganowa yara”
“zomo suna”
“mutum da kare da yara hauji”
```

Este subconjunto captura la sintaxis esencial del hausa—sin cláusulas subordinadas, sin morfología verbal compleja—lo cual lo hace ideal para demostrar análisis LL(1) y construir una gramática libre de contexto que sirva de base a un parser predictivo.

# Modelos
**Gramática inicial (ambigua)**

```
S   → NP VP
NP  → NP 'da' NP
NP  → N
VP  → V NP

N   → 'mutum' | 'yara' | 'zomo' | 'kare'
V   → 'suna'  | 'hauji' | 'ganowa'
```

- S (oración) se descompone en un sintagma nominal (NP) seguido de un sintagma verbal (VP).

- NP → NP 'da' NP introduce coordinación de sustantivos (por ejemplo, “mutum da zomo” = “hombre y conejo”), pero es recursiva a la izquierda.

- NP → N permite que un NP sea simplemente un nombre aislado.

- VP → V NP exige un verbo seguido de un objeto (NP).

- Los símbolos terminales N y V abarcan los sustantivos y verbos básicos del subconjunto de hausa.


#   Problema: Ambigüedad

Esta gramática es ambigua porque, para oraciones coordinadas con más de dos nombres, no queda claro cómo agrupar la serie de “da”s. Por ejemplo:


*“mutum da zomo da kare ganowa yara”*

**Primera posible agrupación (asociación izquierda):**
```
NP → NP 'da' NP
    ├── NP → NP 'da' NP 
    │     ├── NP → N (“mutum”)
    │     └── ‘da’ N (“zomo”)
    └── ‘da’ N (“kare”)
VP → V NP (“ganowa” “yara”)
```
Interpreta “(mutum da zomo) da kare”.

**Segunda posible agrupación (asociación derecha):**
```
NP → NP 'da' NP
    ├── NP → N (“mutum”)
    └── ‘da’ NP
         ├── NP → N (“zomo”)
         └── ‘da’ N (“kare”)
VP → V NP (“ganowa” “yara”)
```
Interpreta “mutum da (zomo da kare)”.

Como se ve, hay dos árboles de análisis distintos para la misma cadena “mutum da zomo da kare ganowa yara”. Esto es inaceptable si queremos aplicar un análisis LL(1), porque el parser no sabrá cómo decidir de forma determinista —sin backtracking— cuál de las dos asociaciones (izquierda o derecha) usar.

Además, la producción recursiva a la izquierda impide directamente el análisis LL(1), ya que un parser predictivo no puede manejar recursividad izquierda sin reescritura.

```
NP → NP 'da' NP
```


# Eliminación de ambigüedad

**Gramática sin ambigüedad (G₁)**

Para resolver el problema de ambigüedad en la producción original, reescribimos la regla de coordinación forzando la asociación hacia la derecha. De este modo, toda secuencia de nombres unidos por “da” se agrupará siempre como:
“N da (N da (N da …))”
y no como “((N da N) da N)”.

La gramática resultante G₁, que ya no genera más de un árbol para la misma cadena coordinada, es:
```
S      → NP VP
NP     → N NP_Aux
NP_Aux → 'da' N NP_Aux
NP_Aux → ε

VP     → V NP

N      → 'mutum'  | 'yara' | 'zomo' | 'kare'
V      → 'suna'   | 'hauji'| 'ganowa'
```

- NP → N NP_Aux
    - Comienza siempre por un sustantivo (N).
    - `NP_Aux` se encarga de concatenar cero o más ocurrencias de “da N”.

- NP_Aux → 'da' N NP_Aux | ε
    - Si hay un “da N” adicional, lo consume y vuelve a llamar a sí mismo (asociación derecha).
    - Si no, produce ε (termina la coordinación).

Con estas reglas, por ejemplo, para la cadena: mutum da zomo da kare ganowa yara
la única derivación para el sintagma nominal del sujeto (“mutum da zomo da kare”) es: 

```
NP
├─ N (“mutum”)
└─ NP_Aux
   ├─ 'da'
   ├─ N (“zomo”)
   └─ NP_Aux
      ├─ 'da'
      ├─ N (“kare”)
      └─ NP_Aux → ε
```
ya que NP_Aux se expande siempre consumiendo “da N” hasta llegar a ε.


# Eliminación de recursividad izquierda

**Problema: recursividad izquierda residual**

Aunque en G₁ ya no existe la forma directa NP → NP 'da' NP, todavía podría haber problemas de parsing predictivo si alguna producción insistiera en “LHS → LHS …”. En nuestra gramática G₁:

- NP → N NP_Aux
  - No es recursiva a la izquierda, porque el lado derecho comienza con un terminal (N).

- NP_Aux → 'da' N NP_Aux | ε
  - Tampoco es recursiva a la izquierda, pues la alternativa que llama a sí misma ('da' N NP_Aux) comienza con el terminal 'da'.

En este sentido, G₁ ya está libre de recursividad izquierda en las producciones de NP y NP_Aux. Sin embargo, para garantizar un análisis LL(1) sin ambigüedad ni conflictos, sólo queda ajustar la producción de VP para evitar que un parser tenga que decidir entre “VP → V NP” y (en otro escenario) “VP → V” —por si quisiéramos permitir el verbo intransitivo. Para no complicar el ejemplo con verbos intransitivos, definiremos en un paso final la gramática G₂, que ya cumple todas las condiciones LL(1).

# Gramática final (G₂) — sin left recursion y totalmente LL(1)

Incorporaremos un no terminal intermedio VP_Tail de modo que:
```
VP → V VP_Tail
VP_Tail → NP | ε
```

De esta manera, al leer el verbo, el parser sabe que siempre debe mirar el siguiente token para decidir si continúa con un objeto (NP) o termina el sintagma verbal.

La gramática G₂ queda como:
```
S        → NP VP

NP       → N NP_Aux
NP_Aux   → 'da' N NP_Aux
NP_Aux   → ε

VP       → V VP_Tail
VP_Tail  → NP
VP_Tail  → ε

N        → 'mutum'  | 'yara' | 'zomo' | 'kare'
V        → 'suna'   | 'hauji'| 'ganowa'
```
- NP_Aux maneja cero o más coordinaciones “da N”.

- VP_Tail maneja el posible sintagma nominal que viene después del verbo, o bien termina el VP con ε.
  
Con esta forma:
1. No hay recursividad izquierda en ningún no terminal (todas las producciones que llaman a un hijo no terminal lo hacen por la derecha, precedido de un terminal).
2. No hay ambigüedad: la coordinación siempre se asocia a la derecha y cada regla LL(1) tiene conjuntos FIRST/FOLLOW disjuntos.
3. Es directamente analizables con un parser predictivo (LL(1)).


# Implementación

Para validar las gramáticas definidas y experimentar con árboles de análisis, utilizaremos Python junto con la biblioteca NLTK (Natural Language Toolkit). A continuación se muestran tres scripts que corresponden a cada una de las gramáticas vistas:

- G₀ (ambigua / left‐recursive) → hausa_grammar_ambiguous.py

- G₁ (sin ambigüedad, pero con recursividad derecha en NP_Aux) → hausa_grammar_unambiguous.py

- G₂ (sin ambigüedad ni recursividad izquierda, compatible LL(1)) → hausa_grammar_no_left_rec.py

Además, habrá un cuarto script llamado test_suite.py que se encargará de ejecutar pruebas automáticas sobre la gramática final G₂, para verificar en cada caso si la oración es aceptada (genera exactamente 1 árbol) o rechazada (genera 0 árboles).

# **1. Script hausa_grammar_ambiguous.py**

Este archivo carga la gramática G₀ (ambigua y recursiva a la izquierda) y muestra cuántos árboles produce para cada oración de prueba.
```
# hasua_grammar_ambiguous.py

import nltk
from nltk import CFG
from nltk.parse import ChartParser

# Definición de la gramática G₀ (ambigua, left‐recursive)
grammar_ambiguous = CFG.fromstring(r"""
  S    -> NP VP
  NP   -> NP 'da' NP
  NP   -> N
  VP   -> V NP
  N    -> 'mutum' | 'yara' | 'zomo' | 'kare'
  V    -> 'suna'  | 'hauji' | 'ganowa'
""")

# Creamos un parser basado en ChartParser
parser_ambiguous = ChartParser(grammar_ambiguous)

# Oraciones de prueba
test_sentences = [
    "mutum da zomo da kare ganowa yara".split(),  # Ejemplo ambiguo: debería producir 2 árboles
    "mutum da yara suna".split(),                # No ambiguo: debería producir 1 árbol
    "zomo ganowa yara".split()                   # Oración simple: 1 árbol
]

print("=== Prueba con gramática AMBIGUA (G₀) ===\n")

for tokens in test_sentences:
    sentence = " ".join(tokens)
    print(f"Oración: \"{sentence}\"")
    trees = list(parser_ambiguous.parse(tokens))
    print(f"  → # de árboles generados: {len(trees)}")
    # Mostrar cada árbol (si hay)
    for idx, tree in enumerate(trees, start=1):
        print(f"  Árbol {idx}:")
        tree.pretty_print()
    print()
```
Cómo funciona

 1- Definimos grammar_ambiguous usando la sintaxis CFG.fromstring de NLTK, copiando exactamente las producciones de G₀.

 2- Creamos un ChartParser con esa gramática.

 3- Para cada oración en test_sentences (ya tokenizada con .split()), generamos la lista de árboles con parser_ambiguous.parse(tokens).

 4- Imprimimos cuántos árboles se generaron y, si hay alguno, lo mostramos con pretty_print().


Resultado esperado:

- Para "mutum da zomo da kare ganowa yara" → # de árboles generados: 2 (dos agrupaciones posibles).

- Para "mutum da yara suna" → # de árboles generados: 1.

- Para "zomo ganowa yara" → # de árboles generados: 1.


# **2. Script hausa_grammar_unambiguous.py**

A continuación se define la gramática G₁ (sin ambigüedad en la coordinación, pero aún con recursividad en NP_Aux). Este script muestra que la misma oración ambigua en G₀, al parsearse con G₁, sólo produce 1 árbol.
```
# hasua_grammar_unambiguous.py

import nltk
from nltk import CFG
from nltk.parse import ChartParser

# Definición de la gramática G₁ (sin ambigüedad, NP_Aux → 'da' N NP_Aux | ε)
grammar_unambiguous = CFG.fromstring(r"""
  S       -> NP VP
  NP      -> N NP_Aux
  NP_Aux  -> 'da' N NP_Aux
  NP_Aux  ->
  VP      -> V NP
  N       -> 'mutum' | 'yara' | 'zomo' | 'kare'
  V       -> 'suna'  | 'hauji' | 'ganowa'
""")

parser_unambiguous = ChartParser(grammar_unambiguous)

# Mismas oraciones para comprobar ambigüedad
test_sentences = [
    "mutum da zomo da kare ganowa yara".split(),  # Ahora debería producir 1 único árbol
    "mutum da yara suna".split(),
    "zomo ganowa yara".split()
]

print("=== Prueba con gramática NO AMBIGUA (G₁) ===\n")

for tokens in test_sentences:
    sentence = " ".join(tokens)
    print(f"Oración: \"{sentence}\"")
    trees = list(parser_unambiguous.parse(tokens))
    print(f"  → # de árboles generados: {len(trees)}")
    for tree in trees:
        tree.pretty_print()
    print()
```

Diferencia clave
- La regla NP → NP 'da' NP (ambigua) se ha reemplazado por
```
NP      → N NP_Aux
NP_Aux  → 'da' N NP_Aux
NP_Aux  → ε
```
lo que fuerza la asociación hacia la derecha y elimina toda ambigüedad de agrupación.

Resultado esperado:
- "mutum da zomo da kare ganowa yara" → # de árboles generados: 1 (único árbol).

- Las demás oraciones también generan 1 árbol.


# **3. Script hausa_grammar_no_left_rec.py**

Para cerrar la implementación, presentamos G₂ (sin ambigüedad ni recursividad izquierda, completamente LL(1)). Aquí se introduce el no terminal intermedio VP_Tail para el sintagma verbal.
```
# hasua_grammar_no_left_rec.py

import nltk
from nltk import CFG
from nltk.parse import ChartParser

# Definición de la gramática G₂ (sin recursividad izquierda, LL(1) friendly)
grammar_no_left_rec = CFG.fromstring(r"""
  S         -> NP VP

  NP        -> N NP_Aux
  NP_Aux    -> 'da' N NP_Aux
  NP_Aux    ->

  VP        -> V VP_Tail
  VP_Tail   -> NP
  VP_Tail   ->

  N         -> 'mutum'  | 'yara' | 'zomo' | 'kare'
  V         -> 'suna'   | 'hauji'| 'ganowa'
""")

parser_no_left_rec = ChartParser(grammar_no_left_rec)

# Oraciones de prueba (igual que antes)
test_sentences = [
    "mutum da zomo da kare ganowa yara".split(),
    "mutum da yara suna".split(),
    "zomo ganowa yara".split()
]

print("=== Prueba con gramática SIN LEFT-RECURSION (G₂) ===\n")

for tokens in test_sentences:
    sentence = " ".join(tokens)
    print(f"Oración: \"{sentence}\"")
    trees = list(parser_no_left_rec.parse(tokens))
    print(f"  → # de árboles generados: {len(trees)}")
    for tree in trees:
        tree.pretty_print()
    print()
```
Notas

- Ahora VP → V VP_Tail y VP_Tail → NP | ε evitan cualquier ambigüedad de “¿VP → V NP” o “VP → V?”. Con VP_Tail el parser consulta el siguiente token para decidir entre expandir NP o terminar el VP con ε.

- Todas las producciones están libres de recursividad izquierda (los lados derechos empiezan con terminales).

Resultado esperado

- Cada oración de prueba genera exactamente 1 árbol. Ya no hay ambigüedad ni problema de recursividad izquierda.

# Complejidad

**Complejidad temporal**

En el peor de los casos para una oración de longitud n (es decir, n tokens), el `chart‐parser` debe considerar todos los sub‐spans posibles y todas las particiones de cada sub‐span. Por lo tanto, Parsing con `ChartParser` → **O(n³)** en tiempo en el peor de los escenarios, donde n es la cantidad de tokens de la oración.
