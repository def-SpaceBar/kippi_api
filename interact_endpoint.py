import tkinter as tk
import threading
import webbrowser
from flask import Flask, jsonify, request, Blueprint
import uuid
import requests
import json

opus_tk_n8n_controller = "http://localhost:5678/webhook/controller_opus_tk"
global_clip_id = None
ACTIVE_TK_INSTANCES = {}
interact_bp = Blueprint('interact_bp', __name__)


def opus_interact(video_id, instance_id, description, selenium_instance_id, category, clip_id=None):
    global global_clip_id
    global opus_tk_n8n_controller
    # Initialize the global clip_id
    global_clip_id = clip_id if clip_id else "N/A"

    def log_request(url, payload):
        print(f"POST to {url} with {payload}")

    def button_action(label):
        if label == 'Download' and global_clip_id == "N/A":
            return print('error, clip_id is None.')
        else:
            payload = {
                "video_id": video_id,
                "selenium_instance_id": selenium_instance_id,
                "action": label,
                "description": description,
                "clip_id": global_clip_id,
                "category": category
            }
            headers = {"Content-Type": "application/json"}
            execute_button_action = requests.post("http://localhost:5678/webhook/controller_opus_tk", json=payload, headers=headers)
            return lambda: log_request(opus_tk_n8n_controller, payload)

    def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

    def open_video_link(link):
        webbrowser.open(link)

    root = tk.Tk()
    root.title("Interaction Form")
    root.geometry("800x600")
    root.configure(bg="#f5f5f5")

    canvas = tk.Canvas(root, width=800, height=600, bg="#f5f5f5", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_rounded_rectangle(50, 50, 750, 550, radius=20, fill="white", outline="#d1d1d1", width=2)

    title_label = tk.Label(
        root,
        text="Interaction Form",
        font=("Arial", 20, "bold"),
        bg="white",
        fg="#333333",
    )
    title_label.place(relx=0.5, rely=0.1, anchor="center")

    details_frame = tk.Frame(root, bg="white")
    details_frame.place(relx=0.5, rely=0.4, anchor="center", width=700, height=200)

    # Variables to hold dynamic Clip ID and related widgets
    clip_id_var = tk.StringVar(value=clip_id if clip_id else "N/A")
    opus_link_var = tk.StringVar(value=f'https://clip.opus.pro/clip/{clip_id}' if clip_id else "N/A")

    def create_labeled_row(parent, label_text, value_var, y_offset, clickable=False, link_var=None):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#555555",
        )
        label.place(relx=0.05, y=y_offset, anchor="w")

        value_label = tk.Label(
            parent,
            textvariable=value_var,
            font=("Arial", 14, "underline" if clickable else "normal"),
            bg="white",
            fg="#007aff" if clickable else "#333333",
            cursor="hand2" if clickable else "",
        )
        if clickable and link_var:
            value_label.bind("<Button-1>", lambda e: open_video_link(link_var.get()))
        value_label.place(relx=0.35, y=y_offset, anchor="w")

        return value_label

    create_labeled_row(details_frame, "Video ID:", tk.StringVar(value=video_id), 20)
    create_labeled_row(details_frame, "Clip ID:", clip_id_var, 60)
    create_labeled_row(details_frame, "Opus Clipping Link:", opus_link_var, 100, clickable=True, link_var=opus_link_var)
    create_labeled_row(details_frame, "Video Link:", tk.StringVar(value=f'https://youtube.com/watch?v={video_id}'), 140,
                       clickable=True, link_var=tk.StringVar(value=f'https://youtube.com/watch?v={video_id}'))
    create_labeled_row(details_frame, "Instance ID:", tk.StringVar(value=selenium_instance_id), 180)
    create_labeled_row(details_frame, "Description:", tk.StringVar(value=description), 220)

    buttons_frame = tk.Frame(root, bg="white")
    buttons_frame.place(relx=0.5, rely=0.8, anchor="center")

    def create_styled_button(parent, text, action):
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            bg="#007aff",
            fg="white",
            command=action,
        )
        button.pack(side="left", padx=10, pady=10)

    create_styled_button(buttons_frame, "Download", action=lambda: button_action("Download"))
    create_styled_button(buttons_frame, "Execute", action=lambda: button_action("Execute"))
    create_styled_button(buttons_frame, "Select", action=lambda: button_action("Select"))

    def update_clip_id():
        global global_clip_id

        def save_new_clip_id():
            global global_clip_id
            new_clip_id = clip_id_entry.get()
            global_clip_id = new_clip_id  # Update the global variable
            clip_id_var.set(new_clip_id)
            opus_link_var.set(f'https://clip.opus.pro/clip/{new_clip_id}')
            update_window.destroy()

        update_window = tk.Toplevel(root)
        update_window.title("Update Clip ID")
        update_window.geometry("400x200")
        tk.Label(update_window, text="Enter new Clip ID:", font=("Arial", 14)).pack(pady=10)
        clip_id_entry = tk.Entry(update_window, font=("Arial", 14))
        clip_id_entry.pack(pady=10)
        tk.Button(update_window, text="Save", command=save_new_clip_id, font=("Arial", 14), bg="#007aff",
                  fg="white").pack(pady=10)

    update_button = tk.Button(root, text="Update Clip ID", command=update_clip_id, font=("Arial", 14), bg="#4CAF50",
                              fg="white")
    update_button.place(relx=0.5, rely=0.95, anchor="center")

    def close_instance():
        root.destroy()

    close_button = tk.Button(root, text="Close", command=close_instance, font=("Arial", 14), bg="#ff4d4d", fg="white")
    close_button.place(relx=0.9, rely=0.9, anchor="center")

    root.mainloop()


@interact_bp.route('/start_opus_tk', methods=['POST'])
def opus_tk_handler():
    data = request.json
    video_id = data.get("video_id")
    description = data.get("description")
    category = data.get("category", None)
    clip_id = data.get("clip_id", None)
    selenium_instance_id = data.get("selenium_instance_id")
    instance_id = str(uuid.uuid4())

    thread = threading.Thread(target=opus_interact,
                              args=(video_id, instance_id, description,
                                    selenium_instance_id, category, clip_id))
    thread.daemon = True
    thread.start()

    return jsonify({"instance_id": instance_id}), 200


@interact_bp.route('/close_tk/<instance_id>', methods=['POST'])
def close_tk(instance_id):
    instance = ACTIVE_TK_INSTANCES.pop(instance_id, None)
    if instance is None:
        return jsonify({"error": "Instance not found"}), 404
    instance["root"].destroy()
    return jsonify({"status": f"Instance {instance_id} closed"}), 200


@interact_bp.route('/list_tk', methods=['GET'])
def list_tk():
    return jsonify({"active_instances": list(ACTIVE_TK_INSTANCES.keys())})
