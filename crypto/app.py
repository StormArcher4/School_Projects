from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Enable CORS for frontend access
from colorama import init
from html import unescape
import re

app = Flask(__name__, template_folder="templates", static_folder="static")  # Set folders for templates and static files
CORS(app)  # Enable CORS

init()  # Initialize colorama

# Add cache control to prevent caching issues
@app.after_request
def add_header(response):
    """Add headers to prevent caching."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Serve the HTML page for homepage
@app.route('/')
def home():
    return render_template('homepage.html')  # Load homepage.html from the templates folder

# Serve the WhisperDots page
@app.route('/whisperdots')
def whisperdots():
    return render_template('WhisperDots.html')  # Load WhisperDots.html from the templates folder

@app.route('/Decodage')
def Decodage():
    return render_template('Decodage.html')  # Make sure this file exists in your templates folder


# Define letters-to-points mapping
alphabet_points = {
    'A': [[1, 1, 0], [0, 4, 1], [0, 1, 1]],
    'B': [[0, 3, 0], [3, 2, 3], [3, 1, 0]],
    'C': [[0, 3, 0], [5, 4, 0], [3, 3, 3]],
    'D': [[0, 0, 3], [3, 3, 3], [1, 0, 3]],
    'E': [[1, 5, 0], [0, 3, 0], [1, 1, 1]],
    'F': [[1, 1, 1], [1, 2, 3], [0, 0, 3]],
    'H': [[1, 4, 1], [3, 3, 1], [3, 0, 0]],
    'I': [[0, 3, 0], [1, 3, 0], [1, 2, 1]],
    'L': [[1, 1, 1], [0, 6, 1], [0, 3, 3]],
    'M': [[1, 1, 1], [3, 1, 3], [2, 3, 0]],
    'N': [[1, 4, 1], [1, 3, 0], [0, 3, 3]],
    'O': [[3, 3, 3], [0, 1, 1], [0, 4, 0]],
    'P': [[1, 1, 1], [3, 0, 1], [3, 3, 3]],
    'R': [[1, 2, 1], [1, 1, 3], [3, 0, 3]],
    'S': [[0, 2, 0], [1, 1, 1], [0, 3, 3]],
    'T': [[1, 4, 1], [0, 3, 1], [3, 3, 0]],
    'U': [[3, 1, 1], [5, 1, 1], [1, 0, 3]],
    'V': [[3, 1, 0], [6, 3, 3], [3, 1, 0]],
    'W': [[1, 1, 0], [1, 3, 3], [1, 1, 0]],
    'Y': [[0, 3, 0], [1, 1, 1], [0, 4, 0]],
    'G': [[1, 2, 1], [2, 3, 1], [1, 1, 2]],
    'J': [[1, 2, 1], [2, 3, 1], [1, 2, 2]],
    'K': [[1, 2, 1], [2, 3, 1], [1, 2, 2]],
    'Q': [[1, 2, 1], [2, 2, 2], [1, 2, 1]],
    'X': [[2, 2, 1], [2, 2, 2], [1, 2, 1]],
    'Z': [[2, 2, 1], [2, 1, 2], [1, 3, 1]]
}

def process_text(text):
    """
    Convert input text into HTML dot‑matrix blocks.
    Each input line becomes three output rows, each followed by a <br>.
    """
    html_out = []  # we'll collect each output row here

    # Split on real newlines, keep empty lines if present
    lines = text.upper().split("\n")

    for line in lines:
        # Prepare three new rows for this single input line
        row0, row1, row2 = "", "", ""

        for ch in line:
            if ch == " ":
                # four non‑breaking spaces between words
                row0 += "&nbsp;&nbsp;&nbsp;&nbsp;"
                row1 += "&nbsp;&nbsp;&nbsp;&nbsp;"
                row2 += "&nbsp;&nbsp;&nbsp;&nbsp;"
            elif ch in alphabet_points:
                matrix = alphabet_points[ch]
                # for each of the 3 sub‑rows of the matrix
                for r, row in enumerate((row0, row1, row2)):
                    cells = []
                    for x in matrix[r]:
                        if   x == 0:
                            cells.append("&nbsp;")
                        elif x == 1:
                            cells.append('<span style="color:white;">●</span>')
                        elif x == 2:
                            cells.append('<span style="color:blue;">●</span>')
                        elif x == 3:
                            cells.append('<span style="color:black;">●</span>')
                        elif x == 4:
                            cells.append('<span style="color:gray;">●</span>')
                        elif x == 5:
                            cells.append('<span style="color:green;">●</span>')
                        elif x == 6:
                            cells.append('<span style="color:red;">●</span>')
                    # join the dots for this row, then pad three non‑breaking spaces
                    block = "&nbsp;".join(cells) + "&nbsp;&nbsp;&nbsp;"
                    if r == 0:
                        row0 += block
                    elif r == 1:
                        row1 += block
                    else:
                        row2 += block

        # Once this line is done, push its three rows into our output list
        html_out.append(row0)
        html_out.append(row1)
        html_out.append(row2)

    # Finally, join everything with <br> so each row prints on its own line
    return "".join(row + "<br>" for row in html_out)

@app.route('/decode', methods=['POST'])
def decode_text():
    data = request.json
    html = data.get("html", "")
    result = decode_dot_html(html)
    return jsonify({"text": result})


def decode_dot_html(html):
    # Mapping from span color to number
    color_map = {
        'white': 1,
        'blue': 2,
        'black': 3,
        'gray': 4,
        'green': 5,
        'red': 6
    }

    # Clean the HTML
    html = unescape(html)

    # Split rows
    rows = html.strip().split("<br>")
    matrix_rows = []

    for row in rows:
        row = row.strip()
        cells = []

        # Find all spans or &nbsp;
        tokens = re.findall(r'style="color:(.*?)">●</span>|&nbsp;', row)

        for token in tokens:
            if token == '':
                cells.append(0)
            elif token in color_map:
                cells.append(color_map[token])
            else:
                cells.append(0)

        matrix_rows.append(cells)

    # Group into characters — each character is 3 columns wide plus 3 &nbsp; in between
    text = ""
    if len(matrix_rows) < 3:
        return ""

    row0, row1, row2 = matrix_rows[0], matrix_rows[1], matrix_rows[2]
    width = len(row0)
    i = 0
    while i + 2 < width:
        block = [
            row0[i:i+3],
            row1[i:i+3],
            row2[i:i+3]
        ]
        # Compare to all known letters
        matched = "?"
        for letter, pattern in alphabet_points.items():
            if pattern == block:
                matched = letter
                break
        text += matched
        i += 4  # Skip the 3 dots + 1 spacer

    return text

# ---- NEW: encode-to-code and decode-from-code ----
def encode_text_to_code(text):
    text = text.upper()
    encoded = []
    lines = text.split('\n')
    for ch in text:
        if ch == ' ':
            encoded.append('___')
        elif ch in alphabet_points:
            flat = sum(alphabet_points[ch], [])
            encoded.append(''.join(str(num) for num in flat))
        else:
            encoded.append('???')
    return '-'.join(encoded)

@app.route('/encode-to-code', methods=['POST'])
def encode_to_code():
    data = request.json
    text = data.get('text', '')
    code = encode_text_to_code(text)
    return jsonify({'code': code})


def decode_code_to_text(code):
    rev_map = { ''.join(str(num) for row in matrix for num in row): letter
                for letter, matrix in alphabet_points.items() }
    result = []
    for part in code.split('-'):
        if part == '___': result.append(' ')
        elif part in rev_map: result.append(rev_map[part])
        else: result.append('?')
    return ''.join(result)

@app.route('/decode-from-code', methods=['POST'])
def decode_from_code():
    data = request.json
    code = data.get('code', '')
    print(f"Received code to decode: {code}")  # Debug output
    text = decode_code_to_text(code)
    print(f"Decoded text: {text}")  # Debug output
    return jsonify({'text': text})


# Flask route to process input text
@app.route('/analyze', methods=['POST'])
def analyze_text():
    data = request.json  # Get JSON data from frontend
    text = data.get("text", "")  # Extract text from request
    
    # Check if this is a code format (from decodage page)
    if '-' in text and all(c in '0123456789-_?' for c in text):
        # This appears to be a code - convert it to dots
        parts = text.split('-')
        dots_html = []
        
        # Process each line for the three rows
        row0, row1, row2 = [], [], []
        
        for part in parts:
            if part == '___':  # Space
                row0.append("&nbsp;&nbsp;&nbsp;&nbsp;")
                row1.append("&nbsp;&nbsp;&nbsp;&nbsp;")
                row2.append("&nbsp;&nbsp;&nbsp;&nbsp;")
            elif len(part) == 9:  # Valid letter code
                # Convert the flat array back to 3x3 matrix
                matrix = [
                    [int(part[0]), int(part[1]), int(part[2])],
                    [int(part[3]), int(part[4]), int(part[5])],
                    [int(part[6]), int(part[7]), int(part[8])]
                ]
                
                # Generate HTML for each row
                for r in range(3):
                    cells = []
                    for x in matrix[r]:
                        if x == 0:
                            cells.append("&nbsp;")
                        elif x == 1:
                            cells.append('<span style="color:white;">●</span>')
                        elif x == 2:
                            cells.append('<span style="color:blue;">●</span>')
                        elif x == 3:
                            cells.append('<span style="color:black;">●</span>')
                        elif x == 4:
                            cells.append('<span style="color:gray;">●</span>')
                        elif x == 5:
                            cells.append('<span style="color:green;">●</span>')
                        elif x == 6:
                            cells.append('<span style="color:red;">●</span>')
                    
                    block = "&nbsp;".join(cells) + "&nbsp;&nbsp;&nbsp;"
                    if r == 0:
                        row0.append(block)
                    elif r == 1:
                        row1.append(block)
                    else:
                        row2.append(block)
        
        # Combine all rows
        dots_html.append("".join(row0))
        dots_html.append("".join(row1))
        dots_html.append("".join(row2))
        
        result = "".join(row + "<br>" for row in dots_html)
        return jsonify({"output": result})
    else:
        # Regular text processing
        result = process_text(text)
        return jsonify({"output": result})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)