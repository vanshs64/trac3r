import open3d as o3d
import numpy as np

# Load TXT data into a NumPy array
points = np.loadtxt("points.txt")

# Convert to Open3D point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

# Visualize
o3d.visualization.draw_geometries([pcd])
