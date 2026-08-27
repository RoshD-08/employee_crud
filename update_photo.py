import re

with open('app.py', 'r') as f:
    content = f.read()

# Add imports
content = content.replace(
    "import psycopg2\nimport psycopg2.extras",
    "import os\nimport uuid\nimport psycopg2\nimport psycopg2.extras\nfrom werkzeug.utils import secure_filename"
)

# Add MAX_CONTENT_LENGTH and UPLOAD_FOLDER
content = content.replace(
    "app.config.from_object(Config)",
    "app.config.from_object(Config)\napp.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024\napp.config['UPLOAD_FOLDER'] = 'static/uploads/photos'"
)

# Add photo to _INSERT_COLS
content = content.replace(
    '"address", "latitude", "longitude",\n]',
    '"address", "latitude", "longitude",\n    "photo",\n]'
)

# Add helper for uploading photos
photo_helper = """
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def handle_photo_upload(file):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        return unique_filename
    return None
"""

content = content.replace(
    "# ═══════════════════════════════════════════\n# EMPLOYEE CRUD ROUTES",
    photo_helper + "\n# ═══════════════════════════════════════════\n# EMPLOYEE CRUD ROUTES"
)

with open('app.py', 'w') as f:
    f.write(content)
