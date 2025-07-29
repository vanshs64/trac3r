import open3d as o3d
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading

# Initialize the visualization window globally
vis = None

def visualize_pcd(pcd_path):
    # Load point cloud
    pcd = o3d.io.read_point_cloud(pcd_path)
    if pcd.is_empty():
        print("Failed to load PCD or it's empty:", pcd_path)
        return

    # Create a new visualization window (blocking)
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="PCD Viewer", width=800, height=600)
    vis.add_geometry(pcd)

    # Set rendering options
    render_option = vis.get_render_option()
    render_option.point_size = 5.0  # Enlarge point size
    render_option.background_color = [0, 0, 0]

    vis.run()  # Blocking call — keeps window open until closed
    vis.destroy_window()

# GUI setup
def on_drop(event):
    filepath = event.data.strip('{}')  # Remove braces if file has spaces
    if filepath.lower().endswith(".pcd"):
        visualize_pcd(filepath)

root = TkinterDnD.Tk()
root.title("Drag and Drop a .pcd File")
root.geometry("400x200")

label = tk.Label(root, text="Drop a .pcd file here", font=("Arial", 16))
label.pack(expand=True, fill="both")

label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", on_drop)

root.mainloop()
