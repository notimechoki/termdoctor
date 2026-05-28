from pathlib import Path

Path("demo_file.txt").write_text("hello", encoding="utf-8")

with open("demo_file.txt/data.txt", "r", encoding="utf-8") as file:
    print(file.read())