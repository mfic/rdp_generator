import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil


def load_yaml(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def generate_rdp_files(template_path: str, servers: list, output_dir: str):
    env = Environment(loader=FileSystemLoader(Path(template_path).parent))
    template = env.get_template(Path(template_path).name)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    for server in servers:
        rdp_content = template.render(
            address=server["address"], username=server["username"]
        )
        file_name = output_dir_path / f"{server['name']}.rdp"
        with open(file_name, "w") as file:
            file.write(rdp_content)
        print(f"RDP file '{file_name}' created successfully")


def list_customer_files(directory: str) -> list:
    customer_dir = Path(directory)
    return list(customer_dir.glob("*.yml")) + list(customer_dir.glob("*.yaml"))


def select_customer_file(customer_files: list) -> str:
    print("Available customer files:")
    for idx, file in enumerate(customer_files):
        print(f"{idx}: {file.name}")

    selected_idx = int(input("Select the customer file by number: "))
    return customer_files[selected_idx]


def clear_output_directory(output_dir: str):
    if Path(output_dir).exists():
        user_input = (
            input(
                f"Do you want to clear the folder '{output_dir}' before generating new sessions? (yes/no): "
            )
            .strip()
            .lower()
        )
        if user_input == "yes":
            shutil.rmtree(output_dir)
            print(f"Cleared the folder '{output_dir}'.")


def main():
    input_dir = "input"
    template_path = "templates/template.rdp.j2"

    customer_files = list_customer_files(input_dir)
    if not customer_files:
        print("No customer files found in the input directory.")
        return

    selected_file = select_customer_file(customer_files)
    config = load_yaml(selected_file)
    servers = config.get("servers", [])

    if not servers:
        print("No servers found in the configuration.")
        return

    output_dir = f"output/{selected_file.stem}"
    clear_output_directory(output_dir)

    generate_rdp_files(template_path, servers, output_dir)


if __name__ == "__main__":
    main()
