# DSU Tree: el DSU con memoria

Proyecto Final 2 de CS2023 Algoritmos y Estructuras de Datos (UTEC, 2026-2), Grupo 14.

Video educativo, al estilo de Manim, que explica y demuestra el **DSU Tree**: un DSU que guarda la historia de sus uniones en un árbol y puede responder **en qué momento** dos elementos quedaron en el mismo grupo.

- **Video:** https://www.youtube.com/watch?v=iYJlmo8y9Ao
- **Informe:** [`report/Informe_Grupo14_DSU_Tree.pdf`](report/Informe_Grupo14_DSU_Tree.pdf) (versión editable: [`report/Informe_Grupo14_DSU_Tree.docx`](report/Informe_Grupo14_DSU_Tree.docx))
- **Integrantes:** Ormachea Mamani Gabriel, Sanchez Echevarria Andre Gianfranco
- **Profesor:** Wilder Nina Choquehuayta

## La estructura

Implementamos la variante con **un nodo nuevo por unión**, en C++17 (`src/dsu_tree.hpp`, `src/dsu_tree.cpp`):

| Operación | Qué hace | Costo |
|---|---|---|
| `DSUTree(n)` | n elementos (1 a n), cada uno en su propio grupo | O(n) |
| `unite(a, b)` | une los grupos de a y b; `true` si eran distintos | O(α(n)) amortizado |
| `connected(a, b)` | ¿están hoy en el mismo grupo? | O(α(n)) amortizado |
| `whenConnected(a, b)` | momento t en que se conectaron; `0` si a = b, `-1` si nunca | O(h), con h ≤ n − 1 |

- Los elementos 1 a n son hojas del **árbol de historia**. La unión efectiva número `t` crea el nodo `n + t`, padre de los nodos que representaban a los dos grupos, y guarda `t`. Como `t` crece hacia arriba, la respuesta de `whenConnected` es el `t` del ancestro común más cercano.
- Un **DSU auxiliar** (unión por tamaño y compresión de caminos) encuentra rápido el grupo de cada elemento. Sus vectores (`dsuParent_`, `dsuSize_`, `compNode_`) están separados de los del árbol de historia (`treeParent_`, `treeTime_`, `treeChildren_`), que la compresión nunca modifica.
- `whenConnected` sube con dos marcadores: en cada paso sube el de menor `t` (si empatan, el de `a`). Si el que debe subir no tiene padre, no hay ancestro común y devuelve `-1`.
- Un elemento fuera de 1..n lanza `std::out_of_range`, y un `n` negativo lanza `std::invalid_argument`.

## La animación sale del código

```
scenarios/*.txt  ->  dsu_tree.cpp (C++17)  ->  build/traces/*.json  ->  Manim (Python)
 operaciones          ejecuta y registra          eventos reales         solo dibuja
```

`DSUTree` recibe un `Trace*` opcional. Cuando existe, registra cada paso real (el camino de cada `find`, la compresión, las raíces comparadas, qué raíz cuelga de cuál, el nodo nuevo, cada paso de la consulta) y una copia de todos sus vectores después de cada operación. Sin traza, la estructura funciona igual y no registra nada.

`anim/trace_loader.py` valida la traza, y las escenas de `anim/` solo deciden posiciones, colores y transiciones: los números, raíces, momentos y respuestas que se ven en el video vienen de la ejecución real. `scripts/render.sh` compila, corre las pruebas y regenera las trazas en cada render.

## Software requerido

| Herramienta | Versión usada |
|---|---|
| g++ (MSYS2 UCRT64) | 16.1.0, C++17 |
| Python | 3.12.10 |
| Manim Community Edition | 0.22.1 |
| matplotlib (solo para la gráfica del benchmark) | 3.11.2 |
| MiKTeX (LaTeX para las fórmulas) | 25.12 |
| ffmpeg | 9.0.2 |
| Fuente CMU Serif | paquete `cm-unicode` de MiKTeX |
| Bash | Git Bash (en Windows) |

## Cómo compilar y reproducir

Desde la raíz del repositorio, en Git Bash:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # en Linux/macOS: .venv/bin/python
bash scripts/build.sh test       # compila y corre las pruebas
bash scripts/build.sh trace      # genera build/traces/*.json desde scenarios/
bash scripts/render.sh           # borrador 480p de todo el video
QUALITY=k bash scripts/render.sh # versión final 4K 60 fps
```

`render.sh` sin argumentos renderiza las ocho escenas y las une en `media/dsu_tree_<calidad>.mp4` (`QUALITY` = `l`, `m`, `h`, `p` o `k`). Con nombres de escena (`bash scripts/render.sh PasoAPaso`) renderiza solo esas. Con `DSU_CAPTIONS=0` se renderiza sin el texto en pantalla.

Desde PowerShell, `bash` abre WSL; hay que usar Git Bash:

```powershell
& "C:\Program Files\Git\bin\bash.exe" scripts/render.sh
```

### Pruebas

`tests/test_dsu_tree.cpp` compara `whenConnected` y `connected` contra un oráculo ingenuo en 5000 ejecuciones al azar (n de 1 a 10, todas las parejas), prueba casos fijos (n = 0, n = 1, sin uniones, uniones repetidas, cadena con n = 2000), invariantes del árbol y que la traza no cambie los resultados. Resultado actual: 4 795 024 comprobaciones, 0 fallos.

### Benchmark

```bash
g++ -std=c++17 -O2 -static src/dsu_tree.cpp bench/bench_dsu_tree.cpp -o build/bench_dsu_tree
build/bench_dsu_tree > report/benchmark.csv
.venv/Scripts/python bench/plot_benchmark.py
```

Mide `unite` y `whenConnected` con n de 10³ a 10⁶ (mediana de 5 repeticiones), con uniones al azar y con una cadena (peor caso). Los resultados están en `report/benchmark.csv` y en el informe.

## Estructura de carpetas

```
src/          dsu_tree.hpp, dsu_tree.cpp, trace.hpp, trace_main.cpp
tests/        oráculo ingenuo y pruebas
bench/        benchmark de tiempos y su gráfica
scenarios/    operaciones de cada escena (idea, paso, grande, cadena)
anim/         escenas de Manim, tema, vistas y lector de trazas
scripts/      build.sh, render.sh y timeline_run.py (mide los tiempos del video)
guion/        guion de narración a dos voces con timestamps
report/       informe, figuras sacadas del video y datos del benchmark
media/        salida del render (no se versiona)
```

## Créditos

- Ormachea Mamani Gabriel y Sanchez Echevarria Andre Gianfranco.
- Estilo visual inspirado en los videos de 3Blue1Brown. No se usó código ni recursos de 3Blue1Brown.
- Animación hecha con [Manim Community Edition](https://docs.manim.community).
