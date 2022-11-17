from concurrent.futures import ProcessPoolExecutor
import os
import json
import time

telemetries_dirpath = "C:\\temp\\UnrealPakTool\\PUBG API\\TelemetryData\\"

telemetry_file = "%s%s-telemetry.json"
export_file = "circle_collection.json"

export_mapList = [
    "Baltic_Main", # Erangel
    "Desert_Main", # Miramar
    "Tiger_Main",  # Taego
]

# not implemented
# export_circlePhases = [0,1,3,4,5,6,7,8,9,10]

ranked_circleSettings_dirpath = "C:\\temp\\UnrealPakTool\\FModel\\Output\\Exports\\" \
                              + "TslGame\\Content\\DesignData\\Bluezone\\"

ranked_circleSettings_filepaths = {
    "Baltic_Main": "%sBluezone_CR_Erangel.json" % ranked_circleSettings_dirpath,
    "Desert_Main": "%sBluezone_CR_Miramar.json" % ranked_circleSettings_dirpath,
    "Tiger_Main":  "%sBluezone_CR_Tiger.json"   % ranked_circleSettings_dirpath
}

def RetrieveFilesFromFolder(telemetries_dirpath):
    assert os.path.isdir(telemetries_dirpath)

    telemetry_json_files = []
    for file in os.listdir(telemetries_dirpath):
        filepath = os.path.join(telemetries_dirpath, file)
        
        if os.path.isfile(filepath):
            if os.path.splitext(filepath)[1] == ".json":
                telemetry_json_files.append(filepath)
    return telemetry_json_files

def ProcessTelemetry_File(telemetryFilepath):
    try:
        with open(telemetryFilepath, "r") as telemetryJSON:

            telemetry =         json.load(telemetryJSON)
            LogMatchStart_set = False
            matchID =           telemetry[0]["MatchId"]
            mapName =           ""
            customGame =        ""
            teamSize =          ""
            circleSettings =    []
            circleLocations =   []
            nextCirclePhase =   0
            lastCircleRadius =  0

            for object in telemetry:
                object_handler = ProcessTelemetry_Object( object,          matchID,          LogMatchStart_set, 
                                                          nextCirclePhase, lastCircleRadius                     )

                match object_handler:

                    # ProcessTelemetry_Object() 
                    case -1000:
                        # Unknown exception
                        return [-1000, matchID]
                    case -1001:
                        # LogMatchStart already set
                        continue
                    case -1002:
                        # Unsupported telemetry object type
                        continue

                    # ProcessTelemetry_Object_LogMatchStart()
                    case -1100:
                        # Unknown exception
                        return [-1100, matchID]
                    case -1101:
                        # This map is not in export_maplist
                        return [-1101, matchID]
                    case -1102:
                        # This telemetry has unsupported gamemode
                        return [-1102, matchID]

                    # ProcessTelemetry_Object_LogGameStatePeriodic()
                    case -1200:
                        # Unknown exception
                        return [-1200, matchID]
                    case -1201:
                        # Phase 1 is not yet available
                        continue
                    case -1202:
                        # Next phase is not yet available
                        continue

                    case _:
                        None

                # Return if unexpected type
                if not isinstance(object_handler, list):
                    return [-101, matchID]

                # Return if unexpected list structure
                if not isinstance(object_handler[0], str):
                    return [-102, matchID]

                objectType = object_handler[0]

                if objectType == "LogMatchStart":
                    # returns ["LogMatchStart", mapName, customGame, teamSize, circleSettings]
                    objectType, mapName, customGame, teamSize, circleSettings = object_handler
                    continue
                elif objectType == "LogGameStatePeriodic":
                    # returns ["LogGameStatePeriodic", circleLocation, nextCirclePhase, lastCircleRadius]
                    objectType, newCircleLocation, nextCirclePhase, lastCircleRadius = object_handler

                    circleLocations.append(newCircleLocation)
                    continue
                else:
                    # Return if unsupported objectType in list
                    return [-103, matchID]
            else:
                # Write cache if loop is finished
                TelemetryCollection = WriteCache_Telemetry( matchID,  mapName,        customGame, 
                                                            teamSize, circleSettings, circleLocations )

                # if not writeCache == 0:
                #    exit("PANIC: WriteCache_Telemetry() returned non-zero")

                # Successful run of ProcessTelemetry_File()
                return [0, matchID, TelemetryCollection]

    except:
        # Failed try-except
        return [-104, matchID]

    # Unknown exception/return
    return [-100, matchID]

def ProcessTelemetry_Object(object, matchID, LogMatchStart_set, nextCirclePhase, lastCircleRadius):
    # return error codes -1000..-1009
    try:
        if "LogMatchStart" in object["_T"]:

            if LogMatchStart_set:
                # LogMatchStart already set
                return -1001

            # returns ["LogMatchStart", mapName, customGame, teamSize, circleSettings]
            handle_LogMatchStart = ProcessTelemetry_Object_LogMatchStart(object, matchID)
            return handle_LogMatchStart

        elif "LogGameStatePeriodic" in object["_T"]:
            # returns ["LogGameStatePeriodic", circleLocation, nextCirclePhase, lastCircleRadius]
            handle_LogGameStatePeriodic = ProcessTelemetry_Object_LogGameStatePeriodic(
                                                                                object,          matchID, 
                                                                                nextCirclePhase, lastCircleRadius )
            return handle_LogGameStatePeriodic
        else:
            # Unsupported telemetry object type
            return -1002
    except:
        print( "\nProcessTelemetry_Object(): " \
             + "\nFailed processing an object:\n%s\n%s" % (object["_T"], object["_D"]) \
             + "\nMatch ID: %s" % matchID
        )
    # Unknown exception/return
    return -1000

def ProcessTelemetry_Object_LogMatchStart(object, matchID):
    # return error codes -1100..-1109
    try:
        mapName =        object["mapName"]
        customGame =     object["isCustomGame"]
        teamSize =       object["teamSize"]
        circleSettings = object["blueZoneCustomOptions"]

        if not mapName in export_mapList:
            return -1101

        # Return if unsupported gamemode
        #if not "custom" or not "competitive" in matchID:
        #    return -1102

        # Circle settings not available in Telemetry for default gamemodes
        # TODO: Multithreading doesn't work. Apply settings afterwards in another loop.
        # TODO: Normal gamemode's circle settings
        #if "competitive" in matchID:
        #    circleSettings = Get_RankedCircleSettings(mapName)

        return ["LogMatchStart", mapName, customGame, teamSize, circleSettings]

    except:
        print( "\nProcessTelemetry_Object_LogMatchStart(): " / 
             + "\nFailed processing an object:\n%s\n%s" % (object["_T"], object["_D"])
             + "\nMatch ID: %s" % matchID
        )
    # Unknown exception/return
    return -1100

def ProcessTelemetry_Object_LogGameStatePeriodic(object, matchID, nextCirclePhase, lastCircleRadius):
    # return error codes -1200..-1209
    try:
        
        x = y = z = radius = 0
        circleLocation = {}

        if nextCirclePhase == 0:
            x = object["gameState"]["safetyZonePosition"]["x"]
            y = object["gameState"]["safetyZonePosition"]["y"]
            z = object["gameState"]["safetyZonePosition"]["z"]
            radius = object["gameState"]["safetyZoneRadius"]

        if nextCirclePhase > 0:
            x = object["gameState"]["poisonGasWarningPosition"]["x"]
            y = object["gameState"]["poisonGasWarningPosition"]["y"]
            z = object["gameState"]["poisonGasWarningPosition"]["z"]
            radius = object["gameState"]["poisonGasWarningRadius"]

            # Before phase 1 is released radius is zero
            if radius == 0:
                # Phase 1 is not yet available
                return -1201

            # Set new phase data only when circle radius has updated from previous
            if lastCircleRadius == radius:
                # Next phase is not yet available
                return -1202

        circleLocation = {
            "x": x,
            "y": y,
            "z": z,
            "radius": radius
        }

        nextCirclePhase += 1
        lastCircleRadius = radius

        return ["LogGameStatePeriodic", circleLocation, nextCirclePhase, lastCircleRadius]
    except:
        print( "\nProcessTelemetry_Object_LogGameStatePeriodic(): " \
             + "\nFailed processing an object:\n%s\n%s" % (object["_T"], object["_D"]) \
             + "\nMatch ID: %s" % matchID
        )
    # Unknown exception/return
    return -1200

def Get_RankedCircleSettings(mapName):
    # [{
    #   Type, Name, Properties:{..}, 
    #   Rows:{
    #       N1:{ 
    #           StartDelay, WarningDuration, ReleaseDuration, 
    #           RadiusRate, RandomRadiusRate, 
    #           PoisonGasDPS, SpreadRatio, LandRatio, 
    #           DamageMagnifierForDistance, DamageMagnifier, DamageMagnifierCurve, 
    #           BluezoneType, CircleAlgorithm, 
    #           FastPlayerCount, FastReleaseDuration, FastWarningDuration, 
    #           bIgnoreSafetyZone
    #       },
    #       .., N10:{..}
    #   }
    # }]

    circleSettings = []
    with open(ranked_circleSettings_filepaths[mapName], "r") as circleSettings_json:
        circleSettingsFromGame = (json.load(circleSettings_json))[0]["Rows"]

        circlePhase = 1
        for circlePhaseSettings in circleSettingsFromGame:
            circlePhaseSettings = circlePhaseSettings["N%d" % circlePhase] # eg. N1

            circleSettings.append({
                "phaseNum": circlePhase,
                "startDelay": circlePhaseSettings["StartDelay"],
                "warningDuration": circlePhaseSettings["WarningDuration"],
                "releaseDuration": circlePhaseSettings["ReleaseDuration"],
                "poisonGasDamagePerSecond": circlePhaseSettings["PoisonGasDPS"],
                "radiusRate": circlePhaseSettings["RadiusRate"],
                "spreadRatio": circlePhaseSettings["SpreadRatio"],
                "circleAlgorithm": circlePhaseSettings["CircleAlgorithm"]
            })

            circlePhase += 1

    return circleSettings

def WriteCache_Telemetry(matchID, mapName, customGame, teamSize, circleSettings, circleLocations):
    
    #global TelemetryCollection
    TelemetryCollection = {
        "matchID":    matchID,
        "mapName":    mapName,
        "customGame": customGame,
        "teamSize":   teamSize,
        "settings":   circleSettings,
        "locations":  circleLocations
    }

    return TelemetryCollection

def Callback_ProcessTelemetry_File(future):

    handle = future.result()
    #print("\n %s" % handle)

    if not isinstance(handle, list):
        print("PANIC: Callback_ProcessTelemetry_File(): Handle is not a list")
        exit()

    matchID = handle[1]
    logEntry = ""

    global matchProcessCount
    matchProcessCount += 1

    match handle[0]:

        # ProcessTelemetry_File()
        case 0:
            global matchSuccessCount
            matchSuccessCount += 1

            global TelemetryCollection
            TelemetryCollection.append( handle[2] )

        case -100:
            # Unknown exception/return
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_File(): -100: Unknown exception"
        case -101:
            # Unexpected type for object_handler
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_File(): -101: Unexpected type for object_handler"
        case -102:
            # Unexpected list structure for object_handler
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_File(): -102: Unexpected list structure for object_handler"
        case -103:
            # Unsupported objectType in object_handler
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_File(): -103: Unsupported objectType in object_handler"
        case -104:
            # Failed try-except
            logEntry = "Match ID: %s" % matchID \
                     + "ProcessTelemetry_File(): -104: Failed try-except"

        # ProcessTelemetry_Object() 
        case -1000:
            # Unknown exception
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_Object(): -1000: Unknown exception"

        # ProcessTelemetry_Object_LogMatchStart()
        case -1100:
            # Unknown exception
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_Object_LogMatchStart(): -1000: Unknown exception"
        case -1101:
            # This map is not in export_maplist
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_Object_LogMatchStart(): -1101: This map is not in export_maplist"
        case -1102:
            # This telemetry has unsupported gamemode
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_Object_LogMatchStart(): -1102: This telemetry has unsupported gamemode"

        # ProcessTelemetry_Object_LogGameStatePeriodic()
        case -1200:
            # Unknown exception
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_Object_LogGameStatePeriodic(): -1200: Unknown exception"

        case _:
            # Unknown return value
            logEntry = "Match ID: %s" % matchID \
                     + "\n\tProcessTelemetry_File(): Unknown return value (%d)" % handle[0]


    if logEntry != "":
        global logEntries
        logEntries.append(logEntry)

    pass

def main():
    print("\nEXECUTING THE SCRIPT\n")
    execution_start_time = time.time()

    global TelemetryCollection
    global matchSuccessCount
    global matchProcessCount
    global logEntries

    #workerpool =          ThreadPool(32)
    telemetryFiles =      RetrieveFilesFromFolder(telemetries_dirpath)
    TelemetryCollection = []    # Appended by WriteCache_Telemetry()
    matchProcessCount =   0
    matchSuccessCount =   0     # Counted by Callback_ProcessTelemetry_File()
    matchCountMax =       len(telemetryFiles)
    logEntries =          []

    print("Processing %d matches" % matchCountMax)

    with ProcessPoolExecutor(max_workers=30) as e:

        for telemetryFile in telemetryFiles:
            future = e.submit(ProcessTelemetry_File, telemetryFile)
            future.add_done_callback(Callback_ProcessTelemetry_File)

            
            print("Processing matches: %d / %d" % (matchProcessCount, matchCountMax), end = "\r")
                
            #if matchProcessCount > 10:
            #    break

            # 0.001 - 0.1 to avoid crashing
            time.sleep(0.001)

        e.shutdown(wait=True)

    print("\nMultithreading finished")
    print("\nLog entries:")
    for logEntry in logEntries:
        print(logEntry)


    with open(export_file, "w") as file:
        TelemetryCollection = json.dumps(TelemetryCollection, indent=4)
        file.write(TelemetryCollection)

    print("\n\nMatches processed: %d / %d" % (matchProcessCount, matchCountMax))
    print("Matches exported: %d / %d" % (matchSuccessCount, matchCountMax))
    print("Export file: %s\\%s" % (os.getcwd(), export_file))

    print("\nExecution time: %.1f seconds" % (time.time() - execution_start_time))
    print("\n--- SUCCESSFUL RUN ---\n")
    return 0

if __name__ == "__main__":
    main()
