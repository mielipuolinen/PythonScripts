import numpy

def DrawCircleMatrix(radius):
    x = y = radius - 1 # Offset for a zero-based numbering
    r = radius - 1 # Offset for a centerpoint; Radius is a measurement from a centerpoint to an edge.
    i = r
    j = 0
    decision = 0

    while (i >= j):

        pixels = [
            [x+i, y+j, False],
            [x+i, y-j, False],
            [x+j, y+i, False],
            [x+j, y-i, False],
            [x-i, y+j, False],
            [x-i, y-j, False],
            [x-j, y+i, False],
            [x-j, y-i, False],
        ]

        for pixel in range(len(pixels)):

            # Check if this pixel is already done
            if pixels[pixel][2]:
                continue

            # Check for duplicate pixels; skip already done pixels or mark found duplicates done
            for pixel_comparison in range(len(pixels)):
                if ( pixels[pixel][0] == pixels[pixel_comparison][0] ) and \
                   ( pixels[pixel][1] == pixels[pixel_comparison][1] ) :

                    # Found duplicate, mark it done:
                    if not pixels[pixel_comparison][2]:
                        pixels[pixel_comparison][2] = True

                    # This pixel is already done, skip it:
                    else:
                        break
            else:
                DrawPixelOnMatrix(pixels[pixel][0], pixels[pixel][1])
                pixels[pixel][2] = True

                # Fill circle:
                # NOTE: Imperfect; This may draw same pixels multiple times, depends on the size of a circle
                x_diff = x - pixels[pixel][0]
                if x_diff >= 0:
                    for n in range( 1, x_diff + 1 ):
                        DrawPixelOnMatrix(pixels[pixel][0] + n, pixels[pixel][1])
                elif x_diff < 0:
                    x_diff = x_diff * (-1)
                    for n in range( 1, x_diff ):
                        DrawPixelOnMatrix(pixels[pixel][0] - n, pixels[pixel][1])
                

        # Midpoint Circle Algorithm
        # Loop through pixels calculated by the algorithm
        if(decision <= 0):
            j += 1
            decision += 1 + 2 * j

        if(decision > 0):
            i -= 1
            decision += 1 - 2 * i
        
    return

def DrawPixelOnMatrix(x,y):
    global circleMatrix
    circleMatrix[x,y] = 1

    return


def CreateCircleMatrix(radius):
    # -1 offset for centering the circle
    x = y = radius * 2 - 1

    global circleMatrix
    circleMatrix = numpy.zeros(
                shape = (x, y), 
                dtype = numpy.uint8
             )

    DrawCircleMatrix(radius)

    return circleMatrix

def main():
    
    CreateCircleMatrix(10)

    global circleMatrix
    print(circleMatrix)

    return

if __name__ == "__main__":
    main()
