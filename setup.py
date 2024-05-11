import os

cwd = os.path.dirname(os.path.abspath(__file__))

out_path = f"{cwd}/output"

if not os.path.exists(out_path):
    os.mkdir(out_path)