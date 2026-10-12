import json
import sys
from collections import Counter
from pathlib import Path


def _known_errors(entries: list[str]) -> Counter[tuple[str, str]]:
    known: Counter[tuple[str, str]] = Counter()
    for entry in entries:
        tool, code, filename, count_text = entry.split(maxsplit=3)
        if tool != "ruff" or not count_text.startswith("x"):
            raise ValueError(f"Nieznany wpis punktu odniesienia: {entry}")
        known[(code, Path(filename).as_posix())] += int(count_text[1:])
    return known


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / ".ai" / "warsztat.json").read_text(encoding="utf-8"))
    baseline = _known_errors(config["odniesienie"]["znane"])
    diagnostics = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    actual: Counter[tuple[str, str]] = Counter()

    for diagnostic in diagnostics:
        filename = Path(diagnostic["filename"]).resolve()
        relative_filename = filename.relative_to(root).as_posix()
        actual[(diagnostic["code"], relative_filename)] += 1

    unexpected = {
        key: count - baseline.get(key, 0)
        for key, count in actual.items()
        if count > baseline.get(key, 0)
    }
    if unexpected:
        print("Nowe błędy Ruff poza punktem odniesienia:")
        for (code, filename), count in sorted(unexpected.items()):
            print(f"  {code} {filename} x{count}")
        return 1

    print(f"Ruff: bez nowych błędów; zastane błędy: {sum(actual.values())}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
