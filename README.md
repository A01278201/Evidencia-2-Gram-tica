# Descripción 
El idioma que elegí es el hausa, una de las lenguas chádicas más habladas en África Occidental (concentra hablantes en Nigeria, Níger, Camerún y países vecinos). El hausa posee un sistema de palabras relativamente simple—sin artículos definidos o indefinidos en la forma que conocemos en idiomas romances—y muestra concordancias de número y género menos rígidas que el español. Además, su sintaxis destaca por construir oraciones básicas con orden Sujeto-Verbo-Objeto (SVO), aunque permite coordinaciones flexibles mediante la conjunción “da” (“y”).

En este proyecto modelamos un subconjunto del hausa: oraciones declarativas simples que constan de

- Sintagmas nominales (NP), formados por un sustantivo (por ejemplo, mutum = “hombre”, zomo = “conejo”, *ni elemento coordinado…”) y opcionalmente una o varias coordinaciones con “da”.

- Sintagmas verbales (VP), con un verbo elemental (por ejemplo, suna = “corren”, hauji = “saltan”, ganowa = “encontró”) seguido de un NP que funciona como objeto.

- Coordinaciones (NP_Aux), usando “da” para unir múltiples sustantivos en un mismo sintagma nominal, siempre con asociación forzada hacia la derecha (p. ej. “mutum da zomo da kare”).

El objetivo es reconocer oraciones como:

```“mutum da zomo ganowa yara”
“zomo suna”
“mutum da kare da yara hauji”```

Este subconjunto captura la sintaxis esencial del hausa—sin cláusulas subordinadas, sin morfología verbal compleja—lo cual lo hace ideal para demostrar análisis LL(1) y construir una gramática libre de contexto que sirva de base a un parser predictivo.
