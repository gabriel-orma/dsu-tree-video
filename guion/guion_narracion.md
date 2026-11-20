# Guion de narración: DSU Tree, el DSU con memoria

Video de referencia: `media/dsu_tree_1080p60.mp4` (duración 4:41.2). Los tiempos se midieron sobre ese render; si el video se vuelve a renderizar, hay que medirlos de nuevo.

- **Voz 1** narra la primera parte: de 0:00.0 a 2:05.5 (el problema, la idea y cómo se construye el árbol).
- **Voz 2** narra la segunda parte: de 2:05.5 a 4:31.2 (uniones de grupos, compresión, consultas, el ejemplo de las islas y la complejidad).
- Los créditos (4:31.2) los dicen las dos voces juntas.

## Cómo usar este guion

- Cada bloque empieza en el **timestamp** indicado y debería terminar antes del siguiente. Las frases se ajustaron para no pasar de unas 2,8 palabras por segundo, un ritmo cómodo y claro.
- Los **puntos suspensivos (…)** marcan una pausa breve. Las palabras en **negrita** van con énfasis.
- La voz **no lee** el texto de pantalla: lo acompaña. Si prefieren que solo hable la voz, el video se puede renderizar sin textos con `DSU_CAPTIONS=0`; los tiempos cambian, así que habría que medirlos de nuevo.
- Para grabar: pongan el video en silencio, graben cada bloque por separado (o toda su parte de corrido mirando el video) y en DaVinci Resolve coloquen cada clip de audio en su timestamp.

## Cómo hablar

- **Voz 1**: tono de quien cuenta una historia. Cálido, curioso, con pausas antes de cada revelación («solo un vector», «momento tres»).
- **Voz 2**: tono de quien narra una jugada. Más energía en la compresión y en la subida de la consulta; vuelve a un tono analítico en la complejidad.
- Sonrían al hablar: se nota en la voz. Bajen el ritmo en los momentos clave (las consultas) y súbanlo un poco en las uniones rápidas.
- Pronunciación: «DSU» se dice «de-ese-u»; «whenConnected» puede decirse «cuándo se conectaron»; «t» se dice «te».

## Voz 1 — Primera parte

### 0:00.0 – 0:02.3  ·  Aparecen 12 bolas sueltas
*Cómo decirlo:* Curioso, voz algo baja, como quien empieza a contar una historia.

> Imagina un montón de cosas sueltas…

### 0:02.3 – 0:10.5  ·  Las bolas se agrupan en islas
*Cómo decirlo:* Asombro que va creciendo; acelera un poco al final.

> Personas, computadoras, ciudades… que poco a poco se van conectando, hasta formar grupos. **Como islas.**

### 0:10.5 – 0:13.5  ·  Texto: «eso hace un DSU»
*Cómo decirlo:* Seguro, con complicidad.

> Eso, justamente, es lo que hace un **DSU**.

### 0:13.5 – 0:17.5  ·  Las islas se achican y aparece el vector
*Cómo decirlo:* Giro de sorpresa: pausa antes de «solo un vector».

> Pero para la computadora… todo esto es **solo un vector**.

### 0:17.5 – 0:23.1  ·  Aparece padre[x]; las raíces se marcan en dorado
*Cómo decirlo:* Explicativo; énfasis en «raíz».

> Cada uno apunta a su grupo; quien se apunta a sí mismo, es la **raíz**.

### 0:23.1 – 0:27.8  ·  Se marcan las casillas de una isla
*Cómo decirlo:* Conclusión simple, sonriendo.

> Tres raíces, tres islas: cada isla llega a una misma raíz.

### 0:27.8 – 0:32.9  ·  Título: DSU Tree
*Cómo decirlo:* Presentación con orgullo, pausa entre las dos frases.

> Esto es… **DSU Tree**. El DSU con memoria.

### 0:32.9 – 0:38.0  ·  «Solo guarda el presente» y la pregunta en rojo
*Cómo decirlo:* Plantea un problema; la pregunta con intriga real.

> El vector solo guarda el **presente**. ¿Cuándo se conectaron el 1 y el 11?

### 0:38.0 – 0:40.7  ·  Texto: «¿Cómo?»
*Cómo decirlo:* Reto al espectador; pausa larga después de «¿Cómo?».

> Hay que guardar la **historia**. ¿Cómo?

### 0:40.7 – 0:44.2  ·  Aparecen 4 hojas y unite(1, 2)
*Cómo decirlo:* Entusiasmo de «tengo una idea»; suspenso al final.

> Cada elemento es una hoja. Cuando dos se unen…

### 0:44.2 – 0:49.9  ·  Nace el nodo amarillo con t = 1
*Cómo decirlo:* Revelación; recalca «momento».

> …creamos un nodo encima de ambos que anota el **momento**: t igual a uno.

### 0:49.9 – 0:54.2  ·  unite(3, 4): nace t = 2
*Cómo decirlo:* Ligero, con ritmo.

> Otra unión, otro nodo: t igual a dos.

### 0:54.2 – 0:57.8  ·  unite(2, 3): nace t = 3
*Cómo decirlo:* Un poco más de energía: se unen los grupos grandes.

> Al unir los dos grupos, nace t igual a tres.

### 0:57.8 – 1:02.1  ·  Consulta: ¿1 y 4? (el camino se marca en rojo)
*Cómo decirlo:* Curiosidad; acompaña la subida del camino.

> ¿Cuándo se conectaron el 1 y el 4? Subimos por el árbol…

### 1:02.1 – 1:07.8  ·  El nodo t = 3 se pone verde
*Cómo decirlo:* Momento «¡ajá!»: énfasis en «momento tres».

> …hasta su ancestro común. Como t crece al subir, la respuesta es el **momento tres**.

### 1:07.8 – 1:11.1  ·  Texto: «un DSU que recuerda su historia»
*Cómo decirlo:* Cierre redondo, con satisfacción.

> Eso es un DSU Tree: un DSU con **memoria**.

### 1:11.1 – 1:23.5  ·  Diapositiva: operaciones y usos
*Cómo decirlo:* Claro y ordenado; «la estrella» con una sonrisa.

> Tiene cuatro operaciones: crear, unir, preguntar si dos elementos están conectados hoy… y la estrella: **cuándo** se conectaron. Sirve, por ejemplo, para redes que cambian con el tiempo.

### 1:23.5 – 1:28.5  ·  Aparecen los vectores del DSU auxiliar
*Cómo decirlo:* Tono de «vamos a abrir la caja».

> Por dentro: arriba, el DSU de siempre, más un vector nuevo: **nodo**.

### 1:28.5 – 1:34.1  ·  Aparecen los vectores del árbol de historia
*Cómo decirlo:* Explicativo, nombrando cada vector.

> Abajo, el árbol: el padre de cada nodo, su momento t y sus hijos.

### 1:34.1 – 1:40.0  ·  unite(1, 2): find de 1 y de 2
*Cómo decirlo:* Arranque de la demostración, con energía.

> Unimos el 1 y el 2. Buscamos sus raíces… y cada uno es su propia raíz.

### 1:40.0 – 1:44.2  ·  Raíces distintas; se marcan las hojas 1 y 2
*Cómo decirlo:* Decidido.

> Son raíces distintas: en el árbol, las hojas 1 y 2.

### 1:44.2 – 1:50.8  ·  Nace el nodo #6 y se llenan sus casillas
*Cómo decirlo:* Invita a mirar; énfasis en «casillas».

> Nace el nodo 6, con t igual a uno. Mira cómo se llenan las **casillas**.

### 1:50.8 – 1:58.2  ·  Cambian padre[2], tam[1] y nodo[1]
*Cómo decirlo:* Explicativo, pausado.

> Unión por tamaño: el 2 cuelga del 1… y el nodo 6 pasa a representar a todo el grupo.

### 1:58.2 – 2:05.5  ·  unite(3, 4): nace el nodo #7
*Cómo decirlo:* Ágil, «ya lo conocemos»; cierra y pasa la posta.

> Con el 3 y el 4, igual: nace el nodo 7, con t igual a dos.

## Voz 2 — Segunda parte

### 2:05.5 – 2:10.9  ·  unite(2, 4) y find(2)
*Cómo decirlo:* Entra con energía nueva: «ahora viene lo bueno».

> Ahora, lo interesante: unir el 2 con el 4. El 2 sube hasta el 1…

### 2:10.9 – 2:16.8  ·  find(4); se marcan los nodos 6 y 7
*Cómo decirlo:* Siguiendo el camino.

> …y el 4, hasta el 3. Raíces distintas: sus nodos son el 6 y el 7.

### 2:16.8 – 2:23.4  ·  Nace el nodo #8 sobre dos nodos amarillos
*Cómo decirlo:* Asombro: el árbol crece hacia arriba.

> Y encima de ellos nace el nodo 8: **momento tres**. El árbol crece hacia arriba.

### 2:23.4 – 2:30.0  ·  Unión por tamaño (2 y 2)
*Cómo decirlo:* Explicativo.

> Empatan en tamaño, así que el 3 cuelga del 1, y el nodo 8 representa a los cuatro.

### 2:30.0 – 2:35.5  ·  unite(1, 4) y find(1)
*Cómo decirlo:* Pícaro, como poniendo una trampa.

> ¿Y si unimos el 1 y el 4… otra vez? El 1 ya es raíz.

### 2:35.5 – 2:41.3  ·  find(4): 4 → 3 → 1 y compresión padre[4] = 1
*Cómo decirlo:* Revelación del truco; énfasis en «atajo».

> El 4 da dos saltos… así que toma un **atajo**: ahora apunta directo al 1.

### 2:41.3 – 2:46.5  ·  Texto en rojo: ya estaban conectados
*Cómo decirlo:* Firme; es un caso borde.

> Eso es compresión de caminos. Misma raíz: ya estaban conectados. **No** nace nada.

### 2:46.5 – 2:53.1  ·  whenConnected(1, 4) y los marcadores u, v
*Cómo decirlo:* Momento clave: baja el ritmo, voz más intensa.

> Momento clave: ¿cuándo se conectaron el 1 y el 4? Comparamos sus t… y sube el **menor**.

### 2:53.1 – 2:56.6  ·  Empate: sube u al nodo 6
*Cómo decirlo:* Narración de jugada, paso a paso.

> Empate en cero: sube u, al 6.

### 2:56.6 – 2:59.4  ·  Sube v al nodo 7
*Cómo decirlo:* Igual.

> Uno contra cero: sube v.

### 2:59.4 – 3:02.2  ·  Sube u al nodo 8
*Cómo decirlo:* Igual, con un poco más de tensión.

> Uno contra dos: sube u.

### 3:02.2 – 3:05.1  ·  Sube v al nodo 8
*Cómo decirlo:* Emoción creciente; remata con «¡también!».

> Tres contra dos… ¡y **también** llega al 8!

### 3:05.1 – 3:09.6  ·  u = v = #8, la respuesta en verde
*Cómo decirlo:* Triunfal; luego una pausa.

> Se encontraron en el 8: se conectaron en el **momento tres**.

### 3:09.6 – 3:17.4  ·  whenConnected(2, 5): el 5 no puede subir
*Cómo decirlo:* Curiosidad que se vuelve callejón sin salida.

> ¿Y el 2 con el 5? El 5 está solo: es raíz y no puede subir. No hay ancestro común…

### 3:17.4 – 3:21.7  ·  Resultado: −1
*Cómo decirlo:* Conclusión firme; otro caso borde.

> …así que la respuesta es **menos uno**: nunca se conectaron.

### 3:21.7 – 3:30.5  ·  unite(5, 2): nace el nodo #9
*Cómo decirlo:* Tranquilo; cierre de la demostración.

> Si unimos el 5 con el 2, nace el nodo 9, con t igual a cuatro. El 5, más pequeño, cuelga del 1.

### 3:30.5 – 3:44.0  ·  Pantalla dividida: islas a la izquierda, árbol a la derecha
*Cómo decirlo:* Emoción de cierre: «ahora mira todo junto»; deja respirar la animación al final.

> Ahora volvamos a las islas del inicio. A la izquierda, el DSU; a la derecha, el árbol que guarda la historia. Cada vez que dos islas se juntan… nace un nodo arriba.

### 3:44.0 – 3:47.7  ·  unite(11, 5) en rojo
*Cómo decirlo:* Rápido, constatando.

> El 11 y el 5 ya compartían isla: nada cambia.

### 3:47.7 – 3:55.7  ·  connected(1, 7): primero no, luego sí
*Cómo decirlo:* Pregunta y respuesta ágil; alegre en «ahora sí».

> ¿El 1 y el 7 están conectados? Todavía no: islas distintas. Tras la última unión… ahora sí.

### 3:55.7 – 4:04.5  ·  whenConnected(1, 11) = 8
*Cómo decirlo:* Retoma la pregunta del inicio con intriga; revelación al final.

> Y la pregunta del principio: ¿desde cuándo están conectados el 1 y el 11? Solo el árbol lo sabe… desde el **momento ocho**.

### 4:04.5 – 4:10.6  ·  Peor caso: la cadena de uniones
*Cómo decirlo:* Cambio a tono analítico.

> ¿Y cuánto cuesta todo esto? El peor caso es una cadena de uniones…

### 4:10.6 – 4:17.0  ·  Texto: la altura llega a n − 1
*Cómo decirlo:* Serio, explicando el porqué.

> …porque el árbol puede ser tan alto como n, y una consulta subirlo entero: **O de n**.

### 4:17.0 – 4:21.7  ·  Filas unite y connected
*Cómo decirlo:* Claro, sin prisa.

> Unir y preguntar si están conectados cuesta casi constante: alfa de n.

### 4:21.7 – 4:26.3  ·  Filas whenConnected y memoria
*Cómo decirlo:* Igual.

> Cuándo se conectaron depende de la altura. Y la memoria es lineal.

### 4:26.3 – 4:31.2  ·  Notas: α(n) y saltos binarios
*Cómo decirlo:* Dato extra, con interés.

> Con saltos binarios, la consulta bajaría a logaritmo de n.

## Las dos voces — Créditos

### 4:31.2 – 4:41.1  ·  Créditos
*Cómo decirlo:* Ambos, cálidos; pueden decirlo a dos voces.

> Esto fue DSU Tree, el DSU con memoria. ¡Gracias por vernos!
