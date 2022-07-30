import websocket
import requests
import json
import threading
import os
from tinydb import Query
class VCSBanPick:
    def __init__(self, database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        # websocket.enableTrace(True)
        self.load_config()
        self.db = database
        self.db_team = self.db.table("Team")
        self.db_player = self.db.table("Player")
        self.db_ban = self.db.table("Ban")
        self.db_pick = self.db.table("Pick")
        self.BanNum = 0
        self.PickNum = 0
        self.ClearData()
        bpt = threading.Thread(target=self.connect)
        bpt.start()

    def connect(self):
        while True:
            ws = websocket.WebSocketApp("ws://" + self.ip +":" + self.port ,
                    on_open = self.on_open,
                    on_message = self.on_message,
                    on_error = self.on_error,
                    on_close = self.on_close)

            ws.run_forever()
    def load_config(self):
        self.ip = self._config["OBS3_IP"]
        self.port = self._config["Banpick_Port"]
        self.VmixAPI = "http://" + self._config["Vmix_IP"] + ":" + self._config["Vmix_Port"] + "/api/?Function="
        self.TimerFormat = self._config["Timer_Format"]
        self.PathPlayerImage = self._config["Player_Image"]
        self.LogoColor = self._config["Logo_Team_Color"]
        self.LogoWhite = self._config["Logo_Team_White"]
        self.LogoBlack = self._config["Logo_Team_Black"]
        self.PathC = self._config["Champ_Center"]
        self.PathL = self._config["Champ_Loading"]
        self.PathS = self._config["Champ_Square"]
        self.PathPCBG = self._config["Player_Card_BG"]
        PlayerIMG = os.listdir(self.PathPlayerImage)
        self.AllPlayer=[x.split('.')[0].upper() for x in PlayerIMG]
        TeamIMG = os.listdir(self.LogoColor)
        self.AllTeam=[x.split('.')[0].upper() for x in TeamIMG]

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
        except:
            return
        if(data["eventType"]=="heartbeat"): return
        if(data["eventType"]=="newState"): 
            self.parseState(data["state"])
        if(data["eventType"]=="newAction"):
            self.parseAction(data["action"])
        if(data["eventType"]=="champSelectStarted"):
            self.CSStarted()
        if(data["eventType"]=="champSelectEnded"):
            self.CSEnded()

    def CSStarted(self):
        print("Ban Pick Started.\n")
        self.ClearData()
        self.BanNum = 0
        self.PickNum = 0   

    def CSEnded(self):
        print("Ban Pick Ended.\n")
        self.BanNum = 0
        self.PickNum = 0

    def ClearData(self):
        self.Ban = self.db_ban.all()
        self.Pick = self.db_pick.all()
        self.Team = self.db_team.all()
        self.Player = self.db_player.all()
        self.Timer = 0
        self.State = ""
        if (self.Team == []):
            for i in range(2):
                Team = {
                    "Name":"",
                    "LogoColor": str(self.LogoColor + ".png"),
                    "LogoWhite": str(self.LogoWhite + ".png"),
                    "LogoBlack": str(self.LogoBlack + ".png"),
                }
                self.Team.append(Team)     

        if (self.Player == []):
            for i in range(10):
                Player = {
                    "Name": "",
                    "Image" : str(self.PathPlayerImage + "None.png"),
                    "PlayerCardName": "",
                    "PlayerCardImage" : str(self.PathPlayerImage + "None.png"),
                    "PlayerCardBG": str(self.PathPCBG + "None.png")
                }
                self.Player.append(Player)

        if (self.Pick == []):
            for i in range(10):
                Pick = {
                    "ChampionC": str(self.PathC + "None.png"),
                    "ChampionL": str(self.PathL + "None.png"),
                    "ChampionS": str(self.PathS + "None.png"),
                    "ChampionSkin": str(self.PathC + "None.png")
                }
                self.Pick.append(Pick)

        if (self.Ban == []):
            for i in range(10):
                Ban = {
                    "Champion": str(self.PathS + "None.png"),
                }
                self.Ban.append(Ban)

        

    def parseAction(self,data):
        if (data["state"]=="ban"):
            self.BanNum += 1
        
        if (data["state"]=="pick"):
            self.PickNum += 1

    def parseState(self,data):
        if (data["champSelectActive"] != True): return
        self.Timer = data["timer"]
        self.State = data["state"]
        self.ParseBan(data)
        self.ParsePick(data)
        self.ParsePlayerName(data)

    def ParseBan(self,data):
        self.db_ban.truncate()
        for i in range(0,5):
            if (data["blueTeam"]["bans"] == []): break
            if (i+1<=len(data["blueTeam"]["bans"])):
                if (data["blueTeam"]["bans"][i]["champion"]["idName"] != ""):
                    self.Ban[i]["Champion"] = str(self.PathS + data["blueTeam"]["bans"][i]["champion"]["idName"] + "_0.jpg")
                else:
                    self.Ban[i]["Champion"] = str(self.PathC + "None.png")
            else:
                self.Ban[i]["Champion"] = str(self.PathC + "None.png")

        for i in range(5,10):
            if (data["redTeam"]["bans"] == []): break
            if ((i%5+1)<=len(data["redTeam"]["bans"])):
                if (data["redTeam"]["bans"][i%5]["champion"]["idName"] != ""):
                    self.Ban[i]["Champion"] = str(self.PathS + data["redTeam"]["bans"][i%5]["champion"]["idName"] + "_0.jpg")
                else:
                    self.Ban[i]["Champion"] = str(self.PathC + "None.png")
            else:
                self.Ban[i]["Champion"] = str(self.PathC + "None.png")   
        self.db_ban.insert_multiple(self.Ban)

    def ParsePick(self,data):
        self.db_pick.truncate()
        for i in range(0,5):
            if (data["blueTeam"]["picks"] == []): break
            if (data["blueTeam"]["picks"][i]["isActive"]):
                self.Player[i]["PlayerCardName"] = ""
                self.Player[i]["PlayerCardImage"] = str(self.PathPlayerImage + "None.png")
                self.Player[i]["PlayerCardBG"] = str(self.PathPCBG + "None.png")
            if (i+1<=len(data["blueTeam"]["picks"])):
                if (data["blueTeam"]["picks"][i]["champion"]["idName"] != ""):
                    self.Player[i]["PlayerCardName"] = ""
                    self.Player[i]["PlayerCardImage"] = str(self.PathPlayerImage + "None.png")
                    self.Player[i]["PlayerCardBG"] = str(self.PathPCBG + "None.png")
                    self.Pick[i]["ChampionC"] = str(self.PathC + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionL"] = str(self.PathL + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionS"] = str(self.PathS + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionSkin"] = str(self.PathC + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_" + str(data["blueTeam"]["picks"][i]["champion"]["currentSkin"]["num"])  + ".jpg")
                else:
                    if (not data["blueTeam"]["picks"][i]["isActive"]):
                        self.Player[i]["PlayerCardName"] = self.Player[i]["Name"]
                        self.Player[i]["PlayerCardImage"] = self.Player[i]["Image"]
                        self.Player[i]["PlayerCardBG"] = str(self.PathPCBG + "Blue.png")
                    self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                    self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                    self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
                    self.Pick[i]["ChampionSkin"] = str(self.PathC + "None.png")
            else:
                self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
                self.Pick[i]["ChampionSkin"] = str(self.PathC + "None.png")

        for i in range(5,10):
            if (data["redTeam"]["picks"] == []): break
            if (data["redTeam"]["picks"][i%5]["isActive"]):
                self.Player[i]["PlayerCardName"] = ""
                self.Player[i]["PlayerCardImage"] = str(self.PathPlayerImage + "None.png")
                self.Player[i]["PlayerCardBG"] = str(self.PathPCBG + "None.png")
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                if (data["redTeam"]["picks"][i%5]["champion"]["idName"] != ""):
                    self.Player[i]["PlayerCardName"] = ""
                    self.Player[i]["PlayerCardImage"] = str(self.PathPlayerImage + "None.png")
                    self.Player[i]["PlayerCardBG"] = str(self.PathPCBG + "None.png")
                    self.Pick[i]["ChampionC"] = str(self.PathC + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionL"] = str(self.PathL + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionS"] = str(self.PathS + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionSkin"] = str(self.PathC + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_" + str(data["redTeam"]["picks"][i%5]["champion"]["currentSkin"]["num"]) + ".jpg")
                else:
                    if (not data["redTeam"]["picks"][i%5]["isActive"]):
                        self.Player[i]["PlayerCardName"] = self.Player[i]["Name"]
                        self.Player[i]["PlayerCardImage"] = self.Player[i]["Image"]
                        self.Player[i]["PlayerCardBG"] = str(self.PathPCBG + "Red.png")
                    self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                    self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                    self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
                    self.Pick[i]["ChampionSkin"] = str(self.PathC + "None.png")
            else:
                self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
                self.Pick[i]["ChampionSkin"] = str(self.PathC + "None.png")
        self.db_pick.insert_multiple(self.Pick)
                

    def ParsePlayerName(self,data):
        self.db_team.truncate()
        self.db_player.truncate()
        for i in range(5):
            if (i+1<=len(data["blueTeam"]["picks"])):
                self.Player[i]["Name"] = str(data["blueTeam"]["picks"][i]["displayName"]).split(' ')

        for i in range(5,10):
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                self.Player[i]["Name"] = str(data["redTeam"]["picks"][i%5]["displayName"]).split(' ')

        for i in range(5):
            if (self.Player[i]["Name"][0] in self.AllTeam):            
                self.Team[0]["Name"] = self.Player[i]["Name"][0]
                self.Player[i]["Name"] = self.Player[i]["Name"][1:]
                self.Team[0]["LogoColor"] = self.LogoColor + self.Team[0]["Name"] + ".png"
                self.Team[0]["LogoWhite"] = self.LogoWhite + self.Team[0]["Name"] + ".png"
                self.Team[0]["LogoBlack"] = self.LogoBlack + self.Team[0]["Name"] + ".png"
            else: 
                for j in range(-1,-4,-1):
                    if (self.Player[i]["Name"][0][:j] in self.AllTeam):
                        self.Team[0]["Name"] = self.Player[i]["Name"][0][:j]
                        self.Player[i]["Name"] = self.Player[i]["Name"][1:]
                        self.Team[0]["LogoColor"] = self.LogoColor + self.Team[0]["Name"] + ".png"
                        self.Team[0]["LogoWhite"] = self.LogoWhite + self.Team[0]["Name"] + ".png"
                        self.Team[0]["LogoBlack"] = self.LogoBlack + self.Team[0]["Name"] + ".png"
                        break
        
        for i in range(5,10):
            if (self.Player[i]["Name"][0] in self.AllTeam):
                self.Team[1]["Name"] = self.Player[i]["Name"][0]
                self.Player[i]["Name"] = self.Player[i]["Name"][1:]
                self.Team[1]["LogoColor"] = self.LogoColor + self.Team[1]["Name"] + ".png"
                self.Team[1]["LogoWhite"] = self.LogoWhite + self.Team[1]["Name"] + ".png"
                self.Team[1]["LogoBlack"] = self.LogoBlack + self.Team[1]["Name"] + ".png"
            else: 
                for j in range(-1,-4,-1):
                    if (self.Player[i]["Name"][0][:j] in self.AllTeam):
                        self.Team[1]["Name"] = self.Player[i]["Name"][0][:j]
                        self.Player[i]["Name"] = self.Player[i]["Name"][1:]
                        self.Team[1]["LogoColor"] = self.LogoColor + self.Team[1]["Name"] + ".png"
                        self.Team[1]["LogoWhite"] = self.LogoWhite + self.Team[1]["Name"] + ".png"
                        self.Team[1]["LogoBlack"] = self.LogoBlack + self.Team[1]["Name"] + ".png"
                        break

        for i in range(10):
            self.Player[i]["Name"] = ' '.join(self.Player[i]["Name"])
            self.Player[i]["Name"] = self.Player[i]["Name"].strip().upper()
            tempName = self.Player[i]["Name"]
            while (not ((tempName in self.AllPlayer) or (tempName == ""))):
                tempName = tempName[:-1]
            if (tempName != ""):
                self.Player[i]["Name"] = tempName

            self.Player[i]["Image"] = str(self.PathPlayerImage  + self.Player[i]["Name"] + ".png")
        self.db_team.insert_multiple(self.Team)
        self.db_player.insert_multiple(self.Player)

    def vmixfunc(self, func, input, selectedname = "", value = "", ):
        url = self.VmixAPI + func + "&Input=" + input + "&SelectedName=" + selectedname + "&Value=" + value 
        try:
            requests.get(url)
        except:
            pass


    def on_error(self, ws, error):
        #print("Ban Pick Websocket Connection error.")
        return

    def on_close(self, ws, close_status_code, close_msg):
        self.ClearData()
        #print("Ban Pick Websocket Connection closed.\n")

    def on_open(self, ws):
        print("Ban Pick Websocket Connected to: " + self.ip + "\n")
