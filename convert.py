import open3d as o3d
import numpy as np
import os

def pcd_to_stl_and_visualize(pcd_path):
    # Load the point cloud
    pcd = o3d.io.read_point_cloud(pcd_path)
    
    if not pcd.has_points():
        print("❌ Error: Point cloud is empty or could not be loaded.")
        return
    
    print(f"📊 Point cloud loaded with {len(pcd.points)} points.")
    
    # --- Step 1: Estimate Normals (Required for Reconstruction) ---
    if not pcd.has_normals():
        print("🔍 Estimating normals (small point cloud mode)...")
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=6)
        )
    
    # --- Step 2: Reconstruct Mesh (Convex Hull for Small Clouds) ---
    if len(pcd.points) < 100:
        print("⚠️ Few points detected! Using convex hull instead of Poisson.")
        mesh, _ = pcd.compute_convex_hull()  # Fallback for tiny clouds
        mesh.compute_vertex_normals()  # Needed for proper STL export
    else:
        # Use Poisson for larger clouds
        print("🌀 Running Poisson surface reconstruction...")
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)
        mesh.compute_vertex_normals()
    
    # --- Step 3: Clean the Mesh (Avoid Open3D Warnings) ---
    print("🧹 Cleaning mesh...")
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()
    
    # --- Step 4: Save as STL ---
    output_path = os.path.join(os.path.dirname(pcd_path), "output.stl")
    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"💾 STL saved to: {output_path}")
    
    # --- Step 5: Visualize (With Fallback) ---
    print("👀 Attempting visualization...")
    try:
        # Standard visualization
        o3d.visualization.draw_geometries( # type: ignore
            [mesh],
            zoom=0.7,
            front=[0, 0, -1],
            lookat=mesh.get_center(),
            up=[0, -1, 0],
            mesh_show_back_face=True,
            window_name="3D Mesh Preview"
        )
    except Exception as e:
        print(f"⚠️ Visualization failed: {str(e)}")
        print("🔄 Trying alternative method (mesh.show())...")
        try:
            mesh.show()  # Simpler viewer
        except:
            print("❌ All visualization methods failed. Open 'output.stl' in MeshLab/Blender.")

# Example usage
pcd_file_path = "mouse.pcd"  # 🚨 Replace with your file path!
pcd_to_stl_and_visualize(pcd_file_path)