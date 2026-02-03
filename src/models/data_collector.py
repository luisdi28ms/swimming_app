import pandas as pd

def process_upload(file):
    """Handles different file types and returns head/tail HTML."""
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        # Requires 'openpyxl' installed for .xlsx
        df = pd.read_excel(file)
    
    return {
        "head": df.head().to_html(classes='table table-striped'),
        "tail": df.tail().to_html(classes='table table-striped')
    }
