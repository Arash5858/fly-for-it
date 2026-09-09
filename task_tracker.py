FluxSentinel/
├── fluxsentinel.py
├── README.md
├── requirements.txt
└── .gitignore
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime


class FluxSentinel:
    def __init__(self, target: str, database: str = ".fluxsentinel.json"):
        self.target = Path(target).resolve()
        self.database = Path(database)

    def calculate_hash(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:
            while chunk := file.read(1024 * 1024):
                sha256.update(chunk)

        return sha256.hexdigest()

    def collect_files(self) -> dict:
        if not self.target.exists():
            raise FileNotFoundError(f"Target does not exist: {self.target}")

        files = {}

        if self.target.is_file():
            files[str(self.target)] = self.calculate_hash(self.target)
            return files

        for file_path in self.target.rglob("*"):
            if file_path.is_file() and self.database.resolve() != file_path.resolve():
                try:
                    files[str(file_path)] = self.calculate_hash(file_path)
                except (PermissionError, OSError):
                    continue

        return files

    def save_snapshot(self, files: dict):
        data = {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "target": str(self.target),
            "files": files
        }

        self.database.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )

    def load_snapshot(self) -> dict:
        if not self.database.exists():
            return {}

        try:
            data = json.loads(self.database.read_text(encoding="utf-8"))
            return data.get("files", {})
        except json.JSONDecodeError:
            return {}

    def scan(self):
        previous = self.load_snapshot()
        current = self.collect_files()

        if not previous:
            self.save_snapshot(current)

            print("Initial snapshot created.")
            print(f"Files tracked: {len(current)}")
            return

        previous_paths = set(previous)
        current_paths = set(current)

        added = current_paths - previous_paths
        removed = previous_paths - current_paths

        modified = {
            path
            for path in current_paths & previous_paths
            if current[path] != previous[path]
        }

        print("\nFluxSentinel Report")
        print("=" * 40)

        print(f"Added:    {len(added)}")
        print(f"Modified: {len(modified)}")
        print(f"Removed:  {len(removed)}")

        if added:
            print("\n[+] Added files")
            for path in sorted(added):
                print(f"  {path}")

        if modified:
            print("\n[*] Modified files")
            for path in sorted(modified):
                print(f"  {path}")

        if removed:
            print("\n[-] Removed files")
            for path in sorted(removed):
                print(f"  {path}")

        if not added and not modified and not removed:
            print("\nNo changes detected.")

        self.save_snapshot(current)


def main():
    parser = argparse.ArgumentParser(
        description="FluxSentinel - Lightweight file integrity monitoring."
    )

    parser.add_argument(
        "path",
        help="File or directory to monitor"
    )

    parser.add_argument(
        "--database",
        default=".fluxsentinel.json",
        help="Snapshot database path"
    )

    args = parser.parse_args()

    try:
        sentinel = FluxSentinel(
            target=args.path,
            database=args.database
        )

        sentinel.scan()

    except FileNotFoundError as error:
        print(f"Error: {error}")
    except PermissionError:
        print("Error: Permission denied.")
    except OSError as error:
        print(f"System error: {error}")


if __name__ == "__main__":
    main()
    
