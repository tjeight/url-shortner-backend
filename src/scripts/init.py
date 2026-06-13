from pathlib import Path


def create_init_files(root_dir: str = "src") -> None:
    root = Path(root_dir)

    for directory in root.rglob("*"):
        if not directory.is_dir():
            continue

        # Skip __pycache__ directories
        if "__pycache__" in directory.parts:
            continue

        init_file = directory / "__init__.py"

        if not init_file.exists():
            init_file.touch()
            print(f"Created: {init_file}")


if __name__ == "__main__":
    create_init_files()
