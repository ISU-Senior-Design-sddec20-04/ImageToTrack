import skimage
from skimage import feature


def img_to_edges(image_gray, sigma=2.4, low_threshold=0.04, high_threshold=0.17):
	"""Converts a grayscale image to a binary image representing edges.
	
	Takes a grayscale image and 3 optional parameters. Uses skimage's canny edge
	detection and outputs a binary image with each pixel representing an edge.
	
	Args:
		image_gray (np.array): Grayscale image to be converted
		sigma (int): Canny edge detection parameter (Optional)
		low_threshold (int): Canny edge detection parameter (Optional)
		high_threshold (int): Canny edge detection parameter (Optional)
	
	Returns: 
		np.array: Binary image representing edges from image_gray
	"""
	
	#Perform Canny edge detection on the image
	edges = skimage.feature.canny(
	    image=image_gray,
	    sigma=sigma,
	    low_threshold=low_threshold,
	    high_threshold=high_threshold,
	)
	
	return edges
	
	
	
	
	
	