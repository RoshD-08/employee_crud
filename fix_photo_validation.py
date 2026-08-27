import re

with open('app.py', 'r') as f:
    content = f.read()

# Replace block in add_employee
add_orig = """                    if allowed_file(file.filename):
                        photo_filename = handle_photo_upload(file)
                    else:
                        errors.append("Invalid photo format. Only JPG, JPEG, and PNG are allowed.")"""

add_new = """                    if allowed_file(file.filename):
                        from PIL import Image
                        try:
                            img = Image.open(file)
                            width, height = img.size
                            file.seek(0)
                            if width != height:
                                errors.append(f"Image must be square (current: {width}x{height}px).")
                            elif width < 200 or width > 400:
                                errors.append(f"Image dimensions must be between 200x200 and 400x400 pixels (current: {width}x{height}px).")
                            else:
                                photo_filename = handle_photo_upload(file)
                        except Exception:
                            file.seek(0)
                            errors.append("Invalid image file.")
                    else:
                        errors.append("Invalid photo format. Only JPG, JPEG, and PNG are allowed.")"""

content = content.replace(add_orig, add_new)

# Replace block in edit_employee
edit_orig = """                    if allowed_file(file.filename):
                        new_photo = handle_photo_upload(file)
                        if new_photo:
                            photo_filename = new_photo
                    else:
                        errors.append("Invalid photo format. Only JPG, JPEG, and PNG are allowed.")"""

edit_new = """                    if allowed_file(file.filename):
                        from PIL import Image
                        try:
                            img = Image.open(file)
                            width, height = img.size
                            file.seek(0)
                            if width != height:
                                errors.append(f"Image must be square (current: {width}x{height}px).")
                            elif width < 200 or width > 400:
                                errors.append(f"Image dimensions must be between 200x200 and 400x400 pixels (current: {width}x{height}px).")
                            else:
                                new_photo = handle_photo_upload(file)
                                if new_photo:
                                    photo_filename = new_photo
                        except Exception:
                            file.seek(0)
                            errors.append("Invalid image file.")
                    else:
                        errors.append("Invalid photo format. Only JPG, JPEG, and PNG are allowed.")"""

content = content.replace(edit_orig, edit_new)

with open('app.py', 'w') as f:
    f.write(content)

