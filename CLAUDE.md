# CLAUDE.md — Proyecto Final 2: DSU Tree animado (CS2023, UTEC, 2026-2)

> Lee este archivo COMPLETO antes de escribir cualquier código. Después, sigue la sección 10 (flujo de trabajo) y haz las preguntas de la sección 11 antes de construir.

---

## 0. Cómo debes trabajar

- Responde y escribe documentación en **español**. Los nombres de variables y funciones pueden ir en inglés.
- Empieza en **modo plan**: propón el diseño, espera confirmación del usuario y solo entonces implementa.
- Trabaja por hitos pequeños (sección 10). Haz commits frecuentes con mensajes claros.
- **No inventes datos.** No fabriques mediciones de rendimiento, citas, nombres de integrantes, números de código, enlaces ni puntos de la rúbrica. Si falta un dato, pregúntalo.
- **Verifica antes de afirmar.** No digas que algo funciona si no lo ejecutaste. Si no puedes ejecutar algo (por ejemplo, no hay LaTeX o ffmpeg instalado), dilo y explica qué falta.
- Antes de dar una tarea por terminada, ejecútala y revisa el resultado (pruebas, render, frames del video).
- Si algo del enunciado es ambiguo, **pregunta**, no asumas en silencio.

---

## 1. Contexto del proyecto

- **Curso:** CS2023 — Algoritmos y Estructuras de Datos, UTEC, ciclo 2026-2. **Profesor:** Wilder Nina Choquehuayta.
- **Proyecto:** "Proyecto Final 2 — Anima tu Algoritmo o Estructura de Datos".
- **Qué se pide:** elaborar un **video educativo, al estilo de Manim** (Mathematical Animation Engine), que explique y demuestre visualmente el funcionamiento de una estructura de datos implementada por el grupo. El enunciado menciona C/C++, pero también dice que el lenguaje y la herramienta de animación son de libre elección del grupo (no es obligatorio Python ni Manim). Esa tensión está resuelta en la sección 11.
- **Referencia de estilo:** el enunciado recomienda revisar los videos del canal 3Blue1Brown. El estilo objetivo está en la sección 7.
- **Grupo:** hasta 3 integrantes. **Entrega única y grupal** por Gradescope (solo un integrante la sube).
- **Fecha límite:** **22 de noviembre de 2026, 20:00** (hora de Bogotá). Hoy es 12 de noviembre de 2026.
- Si el grupo se inspira en un video o ejemplo de terceros, **debe citarlo explícitamente en el informe**.

---

## 2. Estructura asignada: DSU Tree

Definición del enunciado (ítem 14), parafraseada fielmente:

> Árbol construido a partir de un DSU que representa la **historia de las uniones** entre componentes. Permite registrar cómo se fusionan las componentes **a lo largo del tiempo** y puede usarse para responder consultas sobre **el momento en que dos nodos pasan a pertenecer a la misma componente**. Su construcción y utilidad dependen de la **variante específica** de DSU Tree empleada.

Consecuencias:

1. El grupo debe **elegir y documentar una variante concreta** (sección 5.1).
2. Esta estructura **NO es "DSU on tree" (Sack / small-to-large)**. Son técnicas distintas que comparten nombre. No implementes ni expliques Sack.
3. La base es el DSU clásico (`find`, `unite`, compresión de caminos, unión por tamaño). El DSU Tree añade la **historia** de las uniones.
4. El enunciado no fija complejidades para esta estructura: **hay que derivarlas y verificarlas** (sección 5.4).

---

## 3. Reglas obligatorias (no negociables)

Cada una viene del enunciado. Trátalas como criterios de aceptación.

**Sobre la animación real (la regla más importante):**

- [ ] La animación debe estar **impulsada por una implementación real** de la estructura, programada por el propio grupo.
- [ ] **No está permitido animar valores o pasos "a mano"** sin lógica real detrás. La escena de animación **no puede reimplementar** la lógica del DSU Tree; solo la dibuja a partir de lo que la implementación real produjo.
- [ ] **No se permite** usar una implementación ya existente de la estructura asignada (de librerías estándar o de terceros). Los contenedores básicos (`std::vector`, listas, etc.) sí están permitidos. Está permitido usar el sistema de dibujo de Manim solo para **renderizar** (posiciones, formas), nunca para decidir cómo evoluciona la estructura.

**Sobre el contenido mínimo del video:**

- [ ] **Introducción conceptual:** qué es la estructura, qué **Tipo de Dato Abstracto (TDA)** representa y para qué se usa en la práctica.
- [ ] **Demostración animada de las operaciones principales** de la estructura.
- [ ] **Al menos un caso borde relevante** (estructura vacía, un solo elemento, peor caso, etc.).
- [ ] **Breve análisis de complejidad temporal** de las operaciones mostradas.
- [ ] **Título del proyecto y nombres de los integrantes**, al inicio o en los créditos finales.

**Sobre el formato:**

- [ ] Duración sugerida: **1 a 2 minutos**. **Nunca debe exceder 5 minutos.** Por decisión del usuario (12 nov 2026), la claridad manda sobre la brevedad: se puede pasar de 2 minutos con ritmo pausado, apuntando a **3:30–4:15** y con margen bajo 5:00 (ver 11.1).
- [ ] Narración permitida: voz en off, texto en pantalla, o ambos.
- [ ] Video final en **MPEG-4 (`.mp4`)**, **alta resolución** (mínimo 1920×1080).
- [ ] Si el `.mp4` excede el límite de tamaño de Gradescope, se incluye un **enlace** (YouTube no listado, Drive, etc.) dentro del informe.

**Sobre los entregables** (detalle en la sección 8): repositorio de GitHub con `README.md`, video `.mp4`, informe breve en PDF. **Los enlaces deben funcionar.**

---

## 4. Arquitectura: lógica real → traza → animación

Para cumplir la regla de "animación real, no simulada", usa esta arquitectura. Es la decisión central del proyecto.

```
 [Escenario de entrada]        [Implementación real]            [Traza]              [Animación]
  scenarios/demo.txt   --->   dsu_tree.cpp (C++17)   --->   trace.json   --->   Manim CE (Python)
  (operaciones)               calcula TODO el estado        eventos que         solo DIBUJA lo que
                              y emite eventos               la lógica produjo   dice la traza
```

**Definición de "traza":** el registro ordenado de eventos que emite la implementación real mientras ejecuta las operaciones. Cada evento describe algo que el código **realmente hizo**.

Principios:

1. **La lógica vive solo en la implementación real.** Manim no calcula raíces, tamaños, tiempos ni resultados de consultas: los lee de la traza.
2. **La traza se regenera en cada render.** El script de render compila la implementación, la ejecuta sobre el escenario y produce `trace.json`; después Manim lo lee. Nunca se escribe `trace.json` a mano ni se reutiliza uno viejo sin regenerarlo. Así se puede demostrar que el video sale del código.
3. **Un solo comando** reproduce el video completo (`make video` o `scripts/render.sh`). Documéntalo en el README.
4. **La traza contiene los pasos internos**, no solo los resultados: por ejemplo, el camino recorrido por cada `find`, las raíces comparadas, qué componente se cuelga de cuál, el nodo nuevo creado y, en cada consulta, los ancestros recorridos hasta el punto de encuentro.
5. En el video, muestra brevemente que la animación sale del código (por ejemplo, un fragmento del código o un mensaje "trazas generadas por `dsu_tree.cpp`"). Eso refuerza el cumplimiento de la regla ante quien califique.

Esquema de eventos sugerido (ajústalo al diseño final):

```json
{"op": "init",  "n": 6}
{"op": "find",  "x": 3, "path": [3, 8, 9], "root": 9, "compressed": [[3, 9]]}
{"op": "unite", "a": 1, "b": 2, "t": 1, "rootA": 1, "rootB": 2,
                "merged": true, "newNode": 7, "children": [1, 2]}
{"op": "unite", "a": 1, "b": 2, "merged": false, "reason": "ya conectados"}
{"op": "query", "a": 1, "b": 4, "answer": 3, "meetNode": 9,
                "climbA": [1, 7, 9], "climbB": [4, 8, 9]}
```

Si la implementación y la animación están en lenguajes distintos (C++ y Python), la traza es la única interfaz entre ambos. Valídala con un esquema (JSON Schema o validación sencilla en Python) para detectar errores pronto.

---

## 5. Especificación de la implementación

### 5.1 Variante a implementar

Implementa la **Variante A** y documenta la **Variante B** como comparación en el informe (opcional, solo si el tiempo alcanza).

- **Variante A (principal) — árbol de historia con un nodo nuevo por unión.** Los nodos `1..n` son hojas. Cada unión efectiva de dos componentes crea un nodo interno nuevo (`n+1`, `n+2`, ...) que es padre de las raíces de ambas componentes y guarda el momento `t` de la unión. El momento en que `a` y `b` se conectan es el `t` de su **ancestro común más cercano** (LCA) en este árbol. Es la variante más visual: el árbol "crece" con cada unión.
- **Variante B (comparación) — DSU con unión por tamaño, sin compresión de caminos, con marcas de tiempo.** Cada arista padre→hijo guarda el momento en que se creó. La consulta sube desde ambos nodos comparando marcas de tiempo.

### 5.2 API mínima (variante A)

Define y documenta, en C++17, algo equivalente a:

```cpp
class DSUTree {
public:
    explicit DSUTree(int n);                    // n hojas, sin uniones
    bool unite(int a, int b);                   // true si fusionó dos componentes distintas
    bool connected(int a, int b);               // ¿están hoy en la misma componente?
    int  whenConnected(int a, int b) const;     // momento de la unión, 0 si a==b, -1 si nunca se unieron
};
```

Decisiones que debes tomar y documentar: qué significa exactamente el "momento" `t` (sugerido: el número de unión efectiva, `1..n-1`), y qué devuelve la consulta en cada caso borde.

Para tener un `find` eficiente, usa un DSU auxiliar con **unión por tamaño y compresión de caminos**, que apunte al nodo del árbol de historia vigente de cada componente. Mantén **separados** el arreglo del DSU auxiliar (que la compresión modifica) y los arreglos del árbol de historia (que no deben alterarse).

### 5.3 Instrumentación de la traza

El código debe poder emitir eventos sin ensuciar la lógica (por ejemplo, un parámetro opcional `Trace*` o un observador). Si no hay traza activa, la estructura debe funcionar igual y sin costo apreciable.

### 5.4 Complejidad (debes derivarla y verificarla, no asumirla)

Los siguientes valores son **hipótesis de partida** que hay que justificar en el informe y confirmar con mediciones:

- **Memoria:** el árbol de historia tiene como máximo `2n − 1` nodos → O(n).
- **`unite` (variante A):** O(α(n)) amortizado con el DSU auxiliar (unión por tamaño + compresión) más O(1) por crear el nodo.
- **`whenConnected` (variante A):** subir por ancestros cuesta O(h), con `h` la altura del árbol de historia, que en el peor caso es O(n) (una cadena de uniones). Si hace falta O(log n), se puede preprocesar saltos binarios (binary lifting) una vez construido el árbol. Decide qué variante de consulta se implementa y explícala.
- **Variante B:** con unión por tamaño y sin compresión, la altura es O(log n), así que `unite` y la consulta cuestan O(log n).

Para la evidencia empírica: mide tiempos con tamaños crecientes (por ejemplo, 10³ a 10⁶), repite las mediciones y grafica. Registra el hardware y el compilador. **Nunca escribas números que no hayas medido.**

### 5.5 Pruebas (obligatorias)

- Escribe un **oráculo ingenuo**: tras cada unión efectiva, recorre todos los pares y anota el primer momento en que se conectan.
- Compara `whenConnected` contra el oráculo en **muchas ejecuciones aleatorias** (por ejemplo, `n ≤ 10`, todas las parejas) y en casos fijos (n = 1, sin uniones, uniones repetidas, cadena de uniones).
- Las pruebas corren con un solo comando y deben pasar antes de pasar a la animación.

### 5.6 Casos borde a cubrir

Cubre todos en el código y elige 1 o 2 para mostrar en el video:

- `unite(a, b)` cuando ya están en la misma componente (no se crea nodo nuevo, devuelve `false`).
- Consulta entre dos nodos que **nunca** se unieron (devuelve `-1`).
- Consulta de un nodo consigo mismo.
- `n = 1` (sin uniones posibles).
- Cadena de `n−1` uniones (peor caso para la altura del árbol de historia).

---

## 6. Especificación del video

### 6.1 Guion sugerido (≈ 2:00; ajusta tiempos al narrar)

| Tiempo | Escena | Contenido |
|--------|--------|-----------|
| 0:00–0:10 | Gancho y título | Pregunta: "¿cuándo se conectaron estos dos nodos?". Título del proyecto. |
| 0:10–0:30 | Concepto | Recordar el DSU (conjuntos que se fusionan). Qué es el DSU Tree: el DSU **con memoria**. TDA: operaciones `unite`, `connected`, `whenConnected`. Para qué sirve. |
| 0:30–1:05 | Demostración de uniones | Escenario pequeño (n = 6 o 7). Cada `unite` fusiona dos componentes y **crece** un nodo de unión que lleva su momento `t`. |
| 1:05–1:25 | Consulta | `whenConnected(a, b)`: se resaltan los ancestros hasta el LCA y aparece la respuesta. |
| 1:25–1:40 | Casos borde | Unión repetida (ya conectados) y/o consulta de nodos que nunca se unen. |
| 1:40–1:55 | Complejidad | Tabla breve con las complejidades que **verificaste**. |
| 1:55–2:00 | Créditos | Título e integrantes (más referencias de estilo/música si aplica). |

### 6.2 Principios de contenido

- **Una idea por escena.** No muestres más de lo necesario; el video es corto.
- **Revelación progresiva:** construye el árbol paso a paso, nunca todo a la vez.
- **Misma estructura, mismo ejemplo:** usa el mismo escenario en el concepto, la demostración y la consulta para que se vea la continuidad.
- **Texto mínimo en pantalla:** frases cortas (máximo 2 líneas), tamaño legible en 1080p.
- Escribe **primero el guion de narración** con tiempos, y luego ajusta las animaciones al guion (no al revés).

---

## 7. Guía de estilo: 3Blue1Brown

> Nota honesta: este estilo se derivó de la documentación oficial de 3Blue1Brown, de su repositorio de código y de guías sobre su estilo. No es un conjunto de reglas oficiales del canal. Replica el espíritu, no los activos.

### 7.1 Herramientas

- **Manim Community Edition** (paquete `manim` de PyPI). No uses ManimGL (`manimgl`). La versión 0.22.1 exige **Python ≥ 3.11**.
- Necesitas **ffmpeg** y una distribución de **LaTeX** (TeX Live o MiKTeX) para `MathTex`/`Tex`. Verifica que estén instalados antes de empezar.
- Cada escena es una clase de Python con un método `construct`.
- Manim produce **clips sueltos**; el montaje final (voz, música, cortes) se hace en un editor de video tradicional. Nadie debe forzar a Manim a sincronizar la narración.

### 7.2 Configuración base

Los valores por defecto de Manim CE ya usan fondo negro y 1080p a 60 fps. Fíjalos igualmente en `manim.cfg` para que sean explícitos:

```ini
[CLI]
background_color = BLACK
pixel_height = 1080
pixel_width = 1920
frame_rate = 60
```

- 3Blue1Brown renderiza en 4K a 30 fps y fondo `#000000`. Para este proyecto basta **1080p60** (`-qh`).
- **Borradores:** `manim -ql` (480p15). **Versión final:** `manim -qh` (1080p60). No renderices en alta calidad mientras iteras.

### 7.3 Tipografía

- Texto normal: fuente **"CMU Serif"** (la versión Unicode de Computer Modern, la de LaTeX), como en su configuración. Instálala y verifica que Manim la encuentre; si no está disponible, usa "Latin Modern Roman" o la serif más parecida y anótalo.
- Fórmulas y etiquetas de nodos: `MathTex`/`Tex` (Computer Modern por defecto), para el aspecto "de libro".
- Fija la fuente una vez: `Text.set_default(font="CMU Serif")`.

### 7.4 Paleta de colores

Valores verificados en el código de Manim CE 0.22.1. **Importa las constantes de Manim**, no escribas hex a mano.

| Constante | Hex | Rol en este proyecto |
|-----------|-----|----------------------|
| `BLACK` | `#000000` | Fondo |
| `WHITE` | `#FFFFFF` | Texto principal |
| `BLUE_C` (= `BLUE`) | `#58C4DD` | Color principal: hojas (nodos originales) |
| `BLUE_E` | `#236B8E` | Relleno suave de hojas |
| `BLUE_B` | `#9CDCEB` | Azul claro para detalles |
| `YELLOW_C` | `#F7D96F` | Nodos de unión (la "historia") |
| `GOLD_C` | `#F0AC5F` | Acento secundario |
| `RED_C` | `#FC6255` | Consultas y casos borde |
| `GREEN_C` | `#83C167` | Resultado / respuesta |
| `TEAL_C` | `#5CD0B3` | Componentes activas |
| `GREY_BROWN` | `#736357` | Elementos secundarios |

Regla central: **un color, un concepto**. El mismo elemento lleva el mismo color en todo el video. No uses más de 4 o 5 colores por escena.

### 7.5 Animación y ritmo

- **Transforma, no reemplaces.** Cuando algo cambia de estado, usa `Transform`/`ReplacementTransform` para que el espectador vea la continuidad (por ejemplo, el nodo de unión nace **desde** las dos raíces que fusiona).
- Animaciones habituales: `Write` (texto y fórmulas), `FadeIn` con un pequeño desplazamiento, `Create` (aristas y formas), `ReplacementTransform`, `TransformMatchingTex` (fórmulas), `Indicate` y `Circumscribe` (resaltar), `LaggedStart` (varios elementos con desfase), `FadeOut` (salidas).
- **Función de ritmo:** `smooth` (la curva por defecto de Manim). Evita movimientos lineales y rebotes.
- **Duraciones:** `run_time` entre 0.6 y 1.5 s para la mayoría de las animaciones. `self.wait(0.5–1.5)` tras cada paso importante, para que se pueda **leer**. Deja 1–2 s para leer cada fórmula nueva.
- **Pausa de comprensión:** tras el momento clave (la consulta y su respuesta) deja respirar la animación.
- **Cámara:** estática en lo posible. Usa `MovingCameraScene` solo para un zoom justificado.
- **Transiciones entre escenas:** sencillas (el contenido se desvanece o continúa por transformación). Evita efectos vistosos (wipes, giros, rebotes).
- **Composición:** el árbol ocupa la zona principal; texto breve arriba o al lado; una **leyenda** pequeña y discreta con el significado de los colores. Márgenes seguros alrededor.

### 7.6 Estética de los nodos

- Hoja: círculo con borde `BLUE_C`, relleno `BLUE_E` con opacidad ~0.5 y la etiqueta en `MathTex` blanca.
- Nodo de unión: borde `YELLOW_C`, con el valor `t` visible junto al nodo o dentro de él.
- Aristas: líneas finas y claras, que aparecen con `Create`.
- La disposición del árbol debe ser estable: no hagas que los nodos "salten" entre pasos. El nuevo nodo de unión se ubica **encima** de sus hijos.

### 7.7 Audio

- Narración en **español** (ver sección 11), en un solo tono y ritmo tranquilos. Graba con un **buen micrófono** en un lugar silencioso, y limpia ruido en el editor.
- **Música:** instrumental, baja, que no compita con la voz. **No uses la música de Vincent Rubinetti ni otros activos de 3Blue1Brown** sin permiso. Usa música libre con licencia clara (por ejemplo, Creative Commons con atribución), **lee su licencia** y cítala en el informe y en los créditos.
- Montaje: unir clips, voz y música en un editor tradicional (DaVinci Resolve, Kdenlive, Premiere u otro). El grupo decide cuál.

### 7.8 Lo que NO debes hacer

- No copies código, escenas ni recursos del repositorio `3b1b/videos` (su código tiene licencia propia). Escribe tus escenas desde cero con Manim CE.
- No uses mascotas, personajes ni logotipos de 3Blue1Brown.
- No imites su logo, nombre ni voz. El video es del grupo; 3Blue1Brown solo es una **inspiración**, y se cita como tal.

---

## 8. Entregables

### 8.1 Repositorio de GitHub (con `README.md`)

El `README.md` debe incluir: descripción del proyecto, **software requerido con versiones** (compilador C++, Python, Manim, ffmpeg, LaTeX, fuentes), **pasos exactos para compilar y ejecutar**, cómo reproducir el video (un comando), estructura de carpetas, y créditos.

Estructura sugerida:

```
dsu-tree-video/
├── README.md
├── CLAUDE.md
├── Makefile                  # make test | make trace | make video
├── src/                      # dsu_tree.hpp, dsu_tree.cpp, trace_main.cpp
├── tests/                    # oráculo ingenuo y pruebas aleatorias
├── scenarios/                # escenarios de operaciones (entrada)
├── anim/                     # theme.py, trace_loader.py, scenes.py
├── scripts/                  # render.sh, benchmark
├── report/                   # fuente del informe (PDF)
└── media/                    # salida del render (video final)
```

### 8.2 Video

`.mp4` (MPEG-4), mínimo 1920×1080. Verifica con `ffprobe`: duración (≤ 5 min; objetivo ≈ 2 min), resolución, códec y tamaño. Si excede el límite de Gradescope, súbelo como **enlace** (YouTube no listado o Drive) y colócalo en el informe. Comprueba que el enlace funciona **sin iniciar sesión**.

### 8.3 Informe PDF (breve)

Debe contener, en este orden:

1. **Carátula:** curso, integrantes, estructura asignada (DSU Tree).
2. **Descripción de la estructura** y su TDA (operaciones, invariantes, variante elegida).
3. **Herramientas usadas** y **pasos para reproducir el video**.
4. **Contribuciones de cada integrante.**
5. **Análisis de complejidad** (con la derivación y la evidencia empírica).
6. **Evidencia:** capturas o enlace, más el **enlace al repositorio** y el **enlace al video**.
7. **Al menos 2 conclusiones.**
8. **Referencias y citas:** 3Blue1Brown como inspiración, Manim, música, fuentes y cualquier tercero. Si usaron un video o ejemplo de terceros, cítenlo explícitamente.

Todo enlace debe verificarse antes de entregar.

---

## 9. Rúbrica y auto-auditoría

La calificación usa una rúbrica publicada en Gradescope. **Su detalle exacto no está en el enunciado**: solo dice que evalúa **implementación, animación, contenido explicativo e informe**. Pide al usuario que pegue la rúbrica en cuanto esté disponible y ajusta esta sección a ella. No inventes puntajes.

Mientras tanto, usa esta auto-auditoría. Antes de cada entrega parcial y de la final, recórrela y reporta con evidencia (comando ejecutado y resultado).

**Implementación**
- [ ] Implementación propia, sin usar la estructura de una librería.
- [ ] Pasa las pruebas contra el oráculo (aleatorias y casos fijos).
- [ ] Cubre los casos borde de la sección 5.6.
- [ ] Código claro, comentado donde la idea no es obvia, compilable con un comando.

**Animación**
- [ ] La animación sale de la traza generada por el código real (sin lógica duplicada en Manim).
- [ ] Un solo comando regenera traza y video.
- [ ] Estilo coherente con la sección 7 (paleta, tipografía, ritmo, transformaciones).
- [ ] Sin solapamientos ni texto ilegible (se revisan frames extraídos con `ffmpeg`).

**Contenido explicativo**
- [ ] Introducción: qué es, qué TDA representa, para qué sirve.
- [ ] Demostración de las operaciones principales.
- [ ] Al menos un caso borde mostrado.
- [ ] Análisis de complejidad breve y correcto.
- [ ] Título e integrantes en el video.
- [ ] Duración ≤ 5 min (objetivo ≈ 2 min).

**Informe**
- [ ] Contiene todos los apartados de 8.3.
- [ ] Enlaces al repositorio y al video funcionan.
- [ ] Al menos 2 conclusiones.
- [ ] Citas de inspiración y terceros.

**Entrega**
- [ ] Repositorio con `README.md` completo.
- [ ] `.mp4` (o enlace en el informe) y PDF listos antes del plazo.
- [ ] Solo un integrante sube la entrega a Gradescope.

---

## 10. Flujo de trabajo e hitos

Plan sugerido hasta el 22 de noviembre (deja siempre un día de margen):

| Fechas | Hito |
|--------|------|
| 12–13 nov | Resolver las decisiones abiertas (sección 11). Diseño y API. Implementación y pruebas contra el oráculo. |
| 14–15 nov | Instrumentación de la traza y su validación. Tema de Manim (`theme.py`) y primeras escenas en borrador (`-ql`). |
| 16–17 nov | Todas las escenas. Guion de narración con tiempos. Revisión de frames. |
| 18–19 nov | Narración, música, montaje y render final (`-qh`). Mediciones para el análisis de complejidad. |
| 20 nov | `README.md`, informe PDF, verificación de enlaces. |
| 21 nov | Margen y prueba de entrega completa. |
| 22 nov, 20:00 | **Límite de entrega.** |

Reglas de proceso:

1. **Orden obligatorio:** implementación y pruebas → traza → animación. No empieces a animar con una implementación sin validar.
2. Cada hito termina con **evidencia ejecutada** (salida de las pruebas, el comando de render, frames revisados), no con afirmaciones.
3. Revisa los frames del video con `ffmpeg` (extrae imágenes en instantes clave) y comprueba: sin solapamientos, texto legible, colores coherentes, márgenes seguros.
4. Mide la duración con `ffprobe` al final de cada render.
5. Pide al usuario que revise cada borrador antes de seguir. Muestra los avances pronto.

---

## 11. Decisiones abiertas — pregunta al usuario ANTES de construir

Propón el valor por defecto indicado y espera confirmación.

1. **Lenguaje de la implementación.** Por defecto: **C++17** (el enunciado menciona C/C++, y cumple también la lectura de "libre elección"). La animación se hace en Python con Manim CE y lee la traza.
2. **Variante de DSU Tree.** Por defecto: **variante A** (nodo nuevo por unión), con la variante B como comparación opcional en el informe.
3. **Idioma del video y del informe.** Por defecto: **español**.
4. **Narración.** ¿Voz en off, texto en pantalla, o ambos? Por defecto: ambos (texto breve y voz).
5. **Integrantes.** Nombres completos y cuántos son (hasta 3). **No inventes nombres.**
6. **Entorno.** Sistema operativo, versión de Python (≥ 3.11), compilador y si hay LaTeX, ffmpeg y la fuente CMU Serif instalados.
7. **Editor de video** para el montaje final y la música a usar (con su licencia).
8. **Límite de tamaño de Gradescope** para el video. Si se desconoce, planifica el **enlace** como respaldo.
9. **Rúbrica de Gradescope.** Pedir que la peguen cuando esté disponible.

### 11.1 Decisiones tomadas (12 nov 2026)

| # | Decisión | Estado |
|---|----------|--------|
| 1 | C++17 (implementación) + Manim CE (animación) | Confirmado |
| 2 | Variante A implementada; B solo como comparación opcional | Confirmado |
| 3 | Español | Confirmado |
| 4 | Texto en pantalla **desacoplado** (se apaga con `DSU_CAPTIONS=0` sin romper el layout) **+ voz en off de dos integrantes** (decisión del 20 nov 2026). Guion con timestamps medidos sobre `media/dsu_tree_1080p60.mp4` en `guion/guion_narracion.md`; si cambia el video, volver a medir con `scripts/timeline_run.py` (render `--dry_run`). | Confirmado |
| 5 | Integrantes | **Pendiente** — usar un marcador visible en créditos e informe hasta que el usuario los dé |
| 6 | Windows 11, Python 3.12.10 (`.venv` del proyecto), g++ 16.1.0 (MSYS2 UCRT64, enlazado `-static`), Manim CE 0.22.1, MiKTeX 25.12, ffmpeg 9.0.2 (winget `Gyan.FFmpeg`), CMU Serif instalada desde el paquete MiKTeX `cm-unicode`. No hay `make`: usar `scripts/build.sh`. | Verificado |
| 7 | Editor: **DaVinci Resolve**. Música: **ninguna** (decisión del usuario, 15 nov 2026). | Decidido |
| 8 | Límite de Gradescope | Pendiente — planificar enlace como respaldo |
| 9 | Rúbrica | Pendiente |

Preferencia del usuario: **no escribir comentarios dentro del código**; la explicación va en el README y el informe.

**Duración y ritmo (decisión del usuario):** no acelerar el video para que entre en 1–2 minutos. Lo importante es que se entienda exactamente qué pasa en cada operación (cada `find`, la comparación de raíces, la unión por tamaño, el nodo nuevo, cada paso de la consulta), con calma y tiempo de lectura. El único límite duro es **5 minutos**; objetivo 3:30–4:15.

---

## 12. Advertencias finales

- "DSU Tree" ≠ "DSU on tree". No mezclar.
- La animación **no simula**: la lógica está en la implementación y la traza se regenera en cada render.
- No afirmes complejidades ni tiempos sin derivarlos y medirlos.
- No copies activos ni código de 3Blue1Brown; cítalo como inspiración.
- No entregues sin verificar los enlaces, la duración (≤ 5 min), la resolución y el formato (`.mp4`).
- Ante la duda sobre el enunciado, **pregunta**. El enunciado manda sobre este archivo.
