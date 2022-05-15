import websocket
import requests
import json
import threading
class VCSBanPick:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        #f = open("demofile2.txt", "a")
        # websocket.enableTrace(True)
        self.load_config()
        self.BanNum = 0
        self.PickNum = 0
        self.Timer = 0
        self.State = ""
        self.Ban = []
        self.Pick = []        
        self.StateArrow = str(self.PathArrow + "Neutral.png")  
        self.TeamName = ["",""]
        self.TeamPlayer = []
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
        vmip = self._config["Vmix_IP"]
        vmport = self._config["Vmix_Port"]
        self.Url = "http://" + vmip + ":" + vmport + "/api/?Function="
        self.TimerFormat = self._config["Timer_Format"]
        self.PathBan = self._config["Ban_Animation"]
        self.PathLine = self._config["Ban_Line"]
        self.PathArrow = self._config["State_Arrow"]
        self.PathPick = self._config["Pick_Animation"]
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
        self.file.write(message)
        self.file.write("\n\n")

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
        self.TeamName = ["",""]
        self.TeamPlayer = []
        self.Timer = 0
        self.State = ""
        self.StateArrow = str(self.PathArrow + "Neutral.png")
        for i in range(10):
            Ban = {
                "Overlay": str(self.PathBan + "None.png"),
                "Champion": str(self.PathS + "None.png"),
                "Line": str(self.PathLine + "Pick.png")
            }
            Pick = {
                "Overlay": str(self.PathPick + "None.png"),
                "ChampionC": str(self.PathC + "None.png"),
                "ChampionL": str(self.PathL + "None.png"),
                "ChampionS": str(self.PathS + "None.png"),
            }
            Name = ""
            self.Ban.append(Ban)
            self.Pick.append(Pick)
            self.TeamPlayer.append(Name)

    def parseAction(self,data):
        self.restart_30()      

        if (data["state"]=="ban"):
            self.BanNum += 1
        
        if (data["state"]=="pick"):
            self.PickNum += 1
            #print(self.PickNum)
            if (self.PickNum == 10):
                self.restart_60()

    def parseState(self,data):
        if (data["champSelectActive"] != True): return
        self.Timer = data["timer"]
        self.State = data["state"]
        self.ParseArrow(data)
        self.ParseBan(data)
        self.ParsePick(data)
        self.ParsePlayerName(data)

    def ParseBan(self,data):
        for i in range(0,5):
            if (data["blueTeam"]["bans"] == []): break
            if (i+1<=len(data["blueTeam"]["bans"])):
                if (data["blueTeam"]["bans"][i]["isActive"]):
                    self.Ban[i]["Overlay"] = str(self.PathBan + "BAN00001.png")
                    self.Ban[i]["Line"]  = str(self.PathLine + "Picking.png")
                else:
                    self.Ban[i]["Overlay"] = str(self.PathBan + "None.png")
                    self.Ban[i]["Line"]  = str(self.PathLine + "Picked.png")
                if (data["blueTeam"]["bans"][i]["champion"]["idName"] != ""):
                    self.Ban[i]["Champion"] = str(self.PathS + data["blueTeam"]["bans"][i]["champion"]["idName"] + "_0.jpg")
                else:
                    self.Ban[i]["Champion"] = str(self.PathC + "None.png")
            else:
                self.Ban[i]["Champion"] = str(self.PathC + "None.png")
                self.Ban[i]["Overlay"] = str(self.PathBan + "None.png")
                self.Ban[i]["Line"] =  str(self.PathLine + "Pick.png")

        for i in range(5,10):
            if (data["redTeam"]["bans"] == []): break
            if ((i%5+1)<=len(data["redTeam"]["bans"])):
                if (data["redTeam"]["bans"][i%5]["isActive"]):
                    self.Ban[i]["Overlay"] = str(self.PathBan + "BAN00001.png")
                    self.Ban[i]["Line"]  = str(self.PathLine + "Picking.png")
                else:
                    self.Ban[i]["Overlay"] = str(self.PathBan + "None.png")
                    self.Ban[i]["Line"]  = str(self.PathLine + "Picked.png")
                if (data["redTeam"]["bans"][i%5]["champion"]["idName"] != ""):
                    self.Ban[i]["Champion"] = str(self.PathS + data["redTeam"]["bans"][i%5]["champion"]["idName"] + "_0.jpg")
                else:
                    self.Ban[i]["Champion"] = str(self.PathC + "None.png")
            else:
                self.Ban[i]["Champion"] = str(self.PathC + "None.png")
                self.Ban[i]["Overlay"] = str(self.PathBan + "None.png")
                self.Ban[i]["Line"] =  str(self.PathLine + "Pick.png")

    def ParsePick(self,data):
        for i in range(0,5):
            if (data["blueTeam"]["picks"] == []): break
            if (i+1<=len(data["blueTeam"]["picks"])):
                if (data["blueTeam"]["picks"][i]["isActive"]):
                    self.Pick[i]["Overlay"] = str(self.PathPick + "PICK00001.png")
                else:
                    self.Pick[i]["Overlay"] = str(self.PathPick + "None.png")
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
                self.Pick[i]["Overlay"] = str(self.PathPick + "None.png")

        for i in range(5,10):
            if (data["redTeam"]["picks"] == []): break
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                if (data["redTeam"]["picks"][i%5]["isActive"]):
                    self.Pick[i]["Overlay"] = str(self.PathPick + "PICK00001.png")
                else:
                    self.Pick[i]["Overlay"] = str(self.PathPick + "None.png")
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
                self.Pick[i]["Overlay"] = str(self.PathPick + "None.png")
                
    def ParseArrow(self, data):
        if (data["blueTeam"]["isActive"]==True and data["redTeam"]["isActive"]==True):
            self.StateArrow = str(self.PathArrow + "Neutral.png")        
        elif (data["blueTeam"]["isActive"]==True):
            self.StateArrow = str(self.PathArrow + "Blue.png")
        elif (data["redTeam"]["isActive"]==True):
            self.StateArrow = str(self.PathArrow + "Red.png")
        else:
            self.StateArrow = str(self.PathArrow + "Neutral.png")

    def ParsePlayerName(self,data):
        for i in range(0,5):
            if (i+1<=len(data["blueTeam"]["picks"])):
                self.TeamPlayer[i] = str(data["blueTeam"]["picks"][i]["displayName"]).split(' ')
        for i in range(5,10):
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                self.TeamPlayer[i] = str(data["redTeam"]["picks"][i%5]["displayName"]).split(' ')

        for i in range(0,5):
            if (i+1<=len(data["blueTeam"]["picks"])):
                if (i==4):
                    self.TeamName[0]=self.TeamPlayer[i][0]
                    for i in range(0,5):
                        self.TeamPlayer[i].pop(0)
                    break
                if (self.TeamPlayer[0][0]!=self.TeamPlayer[i][0]):
                    break
                    
        for i in range(5,10):
            if ((i%5+1)<=len(data["redTeam"]["picks"])):
                if (i==9):
                    self.TeamName[1]=self.TeamPlayer[i][0]
                    for i in range(5,10):
                        self.TeamPlayer[i].pop(0)
                    break
                if (self.TeamPlayer[5][0]!=self.TeamPlayer[i][0]):
                    break
                    
        #print(self.TeamPlayer)
        for i in range(10):
            self.TeamPlayer[i] = ' '.join(self.TeamPlayer[i])

    def restart_30(self):
        self.vmixfunc("Play","Timer30")
        self.vmixfunc("Restart","Timer30")

    def vmixfunc(self,func,input):
        url = self.Url + func + "&Input=" + input
        try:
            requests.get(url)
        except:
            pass

    def restart_60(self):
        self.vmixfunc("Play","Timer60")
        self.vmixfunc("Restart","Timer60")
        #self.vmixfunc("OverlayInput2In","Timer60")

    def on_error(self, ws, error):
        #print("Ban Pick Websocket Connection error.")
        return

    def on_close(self, ws):
        self.ClearData()
        #print("Ban Pick Websocket Connection closed.\n")

    def on_open(self, ws):
        print("Ban Pick Websocket Connected to: " + self.ip + "\n")
        self.file =  open(self.filename, "a+")
