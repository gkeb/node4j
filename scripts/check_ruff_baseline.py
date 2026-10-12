import json
import subprocess
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


def _ruff_diagnostics(root: Path) -> list[dict]:
    # Ruff uruchamiany bezpośrednio, żeby wynik nie przechodził przez
    # przekierowanie powłoki (PowerShell zapisuje je jako UTF-16).
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", ".", "--output-format=json"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode > 1:
        print(result.stdout, result.stderr, sep="\n")
        raise SystemExit(result.returncode)
    return json.loads(result.stdout)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / ".ai" / "warsztat.json").read_text(encoding="utf-8"))
    baseline = _known_errors(config["odniesienie"]["znane"])
    if len(sys.argv) > 1:
        diagnostics = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    else:
        diagnostics = _ruff_diagnostics(root)
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

    # Liczniki muszą maleć razem z błędami — inaczej przepuszczą nowe.
    stale = {
        key: (count, actual.get(key, 0))
        for key, count in baseline.items()
        if actual.get(key, 0) < count
    }
    if stale:
        print("Punkt odniesienia jest nieaktualny — zmień w warsztat.json:")
        for (code, filename), (known, current) in sorted(stale.items()):
            change = f"x{current}" if current else "usuń wpis"
            print(f"  ruff {code} {filename} x{known} -> {change}")
        return 1

    print(f"Ruff: bez nowych błędów; zastane błędy: {sum(actual.values())}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
