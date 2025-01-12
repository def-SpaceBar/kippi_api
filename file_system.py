import os
from flask import Blueprint, jsonify, request, send_file
import magic as magic

BASE_FOLDER_YOUTUBE_AUTOMATIONS_PATH = r"C:\auto_youtube\\"
file_system_bp = Blueprint('file_system_bp', __name__)


@file_system_bp.route('/get_file', methods=['POST'])
def get_file():
    data = request.json
    file_name = data.get('file_name')
    category = data.get('category')
    parent_video_id = data.get('video_id')
    clip_id = data.get('clip_id')

    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    # Resolve absolute path for security
    absolute_path = os.path.join(BASE_FOLDER_YOUTUBE_AUTOMATIONS_PATH, category, parent_video_id, clip_id, file_name)

    # Check if the file exists
    if not os.path.isfile(absolute_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # Use `magic` to detect the MIME type based on file content
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(absolute_path)

        # Return the file with the detected MIME type
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=os.path.basename(absolute_path),
            mimetype=mime_type
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
