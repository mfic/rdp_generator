import re
import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
TEMPLATE_PATH = BASE_DIR / "templates" / "template.rdp.j2"

REQUIRED_FIELDS = {"name", "address", "username"}
_SAFE_FIELD = re.compile(r"^[\w\-\.@]+$")


def load_yaml(file_path: Path) -> dict | None:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise SystemExit(f"Error: Failed to parse YAML file '{file_path}': {e}")
    except OSError as e:
        raise SystemExit(f"Error: Cannot read file '{file_path}': {e}")


def validate_servers(servers: list):
    for i, server in enumerate(servers):
        missing = REQUIRED_FIELDS - server.keys()
        if missing:
            raise SystemExit(f"Error: Server entry #{i} is missing required fields: {missing}")
        for field in REQUIRED_FIELDS:
            value = str(server[field])
            if not _SAFE_FIELD.match(value):
                raise SystemExit(f"Error: Invalid characters in server field '{field}' on entry #{i}: {value!r}")


def generate_rdp_files(servers: list, output_dir: Path):
    if not TEMPLATE_PATH.exists():
        raise SystemExit(f"Error: Template file not found: '{TEMPLATE_PATH}'")

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH.parent))
    template = env.get_template(TEMPLATE_PATH.name)
    output_dir.mkdir(parents=True, exist_ok=True)

    for server in servers:
        rdp_content = template.render(address=server["address"], username=server["username"])
        file_name = output_dir / f"{server['name']}.rdp"
        with open(file_name, "w") as file:
            file.write(rdp_content)
        print(f"RDP file '{file_name}' created successfully")

    print(f"\nDone. {len(servers)} RDP file(s) generated in '{output_dir}'.")


def list_customer_files() -> list:
    return list(INPUT_DIR.glob("*.yml")) + list(INPUT_DIR.glob("*.yaml"))


def select_customer_file(customer_files: list) -> Path:
    print("Available customer files:")
    for idx, file in enumerate(customer_files):
        print(f"  {idx}: {file.name}")

    while True:
        raw = input("Select the customer file by number: ").strip()
        if raw.isdigit():
            idx = int(raw)
            if 0 <= idx < len(customer_files):
                return customer_files[idx]
        print(f"Please enter a number between 0 and {len(customer_files) - 1}.")


def clear_output_directory(output_dir: Path):
    if output_dir.exists():
        user_input = (
            input(f"Do you want to clear the folder '{output_dir}' before generating new sessions? (yes/no): ")
            .strip()
            .lower()
        )
        if user_input in ("yes", "y"):
            shutil.rmtree(output_dir)
            print(f"Cleared the folder '{output_dir}'.")


def main():
    customer_files = list_customer_files()
    if not customer_files:
        print("No customer files found in the input directory.")
        return

    selected_file = select_customer_file(customer_files)
    config = load_yaml(selected_file)

    if config is None:
        raise SystemExit("Error: The selected file is empty.")

    servers = config.get("servers", [])
    if not servers:
        print("No servers found in the configuration.")
        return

    validate_servers(servers)

    output_dir = BASE_DIR / "output" / selected_file.stem
    clear_output_directory(output_dir)
    generate_rdp_files(servers, output_dir)


if __name__ == "__main__":
    main()
