from flask import Flask, render_template, request
import requests
import logging
import subprocess

app = Flask(__name__, static_url_path='/static')
logging.basicConfig(level=logging.DEBUG)

API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyBfaJZk-ljrgGrnmOeg4wrQ3raKdhQnF1c"

DEFAULT_TEXT = "Generate Complete code: "

FORMAT_TOOLS = {
    'java': 'clang-format -style=Google',
    'python': 'black -',
    'javascript': 'prettier --parser babel --stdin-filepath code.js',
    'csharp': 'clang-format -style=Google',
    'cpp': 'clang-format -style=Google',
    'php': 'clang-format -style=Google',
    'swift': 'swiftformat -',
    'ruby': 'rufo',
    'typescript': 'prettier --parser typescript --stdin-filepath code.ts',
    'kotlin': 'ktlint',
    'go': 'gofmt',
    'r': 'styler --stdin',
    'matlab': 'matlab-formatter',
    'objc': 'clang-format -style=Google',
    'sql': 'sqlformat',
    'html': 'prettier --parser html --stdin-filepath code.html',
    'perl': 'perltidy',
    'bash': 'shfmt',
    'scala': 'scalafmt',
    'rust': 'rustfmt',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    if search_query:
        response = generate_code(DEFAULT_TEXT + search_query)  
        if response and 'candidates' in response:
            code_content, language = extract_code(response)
            if code_content:
                formatted_code = format_code(code_content, language)
                return render_template('result.html', code_content=formatted_code)
        error_msg = "Failed to generate code. Please try again."
    else:
        error_msg = "Please enter a valid code generation prompt."
    return render_template('index.html', error=error_msg)

def generate_code(prompt):
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        error_msg = f"Failed to generate code. Error: {response.text}"
        logging.error(error_msg)
        return None

def extract_code(response):
    candidates = response.get('candidates', [])
    if candidates:
        candidate = candidates[0]
        content_parts = candidate.get('content', {}).get('parts', [])
        if content_parts:
            code_content = content_parts[0].get('text', '')
            language = candidate.get('metadata', {}).get('language', '')
            return code_content, language
    return None, None

def format_code(code, language):
    if language.lower() in FORMAT_TOOLS:
        formatter_cmd = FORMAT_TOOLS[language.lower()]
        if formatter_cmd:
            formatted_code = subprocess.run(formatter_cmd, input=code.encode(), text=True, capture_output=True)
            if formatted_code.returncode == 0:
                return formatted_code.stdout
            else:
                logging.error(f"Failed to format code: {formatted_code.stderr}")
    return code

if __name__ == '__main__':    
    app.run(debug=True)
