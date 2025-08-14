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
        list = parse_numbers(list_str)
        n = int(n_str)
        if n <= 0:
            raise ValueError
    except ValueError:
        abort(400, "Invalid input. Use integers only and n > 0.")
    
    max_val = 0
    for num in list:
        if num > max_val:
            max_val = num

    min_val = list[0]
    for num in list:
        if num < min_val:
            min_val = num
    
    amplitude = max_val - min_val
    while amplitude % n != 0:
        amplitude += 1
    
    range_val = amplitude/n
    j = 0
    classes = []

    while j < n:
        count = 0
        numbers = (0, 0)
        for num in list:
            if num >= (min_val + j * range_val) and num < (min_val + (j + 1) * range_val):
                count += 1
                numbers = (min_val + j * range_val, min_val + (j + 1) * range_val)
        if j == n - 1:
            for num in list:
                if num == (min_val + (j + 1) * range_val):
                    count += 1
                    numbers = (min_val + j * range_val, min_val + (j + 1) * range_val)

        classes.append((numbers, count))
        j += 1
    i = 0
    ExcelList = []
    for group, count in classes:
        i += 1
        if(i < n):
            ExcelList.append(f"[{group[0]}, {group[1]}[ {(count/len(list)*100)}%")
        else:
            ExcelList.append(f"[{group[0]}, {group[1]}] {(count/len(list)*100)}%")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    for line in ExcelList:
        ws.append(line)

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename = f"numbers_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.xlsx"
    return send_file(
        bio,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if __name__ == "__main__":
     app.run(debug=True)
