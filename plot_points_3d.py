import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from graph import points  # assumes graph.py is in the same folder

# Unpack points into x, y, z lists
x, y, z = zip(*points)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, c='b', marker='o')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Points Visualization')

plt.show()