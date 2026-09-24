# Helper for the report only (not part of the analysis).
# Runs each cell of telco_churn_analysis.py and saves:
#   images/<ID>_code.png, images/<ID>_output.png, images/<ID>_chart.png
import contextlib
import io
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer, TextLexer

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("images", exist_ok=True)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def render(text, lexer, path, numbers):
    fmt = ImageFormatter(font_name=MONO, font_size=15, style="friendly" if numbers else "default",
                         line_numbers=numbers, line_pad=3, image_pad=14,
                         line_number_bg="#EEF1F5", line_number_fg="#8A94A6")
    with open(path, "wb") as f:
        f.write(highlight(text, lexer, fmt))


src = open("telco_churn_analysis.py").read()
parts = re.split(r"^# %% \[(\w+)\] (.*)$", src, flags=re.M)
ns = {}
manifest = []
for i in range(1, len(parts), 3):
    cid, title, code = parts[i], parts[i + 1].strip(), parts[i + 2].strip("\n")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, ns)
    item = {"id": cid, "title": title, "code": f"images/{cid}_code.png"}
    render(code, PythonLexer(), item["code"], True)
    out = buf.getvalue().rstrip()
    if out:
        item["output"] = f"images/{cid}_output.png"
        render(out, TextLexer(), item["output"], False)
    if plt.get_fignums():
        item["chart"] = f"images/{cid}_chart.png"
        plt.gcf().savefig(item["chart"], dpi=150)
        plt.close("all")
    manifest.append(item)
    print("done", cid)

json.dump(manifest, open("images/manifest.json", "w"), indent=1)
