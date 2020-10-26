import numpy as np
import sys
import scipy
from scipy import spatial  #For cKDTree



def build_cKDTree(components):
	"""Generate 2d-trees for each connected component to speed up searches
	
	Using the given list of coordinates per connected component, build 
	 individual 2d-trees (kd-tree) for each component to speed up 
	 nearest-neighbor searches
	
	
	Args:
		components (dict): Dictonary containing coordinates per connected component
	
	Returns: 
		dict: Dictionary containing 2d-trees per connected component
	"""
	
	trees = dict()
	for comp in components:
		trees[comp] = spatial.cKDTree(components[comp])
	
	return trees


#------------------------------------------------------------------------------


def build_shortest_dist_matrix(components, trees):
	"""Build an adjacency matrix between all components using shortest dist
	
	Build an adjacency matrix between all components, using the shortest
	 distance between two respective components as an edge
	
	Notes for improvement: - - - - - - - - - - - - - - - - - - - - - - - - - -
	Could also weight the cost based on whether the start and end points are 
	 a line segment end or not here for better end results
	
	Could implement a system to keep track of line segment endpoints in 
	 ConnectedComponentTwoPass's 
	  number_connected_components or list_component_coords
	
	This would likely require redefining euclideanDistance, as that is what
	 cKDTree uses to determine distance
	 Example: http://code.activestate.com/recipes/578434-a-simple-kd-tree-example-with-custom-euclidean-dis/
	
	 ...											  _________3________ ...
	   3: (1,1), (2,1), (2,3), (2,4), (3,2)	..\		4| [(2,4), (2,6), 2]
	   4: (1,6), (2,6), (3,6), (4,4), (4,5)	''/		5| [(2,4), (2,9), 5]
	   5: (2,9), (3,9)							   	 |		  ...
	 ...											 |	Start   End  Dist
	
	
	Args:
		components (dict): Dictonary containing coordinates per connected component
		trees (dict): Dictionary containing 2d-trees per connected component
	
	Returns: 
		np.array: Adjacency matrix containing shortest distance between all components
	"""
	
	size = len(trees.keys())
	adjacency = np.zeros(shape=(size, size)).astype(tuple)
	
	i, j = 0, 0
	comps = list(components.keys())
	
	
	#For every component
	for i, startingComp in enumerate(comps):
		coords = components[startingComp]
		#print("Querying from component", startingComp)
		
		#Find closest points between this component and    lst: 1, *3*, 7, 11, 9, 2
		#those components ahead of it in the list					  | ->
		for j in range(i+1, len(comps)):
			endingComp = comps[j]
			tree = trees[endingComp]
			
			#Query tree with each point from startingComp
			distances, indices = tree.query(coords, k=1)
			
			#Find the index of the shortest distance
			minDistanceIndex = np.argmin(distances)
			minDistance = distances[minDistanceIndex]
			
			#Find the respective points
			start = coords[minDistanceIndex]
			end = tree.data[ indices[minDistanceIndex] ].astype(int)
			
			
			#Add these points to the adjacency list
			adjacency[i][j]= adjacency[j][i]= (tuple(start),tuple(end),minDistance)
	
	
	return adjacency


#------------------------------------------------------------------------------


def dist_to_MST(adjacency):
	"""Build an MST using an adjacency matrix containing distances
	
	Using the adjacency matrix from the last step, create a minimum spanning 
	 tree with distance as the edge cost
	
	The below is Prim's algorithm
	
	
	Args:
		adjacency (np.array): Adjacency matrix containing shortest distance between all components
	
	Returns: 
		list: Minimum Spanning Tree containing connected component distances
	"""
	
	numVertices = len(adjacency)
	visited = [False] * numVertices
	numEdges = 0
	
	#List to store the MST
	MST = []
	
	
	#Set the first vertex to 'visited'
	visited[0] = True
	
	while (numEdges < numVertices - 1):
		min = sys.maxsize
		x = 0
		y = 0
		
		for i in range(numVertices):
			if (visited[i]):
				
				for j in range(numVertices):
					if (not visited[j]):
						if (min > adjacency[i][j][2]):
							min = adjacency[i][j][2]
							x = i
							y = j
		
		
		MST.append(adjacency[x][y])
		visited[y] = True
		numEdges += 1
	
	return MST


#------------------------------------------------------------------------------


def draw_connections(map, MST):
	"""Using an MST containing coordinates, draw lines from each connected coord
	
	Using the MST created above, draw lines along the edges between closest 
	 points to link components
	
	The below is Bresenham's Line Generation algorithm
	
	. . . . . . . .
	. 3 . . . . 4 .
	. 3 . 3 3 = 4 .
	. . 3 . . . 4 .
	. . . . 4 4 . .
	. . . . . . . .
	
	
	Args:
		map (np.array): Map of numbered connected components
		MST (list): Minimum Spanning Tree containing connected component distances
	
	Returns: 
		np.array: Map of edge pixels with connection lines drawn
	"""
	
	for edge in MST:
		#Set up initial conditions
		x1, y1 = edge[0]
		x2, y2 = edge[1]
		dx = x2 - x1
		dy = y2 - y1
		
		#Determine if the line slopes vertically or horizontally
		slopedVertically = abs(dy) > abs(dx)
		
		
		
		#Rotate if vertically sloped
		if (slopedVertically):
			x1, y1 = y1, x1
			x2, y2 = y2, x2
		
		#Swap points to keep things positive
		if (x1 > x2):
			x1, x2 = x2, x1
			y1, y2 = y2, y1
		
		
		#Recalculate slopes
		dx = x2 - x1
		dy = y2 - y1
		
		#Calculate error
		error = int(dx / 2)
		ystep = 1 if (y1 < y2) else -1
		
		#Generate points
		y = y1
		for x in range(x1, x2+1):
			
			if (slopedVertically):
				map[y][x] = 255
			else:
				map[x][y] = 255
			
			error -= abs(dy)
			if (error < 0):
				y += ystep
				error += dx

	return map
	

#------------------------------------------------------------------------------


def print_map(map):
	#Print the new map
	for row in range(0, len(map)):
		print()
		
		for col in range(0, len(map[0])):
			
			if(map[row][col] != 0):
				
				print(" O ", end="")
			else:
				#print("-|-", end="")
				print("   ", end="")