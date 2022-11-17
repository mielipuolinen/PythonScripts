from PIL import Image, ImageDraw
import os
import json
import numpy
import math
from library.drawCircleMatrix import CreateCircleMatrix
from library.drawMaskImage import maskImage

circles_collection_json = r"C:\temp\UnrealPakTool\PUBG API\circle_collection.json"
minimaps = {
    #"Baltic_Main": r"C:\temp\UnrealPakTool\Photoshop\Erangel_Main_High_Res.png",
    "Baltic_Main": r"C:\temp\UnrealPakTool\Photoshop\Erangel_zones_8192x8192.png",
    #"Desert_Main": r"C:\temp\UnrealPakTool\Photoshop\Miramar_Main_High_Res.png",
    "Desert_Main": r"C:\temp\UnrealPakTool\Photoshop\Miramar_zones_8192x8192.png",
    "Tiger_Main": r"C:\temp\UnrealPakTool\Photoshop\Taego_Main_High_Res.png"
}
#export_maps = [ "Baltic_Main", "Desert_Main", "Tiger_Main" ]
#export_maps = [ "Baltic_Main" ]
export_maps = [ "Desert_Main" ]
export_file = "C:\\temp\\UnrealPakTool\\PUBG API\\circles_%s_heatmap_comp_with_zones_w10_p4.png"
#gamemode = "competitive"

circleMatrix = CreateCircleMatrix(50) # circle radius
rowLength = len(circleMatrix)
columnLength = len(circleMatrix[0])
rowCenter = round((rowLength - 1) / 2)
columnCenter = round((columnLength - 1) / 2)

maskFilter = maskImage((8192,8192))
maskFilter.drawLine(coords = (1875,5968, 2175,6285), width = 10)
maskFilterArray = maskFilter.exportToArray()

print("\n--- EXECUTING THE SCRIPT ---\n")

assert os.path.isfile(circles_collection_json)
for i in minimaps:
    assert os.path.isfile(minimaps[i])

for export_map in export_maps:
    centerpoints = []

    print("- Reading circle collection")
    with open(circles_collection_json, "r") as json_data:
        json_data = json.load(json_data)

        match_count = 1
        match_count_max = len(json_data)
        for match in json_data:
            print_end = "\n" if match_count == match_count_max else "\r"
            print("- Reading matches: %d/%d" % (match_count, match_count_max), end=print_end)
            match_count += 1

            if not export_map == match["mapName"]:
                continue

            filterCompetitive = True # Set to True to filter only competitive matches

            filterMatch = True # Set to False to enable filtering
            filterMaskImage = False
            filterPrison = False
            filterLosHigos = False
            filterAlcantara = False
            filterCampoMilitar = False

            if filterCompetitive:
                if not "competitive" in match["matchID"]:
                    continue

            phase = 0
            for circle in match["locations"]:

                if filterMatch:
                    continue

                if filterMaskImage:

                    scaling = 1.003921567 / 100.0
                    x = round(float(circle["x"]) * scaling)
                    y = round(float(circle["y"]) * scaling)

                    if (phase == 1) and maskFilterArray[y,x]:
                        filterMatch = True

                #Prison
                if filterPrison:
                    if 0.0 < circle["x"] and circle["x"] < 170000.0:
                        if 650000.0 < circle["y"] and circle["y"] < 900000.0:
                            filterMatch = True
                    #if 185000.0 < circle["x"] and circle["x"] < 205000.0:
                    #    if 595000.0 < circle["y"] and circle["y"] < 615000.0:
                    #        validMatch = True

                if filterLosHigos:
                    if 0.0 < circle["x"] and circle["x"] < 380000.0:
                        if 710000.0 < circle["y"] and circle["y"] < 900000.0:
                            filterMatch = True

                if filterAlcantara:
                    if 0.0 < circle["x"] and circle["x"] < 80000.0:
                        if 0.0 < circle["y"] and circle["y"] < 170000.0:
                            filterMatch = True

                if filterCampoMilitar:
                    if 640000.0 < circle["x"] and circle["x"] < 800000.0:
                        if 0.0 < circle["y"] and circle["y"] < 80000.0:
                            filterMatch = True
                
                phase += 1
            
            if not filterMatch:
                continue

            phase = 0
            for circle in match["locations"]:
                if(phase == 4):
                    centerpoints.append({
                        "x": circle["x"],
                        "y": circle["y"],
                        "phase": phase
                    })
                phase += 1

    background = Image.open(minimaps[export_map])
    foreground = Image.new(mode="RGBA", size=(8192,8192), color=(255,255,255,0))
    draw = ImageDraw.Draw(foreground)

    draw_count = 1
    draw_count_max = len(centerpoints)

    # heatmap[x,y] = uint16
    heatmap = numpy.zeros((8192, 8192), dtype = numpy.uint16)

    highestHeat = [0,0,0]

    for i in centerpoints:
        print_end = "\n" if draw_count == draw_count_max else "\r"
        print("- Calculating centerpoints: %d/%d" % (draw_count, draw_count_max), end=print_end)
        draw_count += 1

        # scaling x/y coordinates
        # top left (0,0)
        # bot right (816000,816000) -> (8192,8192)
        # 8192/8160 = 1,003921568627451..
        scaling = 1.003921567 / 100.0
        x = i["x"] * scaling
        y = i["y"] * scaling
        r = 20
        phase = i["phase"]

        x = round(x)
        y = round(y)

        for row in range(rowLength):
            for column in range(columnLength): 

                rowOffset = row - rowCenter
                columnOffset = column - columnCenter

                xOffset = x + columnOffset
                yOffset = y + rowOffset

                rowValue = rowCenter + rowOffset
                columnValue = columnCenter + columnOffset

                heatmap[xOffset, yOffset] += circleMatrix[rowValue, columnValue]

    heatDistribution = []
    for x in range(8192):
        for y in range(8192):
            heatDistribution.append(heatmap[x,y])
    heatDistribution.sort(reverse = True)

    heatColor = [ 
        [ 0,    0,      0,  0   ], # index 0 unused
        [ 0,    0,    255,  128 ],
        [ 0,    128,  255,  128 ],
        [ 0,    255,  255,  128 ],
        [ 0,    255,  128,  128 ],
        [ 0,    255,    0,  128 ],
        [ 128,  255,    0,  128 ],
        [ 255,  255,    0,  128 ],
        [ 255,  128,    0,  128 ],
        [ 255,    0,    0,  128 ],
        [ 255,  255,  255,  128 ],
    ]
    heatLevels = len(heatColor) - 1
    heatFactor = heatDistribution[round(len(heatDistribution) * 0.0005)] / heatLevels # highest heat for 0.05% high
    

    draw_count = 1
    draw_count_max = 8191**2
    draw_percentage = 0
    draw_percentage_last = -1

    for x in range(8192):

        draw_percentage = math.floor(draw_count/draw_count_max * 100)

        if ( draw_percentage_last != draw_percentage ) or \
           ( draw_count == draw_count_max ) :
            draw_percentage_last = draw_percentage
            print_end = "\n" if draw_count == draw_count_max else "\r"
            print("- Drawing centerpoints: %d/%d (%d%%)" % (draw_count, draw_count_max, draw_percentage), end=print_end)

        for y in range(8192):

            draw_count += 1
            heat = heatmap[x,y]

            if heat > 0:

                heat = round(heat / heatFactor)

                if heat < 1:
                    heat = 1
                elif heat > heatLevels:
                    heat = heatLevels

                draw.point(
                    xy = [x,y],
                    fill = (heatColor[heat][0], heatColor[heat][1], heatColor[heat][2], heatColor[heat][3]), #RGBA
                )


    print("- Applying minimap")
    background.paste(foreground, (0,0), foreground)
    print("- Exporting the image")
    background.save(export_file % export_map)
    print("- Opening the export image")
    os.startfile(export_file % export_map)

print("\n\n--- SUCCESSFUL RUN ---")
