# PDF Filter Web

This small Flask app uses PyMuPDF (imported as `fitz`) to filter PDF pages by keyword and export results. If you see an error like:

    module 'fitz' has no attribute 'open'

that usually means there's a conflicting package named `fitz` installed in your Python environment (different from PyMuPDF). To fix it, use the following steps in the environment where you run the app:

```powershell
pip uninstall fitz -y
pip install PyMuPDF
```

If you run the app in a virtual environment, make sure you activate it before installing packages.

Once installed, run the app with:

```powershell
python app.py
```

Then open http://127.0.0.1:5000 in your browser and use the PDF filter page.
