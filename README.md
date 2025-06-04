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

**Problema: Ambigüedad**.

Esta gramática es ambigua porque, para oraciones coordinadas con más de dos nombres, no queda claro cómo agrupar la serie de “da”s. Por ejemplo:

*“mutum da zomo da kare ganowa yara”*

Primera posible agrupación (asociación izquierda):
```
NP → NP 'da' NP
    ├── NP → NP 'da' NP 
    │     ├── NP → N (“mutum”)
    │     └── ‘da’ N (“zomo”)
    └── ‘da’ N (“kare”)
VP → V NP (“ganowa” “yara”)
```
Interpreta “(mutum da zomo) da kare”.

Segunda posible agrupación (asociación derecha):
```
NP → NP 'da' NP
    ├── NP → N (“mutum”)
    └── ‘da’ NP
         ├── NP → N (“zomo”)
         └── ‘da’ N (“kare”)
VP → V NP (“ganowa” “yara”)
```
Interpreta “mutum da (zomo da kare)”.
