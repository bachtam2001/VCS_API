import websocket
import requests
import json
import threading
import logging
class VCSBanPick:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        # websocket.enableTrace(True)
        self.load_config()
        self.BanNum = 0
        self.PickNum = 0
        self.Timer = 0
        self.State = ""
        self.Ban = []
        self.Pick = []        
        self.Team = []
        self.Player = []
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
        self.ip = self._config["OBS_IP"]
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

    def on_message(self, ws, message):
        data = json.loads(message)
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
        self.Ban = []
        self.Pick = []
        self.Team = []
        self.Player = []
        self.Timer = 0
        self.State = ""
        for i in range(2):
            Team = {
                "Name":"",
                "LogoColor": str(self.LogoColor + ".png"),
                "LogoWhite": str(self.LogoWhite + ".png"),
                "LogoBlack": str(self.LogoBlack + ".png"),
            }
            self.Team.append(Team)      

        for i in range(10):
            Ban = {
                "Champion": str(self.PathS + "None.png"),
            }
            Pick = {
                "ChampionC": str(self.PathC + "None.png"),
                "ChampionL": str(self.PathL + "None.png"),
                "ChampionS": str(self.PathS + "None.png"),
            }
            Player = {
                "Name": "",
                "Image" : str(self.PathPlayerImage + "None.png"),
            }
            self.Ban.append(Ban)
            self.Pick.append(Pick)
            self.Player.append(Player)

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

    def ParsePick(self,data):
        for i in range(0,5):
            if (data["blueTeam"]["picks"] == []): break
            if (i+1<=len(data["blueTeam"]["picks"])):
                if (data["blueTeam"]["picks"][i]["isActive"]):
                    pass
                else:
                    pass
                if (data["blueTeam"]["picks"][i]["champion"]["idName"] != ""):
                    self.Pick[i]["ChampionC"] = str(self.PathC + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionL"] = str(self.PathL + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionS"] = str(self.PathS + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                else:
                    self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                    self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                    self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
            else:
                self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")

        for i in range(5,10):
            if (data["redTeam"]["picks"] == []): break
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                if (data["redTeam"]["picks"][i%5]["isActive"]):
                    pass
                else:
                    pass
                if (data["redTeam"]["picks"][i%5]["champion"]["idName"] != ""):
                    self.Pick[i]["ChampionC"] = str(self.PathC + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionL"] = str(self.PathL + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                    self.Pick[i]["ChampionS"] = str(self.PathS + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                else:
                    self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                    self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                    self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
            else:
                self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
                

    def ParsePlayerName(self,data):
        for i in range(0,5):
            if (i+1<=len(data["blueTeam"]["picks"])):
                self.Player[i]["Name"] = str(data["blueTeam"]["picks"][i]["displayName"]).split(' ')

        for i in range(5,10):
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                self.Player[i]["Name"] = str(data["redTeam"]["picks"][i%5]["displayName"]).split(' ')

        if (len(self.Player[0]["Name"])==2):
            self.Team[0]["TeamName"] = str(self.Player[0]["Name"][0])

        if (len(self.Player[5]["Name"])==2):
            self.Team[1]["TeamName"] = str(self.Player[5]["Name"][0])
                    
        for i in range(10):
            if (len(self.Player[i]["Name"])==2):
                self.Player[i]["Name"] = self.Player[i]["Name"][1]
            else:
                self.Player[i]["Name"] = self.Player[i]["Name"][0]

            self.Player[i]["Image"] = str(self.PathPlayerImage  + self.Player[i]["Name"] + ".png")

    def vmixfunc(self, func, input, selectedname = "", value = "", ):
        url = self.VmixAPI + func + "&Input=" + input + "&SelectedName=" + selectedname + "&Value=" + value 
        try:
            requests.get(url)
        except:
            pass


    def on_error(self, ws, error):
        #print("Ban Pick Websocket Connection error.")
        return

    def on_close(self, ws):
        self.ClearData()
        #print("Ban Pick Websocket Connection closed.\n")

    def on_open(self, ws):
        print("Ban Pick Websocket Connected to: " + self.ip + "\n")
