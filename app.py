from flask import Flask, render_template, request, send_file, url_for, redirect
import pandas as pd
import io
import fitz  # PyMuPDF
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET', 'POST'])
def about_us():
    if request.method == 'GET':
        products = [
            {"sku":"Apple", "price":10},
            {"sku":"Banana", "price":20},
            {"sku":"Cherry", "price":14},
            {"sku":"Pear", "price":12}
        ]
        return render_template('about.html', products=products)
    if request.method == 'POST':
        cust_email = request.form['cust_email']
        return render_template('thankyou.html', cust_email=cust_email)

@app.route('/calculate_csv', methods=['GET', 'POST'])
def calculate_csv():
    if request.method == 'POST':
        if 'files' not in request.files:
            return "No file"

        files = request.files.getlist('files')

        dataframes = []
        for f in files:
            df = pd.read_csv(f)

            df['total'] = df['qty'] * df['cost']
            dataframes.append(df)

        #Combine dataframe to single one
        combined_df = pd.concat(dataframes, ignore_index=True)

        table_html = combined_df.to_html(classes='table', index=False)

        return render_template("csv_result.html", table=table_html)

    return render_template('calculate_csv.html')


@app.route('/pdf_filter', methods=['GET', 'POST'])
def pdf_filter():
    """Upload a PDF and a keyword. Return a PDF containing only pages where
    the page text contains the keyword (case-insensitive). If no pages match,
    render a result template with a friendly message.
    """
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return render_template('pdf_result.html', message='No file part in request')

        pdf_file = request.files['pdf_file']
        keyword = request.form.get('keyword', '').strip()

        if pdf_file.filename == '':
            return render_template('pdf_result.html', message='No selected file')

        if keyword == '':
            return render_template('pdf_result.html', message='Please provide a keyword to filter')

        if fitz is None:
            return render_template('pdf_result.html', message='PDF support is not available on the server. Install pymupdf.')

        try:
            # read uploaded file bytes
            pdf_bytes = pdf_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
        except Exception as e:
            return render_template('pdf_result.html', message=f'Failed to read PDF: {e}')

        out_doc = fitz.open()
        matched_pages = 0

        # iterate pages and test for keyword (case-insensitive)
        for page_num in range(doc.page_count):
            try:
                page = doc.load_page(page_num)
                text = page.get_text('text') or ''
            except Exception:
                text = ''

            if keyword.lower() in text.lower():
                # insert this single page into output
                out_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                matched_pages += 1

        if matched_pages == 0:
            doc.close()
            out_doc.close()
            return render_template('pdf_result.html', message=f'No pages matched the keyword "{keyword}".')

        try:
            out_bytes = out_doc.write()
            out_io = io.BytesIO(out_bytes)
            out_io.seek(0)
        finally:
            doc.close()
            out_doc.close()

        download_name = f'filtered_{keyword}.pdf'
        return send_file(out_io, mimetype='application/pdf', as_attachment=True, download_name=download_name)

    # GET
    return render_template('pdf_filter.html')

if __name__ == '__main__':
    app.run(debug=True)
