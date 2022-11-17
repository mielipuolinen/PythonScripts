from typing import *
import os
import json
import math

class telemetryFile:

    __t_matchStatistics = Dict[str, Any]
    __t_playerStatistics = Dict[str, Dict]
    __t_players = Dict[str, str]
    __t_steamIDs = List[int]


    def __init__(self, filepath: str) -> None:

        assert os.path.isfile(filepath)

        self.__filepath = filepath

        self.__s_queryMatchStatistics = False
        self.__matchStatistics: telemetryFile.__t_matchStatistics = {}

        self.__s_queryPlayerStatistics = False
        self.__playerStatistics: telemetryFile.__t_playerStatistics = {}

        self.__s_queryPlayers = False
        self.__players: telemetryFile.__t_players = {}
        self.__bots: telemetryFile.__t_players = {}
        self.__steamIDs: telemetryFile.__t_steamIDs = []

        try:
            with open(self.__filepath, "r") as file:
                self.__file = json.load(file)
        except:
            self.__file = None

        return

    def __queryMatchStatistics(self) -> None:

        try:

            # eg.: match.bro.official.pc-2018-20.steam.duo.sea.2022.11.09.22.c1e418f8-2800-4d02-988c-4b1e5874a07a
            matchIdString = self.__file[0]["MatchId"].split(".")
            gameMode = matchIdString[2]
            platform = "%s.%s" % (
                                   matchIdString[3],
                                   matchIdString[4]
                                 )
            partyMode = matchIdString[5]
            region = matchIdString[6]

            # eg.: isGame: 7.5 -> circleCount: 7
            circleCount = math.floor( self.__file[-1]["common"]["isGame"] )

            self.__matchStatistics.update({
                "matchId": self.__file[0]["MatchId"],
                "date": self.__file[0]["_D"], # eg. 2022-11-09T22:32:59.2715287Z
                "date_end": self.__file[-1]["_D"], # eg. 2022-11-09T17:48:05.857Z
                "platform": platform, # eg. pc-2018-20.steam
                "region": region, # eg. na
                "gameMode": gameMode, # eg. official
                "partyMode": partyMode, # eg. squad-fpp
                "circleCount": circleCount # eg. 7
            })

            for object in self.__file:
                if object["_T"] == "LogMatchStart":

                    self.__matchStatistics.update({
                        "mapName": object["mapName"],
                        "perspective": object["cameraViewBehaviour"],
                        "teamSize": object["teamSize"],
                        "customGame": object["isCustomGame"],
                        "eventGame": object["isEventMode"],
                        "bluezoneSettings": object["blueZoneCustomOptions"]
                    })

                    self.__matchStatistics.update({
                        "playerCount": 0,
                        "botCount": 0
                    })

                    for character in object["characters"]:
                        player = character["character"]

                        if player["accountId"][0:7] == "account":
                            self.__matchStatistics.update({
                                "playerCount": self.__matchStatistics["playerCount"] + 1
                            })
                        else:
                            self.__matchStatistics.update({
                                "botCount": self.__matchStatistics["botCount"] + 1
                            })

            self.__s_queryMatchStatistics = True

        except:
            pass

        return

    def __queryPlayers(self) -> None:

        try:

            for object in self.__file:

                if object["_T"] == "LogMatchStart":
                    for character in object["characters"]:
                        player = character["character"]

                        if player["accountId"][0:7] == "account":
                            self.__players.update({
                                player["accountId"]: player["name"]
                            })
                        else:
                            self.__bots.update({
                                player["accountId"]: player["name"]
                            })

                if object["_T"] == "LogPhaseChange":
                    for steamID in object["playersInWhiteCircle"]:
                        if not steamID in self.__steamIDs:
                            self.__steamIDs.append(steamID)
                
            else:
                self.__s_queryPlayers = True

        except:
            pass

        return

    def __queryPlayerStatistics(self) -> None:

        try:

            for object in self.__file:

                if object["_T"] == "LogPlayerPosition":
                    character = object["character"]

                    # if a first log entry for a player
                    if not character["accountId"] in self.__playerStatistics:
                        self.__playerStatistics.update({
                            character["accountId"]: {
                                "kills": 0,
                                "assists": 0,
                                "knocks": 0,
                                "damage": 0,
                                "knocked": 0,
                                "teamKills": 0,
                                "teamDamage": 0
                            } 
                        })

                    self.__playerStatistics[ character["accountId"] ].update({
                        "individualRanking": character["individualRanking"],
                        "teamRanking": character["ranking"],
                        "teamId": character["teamId"]
                    })


                if object["_T"] == "LogPlayerKillV2":
                    if object["killer"]:
                        killer = object["killer"]

                        self.__playerStatistics[ killer["accountId"] ].update({
                            "kills": self.__playerStatistics[killer["accountId"]]["kills"] + 1
                        })



                    for character in object["characters"]:
                        player = character["character"]

                        self.__players.update({
                            player["accountId"]: player["name"]
                        })

                if object["_T"] == "LogPhaseChange":
                    for steamID in object["playersInWhiteCircle"]:
                        if not steamID in self.__steamIDs:
                            self.__steamIDs.append(steamID)
                
            else:
                self.__s_queryPlayerStatistics = True

        except:
            pass

        return

    def getMatchStatistics(self) -> __t_matchStatistics:
        """Returns match statistics from a telemetry.

        Returns
        -------
        __t_matchStatistics
            Dictionary, key:value
        """
        if not self.__s_queryMatchStatistics:
            self.__queryMatchStatistics()

        return self.__matchStatistics

    def getPlayerStatistics(self, onlyRealPlayers: bool = True) -> __t_playerStatistics:
        """Returns all players statistics from a telemetry.

        Parameters
        ----------
        onlyRealPlayers : bool, optional
            Set to False to include bot players, by default True

        Returns
        -------
        __t_playerStatistics
            Dictionary, key: account id, value: dictionary of statistics
        """
        if not self.__s_queryPlayerStatistics:
            self.__queryPlayerStatistics()

        playerStatistics: telemetryFile.__t_playerStatistics = {}

        if onlyRealPlayers:
            for player in self.__playerStatistics:
                if player[0:7] == "account":
                    playerStatistics.update({ player: self.__playerStatistics[player] })
        else:
            playerStatistics = self.__playerStatistics

        return playerStatistics

    def getPlayerNames(self, onlyRealPlayers: bool = True) -> __t_players:
        """Returns all account IDs and names from a telemetry.

        Parameters
        ----------
        onlyRealPlayers : bool, optional
            Set to False to include bot players, by default True

        Returns
        -------
        __t_players
            Dictionary, key: account id, value: player name
        """
        if not self.__s_queryPlayers:
            self.__queryPlayers()

        players: telemetryFile.__t_players = self.__players

        if not onlyRealPlayers:
            players.update(self.__bots)

        return players

    def getSteamIDs(self) -> __t_steamIDs:
        """Returns all seen Steam IDs from a telemetry.
        Note: Do not expect to see all players' SteamIDs.
        SteamIDs seem to be updated only when players gets inside a white circle.

        Returns
        -------
        __t_steamIDs
            Unordered list of SteamID64s
        """
        if not self.__s_queryPlayers:
            self.__queryPlayers()

        return self.__steamIDs


def main():

    telemetryFilepath = r"C:\temp\UnrealPakTool\PUBG API\TelemetryData\c1e418f8-2800-4d02-988c-4b1e5874a07a.json"
    players = telemetryFile(telemetryFilepath).getPlayerNames()
    steamIDs = telemetryFile(telemetryFilepath).getSteamIDs()
    
    #telemetryFilepath = r"C:\temp\UnrealPakTool\PUBG API\TelemetryData\eccd9a6c-9d4e-4aac-bc1a-3a42402d7549.json"
    #players2 = telemetryFile(telemetryFilepath).getPlayerNames()

    print(players)
    #print(steamIDs)
    #print(players2)

    #stats = telemetryFile(telemetryFilepath).getMatchStatistics()
    #print(stats)

    return

if __name__ == "__main__":
    main()
