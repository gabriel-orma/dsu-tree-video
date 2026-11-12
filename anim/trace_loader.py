import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TRACE_DIR = PROJECT_ROOT / "build" / "traces"

REQUIRED_FIELDS = {
    "init": {"n", "dsuParent", "compNode"},
    "find": {"x", "path", "root", "compressed"},
    "unite": {"a", "b", "rootA", "rootB", "merged"},
    "connected": {"a", "b", "rootA", "rootB", "answer"},
    "query": {"a", "b", "answer", "meetNode", "climbA", "climbB", "steps"},
}
MERGED_FIELDS = {"t", "newNode", "children", "dsuChild", "dsuParent", "size"}


class TraceError(ValueError):
    pass


def trace_dir() -> Path:
    return Path(os.environ.get("DSU_TRACE_DIR", DEFAULT_TRACE_DIR))


def load_trace(scenario: str) -> list[dict]:
    path = trace_dir() / f"{scenario}.json"
    if not path.exists():
        raise TraceError(f"no existe {path}; genera las trazas con scripts/render.sh")
    events = json.loads(path.read_text(encoding="utf-8"))
    validate(events)
    return events


def validate(events: list[dict]) -> None:
    if not isinstance(events, list) or not events:
        raise TraceError("la traza esta vacia")
    if events[0].get("op") != "init":
        raise TraceError("la traza debe empezar con init")
    n = events[0]["n"]
    expected_t = 0
    for index, event in enumerate(events):
        op = event.get("op")
        if op not in REQUIRED_FIELDS:
            raise TraceError(f"evento {index}: operacion desconocida {op!r}")
        if op == "init" and index != 0:
            raise TraceError(f"evento {index}: init repetido")
        missing = REQUIRED_FIELDS[op] - event.keys()
        if op == "unite" and event.get("merged"):
            missing |= MERGED_FIELDS - event.keys()
            expected_t += 1
            if event.get("t") != expected_t or event.get("newNode") != n + expected_t:
                raise TraceError(f"evento {index}: t o newNode fuera de secuencia")
        if missing:
            raise TraceError(f"evento {index} ({op}): faltan {sorted(missing)}")
