import sys
import skimage
from skimage import io

__author__ = "Sean Gordon"
__email__ = "SeanGordonkh@gmail.com"
__license__ = "GPL"
__status__ = "Production"

"""Convert Image to a Sisyphus table track

Converts an image into a cartesian coord track for the Sisyphus table:
https://sisyphus-industries.com/


Call the script like so:
python .\ImageToTrack.py .\YOUR_IMAGE_HERE.png

The filetype does not need to be png
"""

# read command-line arguments
filename = sys.argv[1]

# load the original image as grayscale
image = skimage.io.imread(fname=filename, as_gray=True)
image = image[::-1,:] 		#Flip the track for better results on the table

import time
startTime = time.time()


#------------------------------------------------------------------------------
# Convert image to edges

from ImgToEdges import img_to_edges
edges = img_to_edges(image)


#------------------------------------------------------------------------------
# Connect disjoint line segments in edges image

from ConnectedComponentTwoPass import *
map, tags = number_connected_components(edges)

tags = consolidate_tags(tags)
tags = trim_tags(tags)

components = list_component_coords(map, tags)


#------------------------------------------------------------------------------
# Connect all individual edge segments

from ConnectComponents import *
trees = build_cKDTree(components)

adjacency = build_shortest_dist_matrix(components, trees)
MST = dist_to_MST(adjacency)

img = draw_connections(map, MST)


#------------------------------------------------------------------------------
# Brighten the resulting image

for row in range(len(img)):
	for col in range(len(img[0])):
		if (img[row][col] > 0):
			img[row][col] = 255


#------------------------------------------------------------------------------
# Convert the connected edge segments to a table track in cartesian coords

from ConnectedToTrack import *
start = find_start(img)

tree, maxDepth = BFS(img, start)
stack = postorder(tree)
sort_tree(stack)

TRACK = tree_to_track(tree, maxDepth)


#Save the track to a file
with open("{}.txt".format(filename.rsplit(".", 1)[0]), "w") as filehandle:
	for point in TRACK:
		filehandle.write("%s\n" % point)



endTime = time.time()
print("\nScript Runtime: {}\n".format(endTime-startTime))


#Save the final non-upside-down edge image as a preview
io.imsave(fname='result.png', arr=skimage.img_as_int(img[::-1,:]))