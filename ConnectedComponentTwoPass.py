import numpy as np


def number_connected_components(edges):
	"""Numbers adjacent pixels in connected components
	
	Given a binary image, make a map that assigns each edge (non-0) pixel
	 to a 'connected component' #, linking adjacent pixels as a component
	 
	Create a dictionary to keep track of which resulting edge component #s
	 are equivalent, e.g.   1 and 3   or   2 and 4   in the example below
	 
	. . . . . . . .			. . . . . . . .
	. 1 . . . . 1 .			. 1 . . . . 2 .
	. 1 . 1 1 . 1 .   ..\	. 1 . 3 3 . 2 .
	. . 1 . . . 1 .   ''/	. . 1 . . . 2 .
	. . . . 1 1 . .			. . . . 4 2 . .
	. . . . . . . .			. . . . . . . .
	
	Args:
		edges (np.array): Binary image containing image edge pixels
	
	Returns: 
		np.array: Map of numbered connected components
		dict: Dictionary containing equivalent component tags
	"""
	
	map = np.zeros(shape=(len(edges),len(edges[0]))).astype(int)
	
	#Dictionary for equivalent tags
	tags = dict()
	#Current component ID number
	segment = 1
	
	
	#For every pixel...
	for row in range(1, len(map)-1):
		for col in range(1, len(map[0])-1):
			
			#If this is an edge pixel
			if(edges[row][col] != 0):
				#														1 2 3
				#Check surrounding 8 pixels for already found (non-0)	4 X .
				#pixels, disregard bottom right 4 for efficiency		. . .
				neighbors = [map[row-1][col-1], map[row-1][col  ], map[row-1][col+1], 
							 map[row  ][col-1]]
				
				
				for pix in neighbors:
					if(pix != 0):
						
						#If we haven't already found a value...
						if(map[row][col] == 0):
							map[row][col] = pix
						
						#If this pix value isn't a duplicate, record it
						elif(pix != map[row][col]):
							tags[ map[row][col] ].add(pix)
							
				
				#If there was no non-zero pixel in neighbors...
				if(map[row][col] == 0):
					map[row][col] = segment
					segment += 1
				
				#If this key doesn't yet exist...
				if(map[row][col] not in tags):
					tags[ map[row][col] ] = set()
	
	return map, tags


#------------------------------------------------------------------------------


def consolidate_tags(tags):
	"""Consolidate component tags so all component pixels have the same number
	
	Taking the dictionary created in the last step, consolidate it so that all 
	equivalent component #s point to a single parent component #
	
	. . . . . . . .			. . . . . . . .		 ...
	. 1 . . . . 2 .			. 3 . . . . 4 .		1: {3}
	. 1 . 3 3 . 2 .   ..\	. 3 . 3 3 . 4 .		2: {4}
	. . 1 . . . 2 .   ''/	. . 3 . . . 4 .		3: { }
	. . . . 4 2 . .			. . . . 4 4 . .		4: { }
	. . . . . . . .			. . . . . . . .		 ...
	
	This below example is different than the one used throughout this file
	
	1: {2, 5}		6: { }			1: {9}		6: { }
	2: {3}			7: {8}	  ..\   2: {9}		7: {9}
	3: { }			8: {9}	  ''/	3: {9}		8: {9}
	4: { }			9: { }			4: { }		9: {1, 2, 3, 5, 7, 8}
	5: {7}			 ...			5: {9}		 ...
	
	
	Args:
		tags (dict): Dictionary representing connected component tags
	
	Returns: 
		dict: Consolidated dictionary representing connected component tags
	"""
	
	#For every component #...
	for compNum in tags:
		
		#Grab the list of numbers this compNum is equivalent to
		lst = list(tags[compNum])
		
		index = 0
		while index < len(lst):
			#For every number this compNum is equivalent to...
			equiv = lst[index]
			
			#Grab the list of numbers THAT is equivalent to
			children = tags[equiv]
			
			#Remove compNum if it exists in this set (we don't want 2 -> 2, ...)
			children.discard(compNum)
			#And add the set to the current running list, minus duplicates
			children.difference_update(lst)
			lst = lst + list(children)
			
			#Point the child # to only this compNum
			tags[equiv] = set([compNum])
			
			index += 1
		
		#Finally, update this compNum in the dictionary with the new extended list
		tags[compNum] = set(lst)
	
	return tags


#------------------------------------------------------------------------------


def trim_tags(tags):
	"""Trim the tags so that parent component #s always point to an empty set
	
	For ease of use and readability, trim the dictionary so that parent 
	 component #s always point to an empty set
	
	This can easily be combined with the step below for a slight increase in
	 efficiency, but is made separate for readability
	
	A parent component # will always point to either:
	 - An empty set
	 - A list of child component #s, all of which will be < parent
	
	1: {9}		6: { }						  1: {9}		6: { }
	2: {9}		7: {9}					..\   2: {9}		7: {9}
	3: {9}		8: {9}					''/	  3: {9}		8: {9}
	4: { }		9: {1, 2, 3, 5, 7, 8}		  4: { }		9: { }
	5: {9}		 ...						  5: {9}		 ...
	
	
	Args:
		tags (dict): Dictionary representing connected component tags
	
	Returns: 
		dict: Trimmed dictionary representing connected component tags
	"""
	
	for key in tags:
		if (len( tags[key] ) > 0):
			if (key > next(iter( tags[key] ))):
				tags[key] = set()
	
	return tags
	

#------------------------------------------------------------------------------


def list_component_coords(map, tags):
	"""Make a list of all coordinates per component
	
	. . . . . . . .			...
	. 3 . . . . 4 .			...
	. 3 . 3 3 . 4 .   ..\	3: (1,1), (2,1), (2,3), (2,4), (3,2)
	. . 3 . . . 4 .   ''/	4: (1,6), (2,6), (3,6), (4,4), (4,5)
	. . . . 4 4 . .			...
	. . . . . . . .			...
	
	
	Args:
		map (np.array): Map of numbered connected components
		tags (dict): Dictionary representing connected component tags
	
	Returns: 
		dict: Dictionary containing coordinates per connected component
	"""
	
	#Create a new dictionary
	components = dict()
	
	for row in range(0, len(map)):
		for col in range(0, len(map[0])):
			
			#If this pixel is part of a component...
			if(map[row][col] != 0):
				
				#Use the tag dictionary to find if this is a parent component #.
				#If it is a child #, we need to find the parent #.
				key = map[row][col]
				s = tags[key]
				
				
				# The step above can be inserted here for efficiency
				
				#If this component points to an empty set, it is a parent
				if (len(s) != 0):
					#Grab the parent #
					key = next(iter( s ))
				
				
				#Add this coordinate to the dictionary
				coord = (row, col)
				
				if(key in components):
					components[key].append([row, col])
				else:
					components.setdefault(key, [[row, col]])
	
	return components


#------------------------------------------------------------------------------


def print_tags(tags):
	for key in tags:
		if (len( tags[key] ) > 0):
			if (key > next(iter( tags[key] ))):
				tags[key] = set()
				