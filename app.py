from flask import Flask, request, render_template, send_file
import os
from generate_vina_grid import parse_pocket_pdb, write_vina_config

app = Flask(__name__, static_url_path='/static')

# Define directories
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    chart_data = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file uploaded'
        else:
            file = request.files['file']
            if file.filename == '':
                error = 'No file selected'
            elif not file.filename.endswith('.pdb'):
                error = 'Please upload a .pdb file'
            else:
                # Save uploaded file
                pocket_file = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(pocket_file)
                try:
                    # Process file
                    center, size = parse_pocket_pdb(pocket_file)
                    output_file = os.path.join(app.config['OUTPUT_FOLDER'], 'config.txt')
                    write_vina_config(center, size, output_file)

                    # Prepare result for display
                    result = {
                        'center_x': f"{center[0]:.3f}",
                        'center_y': f"{center[1]:.3f}",
                        'center_z': f"{center[2]:.3f}",
                        'size_x': f"{size[0]:.1f}",
                        'size_y': f"{size[1]:.1f}",
                        'size_z': f"{size[2]:.1f}"
                    }

                    # Prepare chart data
                    chart_data = {
                        'labels': ['Size X', 'Size Y', 'Size Z'],
                        'data': [size[0], size[1], size[2]],
                        'colors': ['#007bff', '#28a745', '#dc3545']
                    }

                    return render_template('index.html', result=result, chart_data=chart_data, error=None, download=True)
                except Exception as e:
                    error = str(e)

    return render_template('index.html', result=result, chart_data=chart_data, error=error, download=False)

@app.route('/download')
def download_file():
    output_file = os.path.join(app.config['OUTPUT_FOLDER'], 'config.txt')
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    # For local development only
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
