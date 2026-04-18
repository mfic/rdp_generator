# RDP Generator

Generates `.rdp` connection files from a Jinja2 template and a YAML server list.

## How it works

1. Place a YAML file with your server list in the `input/` folder
2. Run `main.py` — it prompts you to select a file and optionally clear the output folder
3. One `.rdp` file per server is written to `output/<filename>/`

## Prerequisites

- Python 3.10+
- Install dependencies: `pipenv install` (or `pip install jinja2 pyyaml`)

## Input file format

Create a `.yml` or `.yaml` file in `input/` with a `servers` list. The fields `name`, `address`, and `username` are required.

```yaml
servers:
  - name: ServerName-ASDF
    address: server1.domain.com
    username: user@domain.com
  - name: ServerName-FDSA
    address: server2.domain.com
    username: user@domain.com
```

A sample file is provided at `input/_sample.yml`.

## Usage

```bash
python main.py
```

You will be prompted to:
1. Select an input file by number
2. Confirm whether to clear the output folder before generating

Generated files are placed in `output/<input-filename>/`.

## Project structure

```
rdp_generator/
├── input/           # Place your YAML server files here
├── output/          # Generated .rdp files (one subfolder per input file)
├── templates/
│   └── template.rdp.j2   # Jinja2 RDP template
└── main.py
```

## Field validation

Field values for `name`, `address`, and `username` are validated against a safe character set (`a-z`, `A-Z`, `0-9`, `-`, `_`, `.`, `@`). Entries with invalid characters are rejected before any files are written.
