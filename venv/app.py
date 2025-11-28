from flask import Flask, render_template, request, send_file
from datetime import datetime
import re
import io
import zipfile
from collections import defaultdict
import pymupdf as fitz

app = Flask(__name__)

@app.route('/')
def index():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', time=current_time)

@app.route('/about', methods=['GET', 'POST'])
def about_us():  # ← This was missing! That's why error happened
    if request.method == 'GET':
        products = [
            {"sku": "Apple", "price": 10},
            {"sku": "Banana", "price": 20},
            {"sku": "Cherry", "price": 14},
            {"sku": "Pear", "price": 12}
        ]
        return render_template('about.html', products=products)
    if request.method == 'POST':
        cust_email = request.form['cust_email']
        return render_template('thankyou.html', cust_email=cust_email)

@app.route('/classifier', methods=['GET', 'POST'])
def classifier():
    global results_data
    if request.method == 'POST':
        files = request.files.getlist('files')
        categorized = defaultdict(list)

        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                pdf_data = file.read()
                try:
                    doc = fitz.open(stream=pdf_data, filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    category = classify(text)
                    categorized[category].append((file.filename, pdf_data))
                except:
                    categorized["Error"].append((file.filename, pdf_data))

        results_data = categorized
        return render_template('classifier_result.html', results=categorized, total=len(files))

    return render_template('classifier_form.html')

def classify(text):
    text = text.lower()
    if any(x in text for x in ["invoice", "total amount", "nt$", "tax invoice", "bill to"]):
        return "Invoice"
    if any(x in text for x in ["contract", "agreement", "party a", "party b", "signed"]):
        return "Contract"
    if any(x in text for x in ["resume", "cv", "experience", "education", "github", "linkedin"]):
        return "Resume"
    if any(x in text for x in ["quotation", "quote", "unit price", "valid until", "offer"]):
        return "Quotation"
    return "Other"

# Store results temporarily
results_data = {}

@app.route('/download/<category>')
def download(category):
    if category not in results_data:
        return "Not found", 404
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        for name, data in results_data[category]:
            zf.writestr(name, data)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"{category}s.zip", mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)