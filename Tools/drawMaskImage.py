from PIL import Image, ImageDraw
import numpy
import os
from typing import *

class maskImage:
    def __init__(self, size: Tuple[int, int] = (0,0)) -> None:
        """Create a new mask image in black and white (mode 1) with given size.

        Parameters
        ----------
        size : Tuple[int, int], optional
            Image size (x,y), by default (0,0)
        """
        self.image = Image.new(
            mode = "1", # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
            size = size, # one-based numbering
            color = 0 # 0: white, 1: black
        )
        self.draw = ImageDraw.Draw(self.image)
        return

    def exportToArray(self) -> numpy.ndarray:
        """Export image to a numpy array.

        Returns
        -------
        numpy.ndarray
            Array image
        """
        return numpy.asarray(self.image)

    def exportToFile(self, path: str = "test.png") -> str:
        """Export image to a file and opens it with default program.

        Parameters
        ----------
        path : str, optional
            Filepath, by default "test.png"

        Returns
        -------
        str
            filepath
        """
        self.image.save(path)
        os.startfile(path)
        return path

    def drawLine(self, coords: Tuple[int, int, int, int], width: int, fill: bool = True) -> None:
        """Draws a line from point A to point B.

        Parameters
        ----------
        coords : Tuple[int, int, int, int]
            Zero-based numbering
        width : int
            Line width
        fill : bool, optional
            True/False white/black, by default True
        """
        self.draw.line(
            xy = coords, #[x1,y1,x2,y2]; zero-based numbering
            fill = fill, #True: white, False: black
            width = width
        )
        return

    def drawRectangle(self, coords: Tuple[int, int, int, int], fill: bool = True) -> None:
        """Draws a rectangle with top-left and bottom-right coordinates.

        Parameters
        ----------
        coords : Tuple[int, int, int, int]
            Zero-based numbering
        fill : bool, optional
            True/False white/black, by default True
        """
        self.draw.rectangle(
            xy = coords, #[x1,y1,x2,y2]; zero-based numbering
            fill = fill #True: white, False: black
        )
        return

    def drawEllipse(self, coords: Tuple[int, int, int, int], fill: bool = True) -> None:
        """Draws an ellipse with top-left and bottom-right coordinates.

        Parameters
        ----------
        coords : Tuple[int, int, int, int]
            Zero-based numbering
        fill : bool, optional
            True/False white/black, by default True
        """
        self.draw.ellipse(
            xy = coords, #[x1,y1,x2,y2]; zero-based numbering
            fill = fill #True: white, False: black
        )
        return

    def setBackgroundImage(self, path: str) -> None:
        """Set a given image as a background image for the mask.
        The mask is converted to RGBA, where black is transparent.

        Parameters
        ----------
        path : str
            Image filepath, should have same resolution with mask image
        """
        background = Image.open(path)
        self.image.convert(mode = "RGBA")
        background.paste(im = self.image, box = [0,0], mask = self.image)
        self.image = background

        return


def main():

    image = maskImage(size = [8192,8192])
    #image.drawRectangle(coords = [1893,5967, 2006,6100])
    #image.drawEllipse(coords = [1893,5967, 2006,6100], fill = False)
    image.drawLine(coords = [1875,5968, 2175,6285], width = 15)
    
    #image.setBackgroundImage(path = r"C:\temp\UnrealPakTool\Photoshop\Miramar_Main_High_Res.png")

    image.exportToFile()
    imageArray = image.exportToArray()
    print(imageArray)

    return

if __name__ == "__main__":
    main()
