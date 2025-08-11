# ADGM Corporate Agent — Document Reviewer

A Streamlit-based web app for reviewing `.docx` documents by analyzing their content using custom analysis logic.

## Features

- Upload multiple `.docx` files at once.
- Analyze documents automatically with the `analyze_docx_file` function.
- View results interactively in the web interface.
- Simple and user-friendly UI built with Streamlit.

## Installation

# 1. Clone the repository:


   git clone https://github.com/yourusername/adgm-corporate-agent.git
   cd adgm-corporate-agent

# 2. Create and activate a virtual environment (optional but recommended):

    Copy
    Edit
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies:

   
    Copy
    Edit
    pip install -r requirements.txt

    # Usage
    Run the Streamlit app:

    Copy
    Edit
    streamlit run app.py
# 4. Use the file uploader to select one or more .docx files.

Click the Analyze button to start document analysis.

Results will be displayed below or in a separate section.

# 5. File Structure
app.py — Main Streamlit application.

reviewer.py — Contains the analyze_docx_file function to process documents.

uploads/ — Folder where uploaded files are saved temporarily.

# 6. Dependencies
Streamlit

python-docx (if used inside reviewer.py)

Other dependencies based on your analysis code

# 7. Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

# 8. License
Specify your license here (e.g., MIT, Apache 2.0, etc.)