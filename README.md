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

**1. Script hausa_grammar_ambiguous.py**

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






