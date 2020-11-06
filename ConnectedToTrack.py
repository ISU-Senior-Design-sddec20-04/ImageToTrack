from collections import deque 


# To store image pixel cordinates 
class Point: 
	def __init__(self, r: int, c: int): 
		self.r = r	#Row
		self.c = c 	#Col


class Node:
	def __init__(self, pt: Point):
		self.pt = pt		#The point in the image this represents
		self.children = []	#Points that followed this one in BFS
		self.depth = -1		#Depth of this node in the tree	
		self.farthestLeaf = -1	#Distance to farthest leaf node from this node
		self.parent = None
	
	
	def __str__(self):
		ret = "({}, {})".format(self.pt.r, self.pt.c)
		return ret
		
	def brack(self):
		ret = "[{}, {}]".format(self.pt.r, self.pt.c)
		return ret
	
	def norm(self):
		ret = "{} {}".format(self.pt.r, self.pt.c)
		return ret
		
		
	def __repr__(self, depth=0):
		ret = ": "*depth+"({}, {}) {}".format(self.pt.r, self.pt.c, self.farthestLeaf)+"\n"
		for child in self.children:
			ret += child.__repr__(depth+1)
		return ret


#Is this point in bounds
def inBounds(row: int, col: int, ROW: int, COL: int):
	return (row >= 0) and (row < ROW) and (col >= 0) and (col < COL)


# These arrays are used to get row and column  
# numbers of 8 neighbours of a given cell  
ROWDELTA = [-1, -1, -1,
			 0,      0,
			 1,  1,  1]
COLDELTA = [-1,  0,  1,
			-1,      1,
			-1,  0,  1]


#------------------------------------------------------------------------------


def BFS(img, start: Point):
	"""Visit all pixels via BFS
	
	Run BFS on the map of connected pixels to represent drawing the image 
	 without lifting your pencil. 
	
	BFS rather than DFS ensures we get adjacent pixels first rather than 
	 reaching the end and then having to retrace for one pixel at the beginning
	
	Args:
		img (np.array): Map of connected pixels to be traced
		start (Point): Starting point to begin BFS
	
	Returns: 
		node: Root node of our BFS tree
		int: MaxDepth reached during BFS
	"""
	
	ROW = len(img)
	COL = len(img[0])
	
	visited = [[False for i in range(COL)] for j in range(ROW)] 
	
	#Mark the start pixel as visited
	visited[start.r][start.c] = True
	
	#Create a queue to hold points to be visited
	q = deque()
	
	node = Node(start)
	
	#Enqueue and set this node to the root of our BFS result tree
	q.append(node)
	root = node
	root.depth = 0
	
	#Keep track of the maximum depth
	maxDepth = 0


	#While the queue still has more nodes...
	while q:
		#Dequeue the next point
		curr = q.popleft()
		
		#Enqueue the adjacent points
		for i in range(8):
			#Calculate the coordinates of the next point
			row = curr.pt.r + ROWDELTA[i]
			col = curr.pt.c + COLDELTA[i]
			
			
			#If this point is in bounds, is a valid edge,
			#and hasn't been visited yet...
			if(inBounds(row, col, ROW, COL) and (img[row][col] > 0) and (not visited[row][col])):
				visited[row][col] = True
				adjPoint = Node(Point(row, col))
				adjPoint.depth = curr.depth+1	#Update our depth
				
				maxDepth = max(maxDepth, adjPoint.depth)
				
				#Enqueue it and add it to the tree
				q.append(adjPoint)
				curr.children.append(adjPoint)
				adjPoint.parent = curr
	
	
	return root, maxDepth


#------------------------------------------------------------------------------


def postorder(root: Node):
	"""Postorder traversal recording farthest child depth and sorting tree
	
	Perform a postorder traversal, record farthest child depth and sort node 
	 children on that rather than printing as a usual postorder would
	
	
	Args:
		root (Node): BFS tree to perform postorder traversal on
	
	Returns: 
		list: Postorder traversal result stack
	"""
	
	#Create stacks for postorder traversal
	stack = [] 
	stack2 = []
	
	#Add the root node to the stack
	stack.append(root) 
	
	while(len(stack)): 
		#Pop the next node
		curr = stack.pop()
		stack2.append(curr)
		children = curr.children
		
		for child in children:
			stack.append(child)
	
	return stack2


#------------------------------------------------------------------------------


def sort_tree(stack: list): 
	"""Sort a BFS tree using its postorder traversal
	
	As the postorder traversal of a BFS contains references to each node in a 
	 BFS, simply sort the BFS using the postorder stack
	
	Args:
		stack (list): Postorder traversal result stack, contains node references
	"""
	
	#Stack holds the postorder traversal of our tree
	stack.reverse()
	
	for node in stack:
		if (len(node.children) == 0):
			node.farthestLeaf = 0
		
		node.children = sorted(node.children, key=lambda child: child.farthestLeaf, reverse=True)
		
		parent = node.parent
		
		#If this is the root node, we're done
		if (node.parent == None):
			return
		
		parent.farthestLeaf = max(node.farthestLeaf + 1, parent.farthestLeaf)


#------------------------------------------------------------------------------


def tree_to_track(root: Node, maxDepth: int):
	"""Convert BFS tree to a cartesian Sisyphus table track
	
	Args:
		root (Node): BFS tree to perform postorder traversal on
		maxDepth (int): Maximum depth of the BFS tree 'root'
	
	Returns: 
		list: List of cartesian coordinates for the table to draw
	"""
	
	TRACK = []
	
	stack = []
	stack.append(root)
	
	goingUp = False	#If True and the current node has children, dont print
	existsChildAbove = None
	
	
	while(len(stack)):
		curr = stack[len(stack)-1]
		children = curr.children
		
		#The existence of an untouched child will tell us not to stop 
		# if we reach maxDepth
		if(curr == existsChildAbove):
			existsChildAbove = None
		
		if(len(children) > 1 and existsChildAbove is None):
			existsChildAbove = children[0]
		
		
		#If we're not moving upward to a node with children...
		if(not(goingUp and len(children))):
			ret = ": "*(len(stack)-1)+"{}".format(curr)
			#TRACK.append(Node.brack(curr))
			TRACK.append(Node.norm(curr))
	
	
	
		#If this node has more children...
		if (len(children) > 0):
			#Move the last child to the stack
			stack.append(children.pop())
			goingUp = False
				
		
		else: #Remove it
			stack.pop()
			goingUp = True
	
			#If we've reached maxDepth and touched all nodes, we're done
			if (curr.depth == maxDepth-1 and existsChildAbove is None):
				break
				
		
	return TRACK


#------------------------------------------------------------------------------


def find_start(img):
	"""Find the best coordinate to start BFS 
	
	Find the closest pixel to the edge of the image as a coord to start the 
	 marble from. Circle clockwise around the image until an edge pixel is 
	 found, then return it
	
	Algorithm from https://www.geeksforgeeks.org/print-a-given-matrix-in-spiral-form/
	
	Because the binary image created earlier has no edge pixels on the 
	 outermost pixel ring, skip it
	
	
	Args:
		img (np.array): Image to find the starting point of
	
	Returns: 
		Point: Recommended starting point for BFS for the input image
	"""
	
	l = 0 +1
	k = 0 +1
	m = len(img) -1
	n = len(img[0]) -1
	
	while(k < m and l < n):
		
		#Check the top-most row
		for i in range(l, n):
			if(img[k][i] > 0):
				return Point(k, i)
		k += 1
		
		for i in range(k, m):
			if(img[i][n-1] > 0):
				return Point(i, n-1)
		n -= 1
		
		if(k < m):
			for i in range(n-1, l-1, -1):
				if(img[m-1][i] > 0):
					return Point(m-1, i)
			m -= 1
		
		if(l < n):
			for i in range(m-1, k-1, -1):
				if(img[i][l] > 0):
					return Point(i, l)
			l += 1
	
	return -1