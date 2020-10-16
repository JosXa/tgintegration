from pathlib import Path

from decouple import config


def generate():
    examples_dir = Path(__file__).parent.parent / "examples"

    s = f"""
[pyrogram]
api_id={config("API_ID")}
api_hash={config("API_HASH")}
    """

    with open(examples_dir / "config.ini", "w") as text_file:
        text_file.write(s)


if __name__ == "__main__":
    generate()
