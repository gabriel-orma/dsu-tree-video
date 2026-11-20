import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "report" / "benchmark.csv"
target = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "report" / "figuras" / "fig11_tiempos.png"

rows = list(csv.DictReader(source.open(encoding="utf-8")))
cases = {"aleatorio": ("uniones al azar", "o", "-"), "cadena": ("cadena (peor caso)", "s", "--")}

plt.rcParams.update({"font.family": "Calibri", "font.size": 11})
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for case, (label, marker, style) in cases.items():
    data = [r for r in rows if r["caso"] == case]
    n = [int(r["n"]) for r in data]
    axes[0].plot(n, [float(r["unite_ns"]) for r in data], marker=marker, linestyle=style, color="black", label=label)
    axes[1].plot(n, [float(r["query_ns"]) / 1000 for r in data], marker=marker, linestyle=style, color="black", label=label)

axes[0].set_title("unite: tiempo por llamada")
axes[0].set_ylabel("nanosegundos")
axes[0].set_ylim(bottom=0)
axes[1].set_title("whenConnected: tiempo por consulta")
axes[1].set_ylabel("microsegundos")
axes[1].set_yscale("log")
for ax in axes:
    ax.set_xscale("log")
    ax.set_xlabel("n (número de elementos)")
    ax.grid(True, which="major", color="0.85")
    ax.legend(frameon=False)
fig.tight_layout()
target.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(target, dpi=200)
print(target)
