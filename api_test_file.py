import tkinter as tk
import webbrowser

def create_interaction_form(video_id, instance_id, description, clip_id=None):
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
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

    def send_post_request(url, payload):
        print(f"POST to {url} with {payload}")

    def create_button_action(post_url, label):
        return lambda: send_post_request(
            post_url,
            {
                "video_id": video_id,
                "instance_id": instance_id,
                "action": label
            },
        )

    def open_video_link(link):
        webbrowser.open(link)

    root = tk.Tk()
    root.title("Interaction Form")
    root.geometry("800x600")
    root.configure(bg="#f5f5f5")

    # Background rectangle with rounded edges
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
    title_label.place(relx=0.5, rely=0.15, anchor="center")

    details_frame = tk.Frame(root, bg="white")
    details_frame.place(relx=0.5, rely=0.4, anchor="center", width=700, height=200)

    def create_labeled_row(parent, label_text, value_text, y_offset, clickable=False, link=None):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#555555",
        )
        label.place(relx=0.05, y=y_offset, anchor="w")

        if clickable:
            value = tk.Label(
                parent,
                text=value_text,
                font=("Arial", 14, "underline"),
                bg="white",
                fg="#007aff",
                cursor="hand2",
            )
            value.bind("<Button-1>", lambda e: open_video_link(link))
        else:
            value = tk.Label(
                parent,
                text=value_text,
                font=("Arial", 14),
                bg="white",
                fg="#333333",
            )
        value.place(relx=0.35, y=y_offset, anchor="w")

    create_labeled_row(details_frame, "Video ID:", video_id, 20)
    create_labeled_row(details_frame, "Clip ID:", clip_id, 60)
    if clip_id is not None:
        create_labeled_row(details_frame, "Opus Clipping Link:", 'https://clip.opus.pro/clip/' + clip_id, 100, clickable=True, link='https://clip.opus.pro/clip/' + clip_id)
    else:
        create_labeled_row(details_frame, "Opus Clipping Link:", 'clip_id not supplied', 100, clickable=True, link='https://clip.opus.pro/')
    create_labeled_row(details_frame, "Video Link:", 'https://youtube.com/watch?v=' + video_id, 140, clickable=True, link='https://youtube.com/watch?v=' + video_id)
    create_labeled_row(details_frame, "Instance ID:", instance_id, 180)
    create_labeled_row(details_frame, "Description:", description, 220)

    buttons_frame = tk.Frame(root, bg="white")
    buttons_frame.place(relx=0.5, rely=0.8, anchor="center")

    def create_styled_button(parent, text, action):
        button = tk.Canvas(parent, width=120, height=50, bg="white", highlightthickness=0)
        button.create_rounded_rectangle(0, 0, 120, 50, radius=20, fill="#007aff", outline="")
        button.create_text(60, 25, text=text, font=("Arial", 14, "bold"), fill="white")
        button.bind("<Button-1>", lambda e: action())
        button.pack(side="left", padx=10)

    create_styled_button(buttons_frame, "Option 1", create_button_action("http://example.com/api/option1", "Select"))
    create_styled_button(buttons_frame, "Option 2", create_button_action("http://example.com/api/option2", "Download"))
    create_styled_button(buttons_frame, "Option 3", create_button_action("http://example.com/api/option3", "Execute"))
    create_styled_button(buttons_frame, "Option 4", create_button_action("http://example.com/api/option4", "Close"))

    root.mainloop()


if __name__ == "__main__":
    video_id = "example_video_id"
    instance_id = "example_instance_id"
    description = "Example description of the video"

    create_interaction_form(video_id, instance_id, description)
