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
NP_Aux   → 'da' N NP_Aux   |  ε

VP       → V VP_Tail
VP_Tail  → NP   |  ε

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

En esta caso trabajamos con una version del código en Python: Parser LL(1) con la gramática G₂ (sin ambigüedad ni left‐recursion), que garantiza análisis en tiempo O(n).


```
import nltk
from nltk import CFG
from nltk.parse import ChartParser

# —————————————————————————————————————————————————————————————
# Gramática G₂ (sin ambigüedad ni recursividad izquierda) en NLTK
# —————————————————————————————————————————————————————————————
hausa_grammar_unambiguous = CFG.fromstring(r"""
S         -> NP VP

NP        -> N NP_Aux
NP_Aux    -> 'da' N NP_Aux
NP_Aux    ->

VP        -> V VP_Tail
VP_Tail   -> NP
VP_Tail   ->

N         -> 'mutum' | 'yara' | 'zomo' | 'kare'
V         -> 'suna'  | 'hauji' | 'ganowa'
""")

parser = ChartParser(hausa_grammar_unambiguous)

test_sentences = [
    "mutum da zomo da kare ganowa yara",
    "mutum da yara suna",
    "zomo ganowa yara",
]

for sentence in test_sentences:
    tokens = sentence.split()
    trees = list(parser.parse(tokens))
    print(f"'{sentence}' genera {len(trees)} árbol(es):")
    for tree in trees:
        tree.pretty_print()
    print()
```

**¿Por qué NO hay ambigüedad ni left‐recursion?**

Sin ambigüedad:

- En G₀, la regla `NP → NP 'da' NP` permitía agrupar “mutum da zomo da kare” de dos maneras distintas.

- Ahora, con `NP → N NP_Aux` y `NP_Aux → 'da' N NP_Aux | ε`, toda secuencia `"N da N da N …"` se asocia a la derecha automáticamente, así no hay dos árboles distintos para la misma cadena.

Sin recursividad izquierda:

- Ninguna producción arranca con su propio no terminal. Por ejemplo, antes `NP → NP 'da' NP` era left‐recursive, pero ahora `NP → N NP_Aux` arranca con un terminal (N).

- Esto permite un parsing más sencillo (ni siquiera se necesitan transformaciones; ChartParser no se atasca en bucles infinitos).



# **Complejidad**

Un parser LL(1) procesa una cadena de longitud n en una sola pasada, haciendo por cada token una única consulta a la tabla de parsing y empujando/desapilando un número constante de símbolos. Por ello su coste temporal es O(n), y la pila de símbolos puede crecer a lo sumo O(n), resultando en una complejidad espacial también O(n).


# Referencias

Aho, A. V., Sethi, R., & Ullman, J. D. (1986). Compilers: Principles, Techniques, and Tools (1.ª ed.). Addison-Wesley.

Hopcroft, J. E., & Ullman, J. D. (1979). Introduction to Automata Theory, Languages, and Computation. Addison-Wesley.

Sipser, M. (2006). Introduction to the Theory of Computation (2.ª ed.). Thomson Course Technology.

Jurafsky, D., & Martin, J. H. (2020). Speech and Language Processing (3.ª ed.). Prentice Hall.

Pereira, F. C. N., & Shieber, S. M. (1987). Prolog and Natural-Language Analysis. CSLI Publications.

Bird, S., Klein, E., & Loper, E. (2009). Natural Language Processing with Python. O’Reilly Media.
