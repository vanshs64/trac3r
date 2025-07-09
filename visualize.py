import open3d as o3d

# Load your point cloud
pcd = o3d.io.read_point_cloud("cube.pcd")

# Visualize it
o3d.visualization.draw_geometries([pcd])
