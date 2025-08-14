from flask import Flask, render_template, request, send_file, abort
from io import BytesIO
from openpyxl import Workbook
import re
from datetime import datetime

app = Flask(__name__)

def parse_numbers(s: str):
    tokens = re.split(r"[,\s;]+", s.strip())
    nums = []
    for t in tokens:
        if t == "":
            continue
        nums.append(int(t))
    return nums

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    list_str = request.form.get("numbers", "").strip()
    n_str = request.form.get("n", "").strip()

    if not list_str or not n_str:
        abort(400, "Please provide both the list of numbers and n.")

    try:
        numbers_list = parse_numbers(list_str)
        n = int(n_str)
        if n <= 0:
            raise ValueError
    except ValueError:
        abort(400, "Invalid input. Use integers only and n > 0.")
    
    max_val = max(numbers_list)
    min_val = min(numbers_list)
    
    amplitude = max_val - min_val
    while amplitude % n != 0:
        amplitude += 1
    
    range_val = amplitude/n
    classes = []

    for j in range(n):
        count = 0
        lower = min_val + j * range_val
        upper = min_val + (j + 1) * range_val
        
        for num in numbers_list:
            if (num >= lower and num < upper) or (j == n-1 and num == upper):
                count += 1
        
        classes.append(((lower, upper), count))

    wb = Workbook()
    ws = wb.active
    ws.title = "Histogram"
    
    
    for (lower, upper), count in classes:
        class_range = f"[{lower}, {upper}]" if j == n-1 else f"[{lower}, {upper}["
        percentage = f"{(count/len(numbers_list)*100):.2f}%"
        ws.append([class_range, count, percentage])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename = f"histogram_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.xlsx"
    return send_file(
        bio,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
if __name__ == "__main__":
     app.run(debug=True)
