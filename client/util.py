import cv2
import math
import numpy as np
import matplotlib.pyplot as plt

predictionLocation = None
falseDetection = []

LEFT = "left"
RIGHT = "right"

netSlope = 0
netIntercept = 0

topSlope = 0
topIntercept = 0

bottomSlope = 0
bottomIntercept = 0

leftSlope = 0
leftIntercept = 0

rightSlope = 0
rightIntercept = 0

recentLocations = []

def getTableSide(location):
	x = location[0]
	y = location[1]
	if x > 0 and y > 0:
		rightSide = (netSlope * x) + netIntercept
		if y > rightSide + 20:
			return RIGHT
		elif y < rightSide - 20:
			return LEFT
		else:
			return ""
	else:
		return ""

def addBallLocation(location, image):
	recentLocations.append(location)
	size = len(recentLocations)
	lineThickness =2
	count = 0
	for loc in recentLocations:
		if count < size - 1:
			cv2.line(image, loc, recentLocations[count+1], (0,255,0), lineThickness)
		count +=1 	

def resetLocations():
	recentLocations = []

knownSide = ""
def colDetection2():
	print(recentLocations)
	size = len(recentLocations)
	if size < 1:
		return False
	x = [i[0] for i in recentLocations]
	y = [k[1] for k in recentLocations]

	a = np.polyfit(x, y, 2)
	b = np.poly1d(a)

	crit = b.deriv().r
	r_crit = crit[crit.imag==0].real
	test = b.deriv(2)(r_crit)
	x_min = r_crit[test>0]
	y_min = b(x_min)
	# print(size)
	# print(a)
	print(b)
	plt.plot(x,y)
	plt.plot(x, b(x))
	plt.plot(x_min, y_min, 'o' )
	plt.show()
	return False


X = 0
Y = 1
MaxFrames = 4
BounceSensitivity = 1.3  # How sensitive it should be to bounces. Bounded from [0, 2]. Lower values = more sensitive.
Xs = []
Ys = []
diffs = []


def col_det(location):
  global Ys, Xs, diffs, BounceSensitivity, X, Y

  bounce = False

  manage_Ys(location[Y])
  manage_Xs(location[X])

  num_Ys = len(Ys)
  num_Xs = len(Xs)
  num_diffs = len(diffs)

  if num_Ys > 1:  # At least 2 frames
	x = Xs[num_Xs - 1]
	prev_x = Xs[num_Xs - 2]
	y = Ys[num_Ys - 1]
	prev_y = Ys[num_Ys - 2]
	if (x - prev_x) > 0:
		diff = (y - prev_y) / (x - prev_x)
		manage_diffs(diff)
	else:
		bounce = False

  if num_diffs > 1:  # At least 3 frames
	diff = diffs[num_diffs - 1]
	prev_diff = diffs[num_diffs - 2]
	if abs(diff) + abs(prev_diff) > BounceSensitivity:
	  bounce = True

  if bounce:
	Xs = []
	Ys = []
	diffs = []

  return bounce


def manage_Xs(x):
  global Xs, MaxFrames

  Xs.append(x)
  if len(Xs) == MaxFrames:
	Xs.pop(0)


def manage_Ys(y):
  global Ys, MaxFrames

  Ys.append(y)
  if len(Ys) == MaxFrames:
	Ys.pop(0)


def manage_diffs(diff):
  global diffs, MaxFrames

  diffs.append(diff)
  if len(diffs) == MaxFrames - 1:
	diffs.pop(0)

# def collisionDetection(location, image):
# 	global recentLocations
# 	maxSize = 20
# 	size = len(recentLocations)

# 	bounce = False
# 	#1 is up, 0 is nothing, -1 is down
# 	direction = 0
# 	newDirection = 0
# 	if size > 2:
# 		lineThickness =2
# 		count = 0
# 		for loc in recentLocations:
# 			if count < size - 1:
# 				cv2.line(image, loc, recentLocations[count+1], (0,255,0), lineThickness)
# 			count +=1 
# 		oldest = recentLocations[0][1]
# 		newest = recentLocations[size - 1][1]
# 		# print(newest, oldest, location[1])
# 		if (newest - oldest) > 0:
# 			direction = -1
# 		else:
# 			direction = 1

# 		if (location[1] - newest) > 0:
# 			newDirection = -1
# 		else: 
# 			newDirection = 1

# 		if direction != newDirection:
# 			if direction == -1:
# 				bounce = True
# 			recentLocations = []

# 	if len(recentLocations) == maxSize:
# 		recentLocations.pop(0)		
# 	recentLocations.append(location)
# 	return bounce

def detectParabola(locations):
	# highestY1 = 0
	# highestY2 = 0
	assumedVertex = 10000

	size = len(locations)

	count = 0
	index = 0
	for loc in locations:
		if loc[1] < assumedVertex:
			assumedVertex = loc[1]
			index = count
		count += 1
	if index < size - 1:
		return False
	else:
		return True

def directionOfBall(locations):
	
	# x movement going down is left
	# x movement going up is right
	size = len(locations)
	if size > 1:
		if locations[0][0] > locations[size-1][0]:
			print("right")
		else:
			print("left")

def isBallOnTable(location):
	x = location[0]
	y = location[1]
	if x > 0 and y > 0:
		#check bottom
		bottomLine = (bottomSlope * x) + bottomIntercept
		if y > bottomLine:
			# print("bottom failed")
			return False
		#check left
		leftLine = (leftSlope * x) + leftIntercept
		if y < leftLine:
			# print("left failed")
			return False
		#check right
		rightLine = (rightSlope * x) + rightIntercept
		if y < rightLine:
			# print("right failed")
			return False
		return True
	else:
		return False


def detectionHandler(detections, img):

	if netSlope == 0 and netIntercept == 0:
		return (0,0), (0,0)
	bestpt1 = (0,0)
	bestpt2 = (0,0)
	for detection in detections:
		height, width = img.shape[:2]
		minDist = 10000
		for detection in detections:
			x, y, w, h = detection[2][0],\
				detection[2][1],\
				detection[2][2],\
				detection[2][3]
			xmin, ymin, xmax, ymax = convertBack(
				float(x), float(y), float(w), float(h))
			pt1 = (xmin, ymin)
			pt2 = (xmax, ymax)

			tmp_img = img

			cropped = tmp_img[ymin:ymax, xmin:xmax]
			if len(cropped) >= 1:
				try:
					dist, r, g, b = getOrangeDistance(cropped)
				except (TypeError):
					print("dumb error")
				else:
					if dist < minDist:
						minDist = dist
						bestpt1 = pt1
						bestpt2 = pt2
	return bestpt1, bestpt2
	#return (0,0), (0,0)

def tableBoundaryHandler(image, tableBoundariesSet):

	global netSlope, netIntercept, topSlope, topIntercept, bottomSlope, bottomIntercept, leftSlope, leftIntercept, rightSlope, rightIntercept
	if len(tableBoundariesSet) == 6:

		netCoordinatesTop = tableBoundariesSet[4]
		netCoordinatesBottom = tableBoundariesSet[5]

		topCoordinatesLeft = tableBoundariesSet[0]
		topCoordinatesRight = tableBoundariesSet[1]

		bottomCoordinatesLeft = tableBoundariesSet[2]
		bottomCoordinatesRight = tableBoundariesSet[3]

		leftCoordinatesTop = tableBoundariesSet[0]
		leftCoordinatesBottom = tableBoundariesSet[2]

		rightCoordinatesTop = tableBoundariesSet[1]
		rightCoordinatesBottom = tableBoundariesSet[3]

		netSlope = float((netCoordinatesTop[1] - netCoordinatesBottom[1])) / float((netCoordinatesTop[0] - netCoordinatesBottom[0]))
		netIntercept = netCoordinatesTop[1] - netSlope * netCoordinatesTop[0]

		# topSlope = (topCoordinatesLeft[1] - topCoordinatesRight[1]) / (topCoordinatesLeft[0] - topCoordinatesRight[0]);
		# topIntercept = topCoordinatesLeft[1] - topSlope * topCoordinatesRight[0]

		bottomSlope = float((bottomCoordinatesLeft[1] - bottomCoordinatesRight[1])) / float((bottomCoordinatesLeft[0] - bottomCoordinatesRight[0]))
		bottomIntercept = bottomCoordinatesLeft[1] - bottomSlope * bottomCoordinatesRight[0]

		leftSlope = float((leftCoordinatesTop[1] - leftCoordinatesBottom[1])) / float((leftCoordinatesTop[0] - leftCoordinatesBottom[0]))
		leftIntercept = leftCoordinatesTop[1] - leftSlope * leftCoordinatesTop[0]

		rightSlope = float((rightCoordinatesTop[1] - rightCoordinatesBottom[1])) / float((rightCoordinatesTop[0] - rightCoordinatesBottom[0]))
		rightIntercept = rightCoordinatesTop[1] - rightSlope * rightCoordinatesTop[0]



		lineThickness = 2
		# (x1, y1) (x2, y2) (x3, y3), (x4, y4)

		#top/bottom lines
		cv2.line(image, topCoordinatesLeft, topCoordinatesRight, (0,255,0), lineThickness)
		cv2.line(image, bottomCoordinatesLeft, bottomCoordinatesRight, (0,255,0), lineThickness)

		#left/right lines
		cv2.line(image, leftCoordinatesTop, leftCoordinatesBottom, (0,255,0), lineThickness)
		cv2.line(image, rightCoordinatesTop, rightCoordinatesBottom, (0,255,0), lineThickness)

		length =  distance(tableBoundariesSet[0], tableBoundariesSet[1])
		projectedLength = int(length / 5)

		pLeft = tableBoundariesSet[0]
		pRight = tableBoundariesSet[1]

		pl = list(pLeft)
		pr = list(pRight)
		pl[1] = pl[1] - projectedLength
		pr[1] = pr[1] - projectedLength

		projectedLeft = tuple(pl)
		projectedRight = tuple(pr)

		cv2.line(image, tableBoundariesSet[0], projectedLeft, (0,255,0), lineThickness)
		cv2.line(image, tableBoundariesSet[1], projectedRight, (0,255,0), lineThickness)
		cv2.line(image, projectedLeft, projectedRight, (0,255,0), lineThickness)


		cv2.line(image, tableBoundariesSet[4], tableBoundariesSet[5], (0,255,0), lineThickness)


def distance(p0, p1):
	return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def magnitude(v0):
	return math.sqrt(v0[0]**2 + v0[1]**2)

def dotProduct(v0, v1):
	return (v0[0] * v1[0]) + (v0[1] * v1[1])

def getCenterPoint(x1, y1, x2, y2):
	centerPoint = ((x1 + x2) / 2, (y1 + y2) / 2)
	return centerPoint

def getOrangeDistance(img):
	total_r = 0
	total_g = 0
	total_b = 0
	count = 0
	for row in img:
		for pix in row:
			total_r += pix[0]
			total_g += pix[1]
			total_b += pix[2]
			count += 1
	if count <= 0:
		return 1000
	total_r /= count
	total_g /= count
	total_b /= count
	
	distance = math.sqrt((105-total_r)**2+(75-total_g)**2+(30-total_b)**2)
	return distance, total_r, total_g, total_b
	#print(distance)


def convertBack(x, y, w, h):
	xmin = int(round(x - (w / 2)))
	xmax = int(round(x + (w / 2)))
	ymin = int(round(y - (h / 2)))
	ymax = int(round(y + (h / 2)))
	return xmin, ymin, xmax, ymax