from pathlib import Path

Path("demo_folder").mkdir(exist_ok=True)

with open("demo_folder", "r", encoding="utf-8") as file:
    print(file.read())