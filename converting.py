import open3d as o3d
import numpy as np
import os
from formatPCD import convert_to_pcd 

def crop_to_object_xy(pcd, z_threshold=5.0, xy_margin=5.0):
    points = np.asarray(pcd.points)
    z_values = points[:, 2]

    # Step 1: Use elevated points to find object XY bounds
    bed_z = np.median(z_values)
    object_mask = z_values > bed_z + z_threshold
    object_points = points[object_mask]

    if object_points.size == 0:
        print("mo elevated points detected. Check threshold.")
        return pcd

    x_min, y_min = np.min(object_points[:, :2], axis=0) - xy_margin
    x_max, y_max = np.max(object_points[:, :2], axis=0) + xy_margin

    # Step 2: Keep all points within that XY region (including flat bedplate)
    xy_mask = (
        (points[:, 0] >= x_min) & (points[:, 0] <= x_max) &
        (points[:, 1] >= y_min) & (points[:, 1] <= y_max)
    )

    filtered_points = points[xy_mask]
    print(f"cropped to bounding box: {len(filtered_points)} points remain.")

    pcd.points = o3d.utility.Vector3dVector(filtered_points)
    return pcd


def amplify_z(pcd, scale):
    """Stretch the Z values to exaggerate height features."""
    points = np.asarray(pcd.points)
    points[:, 2] *= scale
    pcd.points = o3d.utility.Vector3dVector(points)
    return pcd


def pcd_to_stl_and_visualize(pcd_path):
    # Load the point cloud
    pcd = o3d.io.read_point_cloud(pcd_path)
    pcd = crop_to_object_xy(pcd)
    pcd = amplify_z(pcd, scale=5)  # You can tune this value (e.g. 1.5–3.0)


    if not pcd.has_points():
        print("error: Point cloud is empty or could not be loaded.")
        return
    
    print(f"point cloud loaded with {len(pcd.points)} points.")
    
    # --- Step 1: Estimate Normals (Required for Reconstruction) ---
    if not pcd.has_normals():
        print("Estimating normals (small point cloud mode)...")
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=6)
        )
    
    # --- Step 2: Reconstruct Mesh (Convex Hull for Small Clouds) ---
    if len(pcd.points) < 100:
        print("few points detected- Using convex hull instead of Poisson.")
        mesh, _ = pcd.compute_convex_hull()  # Fallback for tiny clouds
        mesh.compute_vertex_normals()  # Needed for proper STL export
    else:
        # Use Poisson for larger clouds
        # print("Running Poisson surface reconstruction...")
        # mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)

        # print("Running Alpha Shape model")
        # mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha=0.1)

        print("Using ball pivoting")
        radii = [0.005, 0.01, 0.02]
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd, o3d.utility.DoubleVector(radii)
        )


        mesh.compute_vertex_normals()
    
    # --- Step 3: Clean the Mesh (Avoid Open3D Warnings) ---
    print("cleaning mesh...")
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()


    mesh.paint_uniform_color([0.3, 0.8, 0.3])  # Light green
    
    # --- Step 4: Save as STL ---
    output_path = os.path.join(os.path.dirname(pcd_path), "output.stl")
    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"💾 STL saved to: {output_path}")
    
    # --- Step 5: Visualize (With Fallback) ---
    print("attempting visualization...")
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
        print(f"Visualization failed: {str(e)}")
        print("🔄 Trying alternative method (mesh.show())...")
        try:
            mesh.show()  # Simpler viewer
        except:
            print("visualization methods failed. Open 'output.stl' in MeshLab/Blender.")

def pcd_to_stl_and_visualize_custom(pcd_path, output_path, visualize=True):
    # --- Your current code with only 2 changes: ---
    # 1. Replace `output_path = ...` with the given output_path
    # 2. Wrap visualization section inside `if visualize:`

    pcd = o3d.io.read_point_cloud(pcd_path)
    pcd = crop_to_object_xy(pcd)
    pcd = amplify_z(pcd, scale=1)

    if not pcd.has_points():
        print("error: Point cloud is empty or could not be loaded.")
        return

    print(f"point cloud loaded with {len(pcd.points)} points.")

    if not pcd.has_normals():
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=6)
        )

    if len(pcd.points) < 100:
        mesh, _ = pcd.compute_convex_hull()
        mesh.compute_vertex_normals()
    else:
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)
        mesh.compute_vertex_normals()

    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()
    mesh.paint_uniform_color([0.3, 0.8, 0.3])

    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"💾 STL saved to: {output_path}")

    if visualize:
        try:
            o3d.visualization.draw_geometries(
                [mesh],
                zoom=0.7,
                front=[0, 0, -1],
                lookat=mesh.get_center(),
                up=[0, -1, 0],
                mesh_show_back_face=True,
                window_name="3D Mesh Preview"
            )
        except Exception as e:
            print(f"Visualization failed: {str(e)}")

def batch_convert_pcds_to_stl(directory="./pcd", visualize=False):
    """Converts all .pcd files in a folder to .stl using existing pipeline."""
    files = sorted(f for f in os.listdir(directory) if f.endswith(".pcd"))

    if not files:
        print("❌ No .pcd files found in the directory.")
        return

    for filename in files:
        pcd_path = os.path.join(directory, filename)
        base_name = os.path.splitext(filename)[0]
        stl_path = os.path.join(directory, f"{base_name}.stl")

        print(f"\n🌀 Converting {filename} → {base_name}.stl")
        
        # Temporarily override the STL output path in your function
        def wrapped_conversion(pcd_path_override):
            nonlocal stl_path
            # Copy the function body from `pcd_to_stl_and_visualize` here but replace "output.stl" with `stl_path`
            # OR better:
            pcd_to_stl_and_visualize_custom(pcd_path_override, stl_path, visualize)

        wrapped_conversion(pcd_path)

    print(f"\n converted {len(files)} PCDs to STL.")

# mainFilePath = "katHandResult.pcd"
# # Example usage
# convert_to_pcd("katHand.pcd", mainFilePath) #file path

# pcd_to_stl_and_visualize(mainFilePath)



mainFilePath = "pcd/spruhaHand.pcd"
# Example usage
convert_to_pcd("pcd/spruha.pcd", mainFilePath) #file path

pcd_to_stl_and_visualize(mainFilePath)

# batch_convert_pcds_to_stl("pcd") # directory containing all the pcd filesp