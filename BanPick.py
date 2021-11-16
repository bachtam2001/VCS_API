import websocket
import requests
import json
import threading, time
from datetime import datetime
class VCSBanPick:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        #f = open("demofile2.txt", "a")
        self.load_config()
        self.file = open("log/banpick/" + datetime.now().strftime("%d-%m-%Y %H-%M-%S")+".log","a+")
        # websocket.enableTrace(True)
        self.BanNum = 0
        self.PickNum = 0
        self.Timer = 0
        self.Ban = []
        self.Pick = []        
        self.StateArrow = str(self.PathArrow + "Neutral.png")  
        self.TeamName = ["",""]
        self.TeamPlayer = []
        self.Active = False
        self.ClearData()
        self.connect()
        

    def connect(self):
        ws = websocket.WebSocketApp("ws://" + self.ip +":" + self.port ,
                on_open = self.on_open,
                on_message = self.on_message,
                on_error = self.on_error,
                on_close = self.on_close)
        wst = threading.Thread(target=ws.run_forever)
        wst.start() 

    def load_config(self):
        self.ip = self._config["OBS_IP"]
        self.port = self._config["Banpick_Port"]
        vmip = self._config["Vmix_IP"]
        vmport = self._config["Vmix_Port"]
        self.Url = "http://" + vmip + ":" + vmport + "/api/?Function="
        self.PathBan = self._config["Ban_Animation"]
        self.PathLine = self._config["Ban_Line"]
        self.PathArrow = self._config["State_Arrow"]
        self.PathPick = self._config["Pick_Animation"]
        self.PathC = self._config["Champ_Center"]
        self.PathL = self._config["Champ_Loading"]
        self.PathS = self._config["Champ_Square"]

    def on_message(self, ws, message):
        self.file.write(message)
        self.file.write("\n\n\n")
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
        self.ClearData()             
        self.Active = True       
        self.BanNum = 0
        self.PickNum = 0
        self.Ban[0]["Overlay"] = str(self.PathBan + "BAN00001.png")
        self.Ban[0]["Line"] =  str(self.PathLine + "Picking.png")      
        self.ClearData()

    def CSEnded(self):
        self.Active = False
        self.BanNum = 0
        self.PickNum = 0

    def ClearData(self):
        self.Ban = []
        self.Pick = []
        self.TeamName = ["",""]
        self.TeamPlayer = []
        self.Timer = 0
        self.StateArrow = str(self.PathArrow + "Neutral.png")
        for i in range(10):
            Ban = {
                "Overlay": str(self.PathBan + "None.png"),
                "Champion": str(self.PathS + "None.png"),
                "Line": str(self.PathLine + "Pick.png")
            }
            Pick = {
                "Name" : "PLAYER",
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
        if (data["state"]=="none"):
            self.Active = True
            self.ClearData()            

        if (data["state"]=="ban"):
            self.BanNum += 1
        
        if (data["state"]=="pick"):
            self.PickNum += 1
            if (self.PickNum == 9):
                self.restart_60()

    def parseState(self,data):
        if (not self.Active): return
        if (data["champSelectActive"] != True): return
        self.Timer = data["timer"]
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
            if (data["blueTeam"]["picks"][i]["isActive"]):
                self.Pick[i]["Overlay"] = str(self.PathPick + "PICK00001.png")
            else:
                self.Pick[i]["Overlay"] = str(self.PathPick + "None.png")
            if (data["blueTeam"]["picks"][i]["champion"]["idName"] != ""):
                self.Pick[i]["ChampionC"] = str(self.PathC + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_centered_splash.jpg")
                self.Pick[i]["ChampionL"] = str(self.PathL + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                self.Pick[i]["Champion"] = str(self.PathS + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
            else:
                self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")

        for i in range(5,10):
            if (data["redTeam"]["picks"] == []): break
            if (data["redTeam"]["picks"][i%5]["isActive"]):
                self.Pick[i]["Overlay"] = str(self.PathPick + "PICK00001.png")
            else:
                self.Pick[i]["Overlay"] = str(self.PathPick + "None.png")
            if (data["redTeam"]["picks"][i%5]["champion"]["idName"] != ""):
                self.Pick[i]["ChampionC"] = str(self.PathC + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_centered_splash.jpg")
                self.Pick[i]["ChampionL"] = str(self.PathL + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                self.Pick[i]["ChampionS"] = str(self.PathS + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
            else:
                self.Pick[i]["ChampionC"] = str(self.PathC + "None.png")
                self.Pick[i]["ChampionL"] = str(self.PathL + "None.png")
                self.Pick[i]["ChampionS"] = str(self.PathS + "None.png")
                
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
            self.TeamPlayer[i] = str(data["blueTeam"]["picks"][i]["displayName"]).split(' ')
            if (i==4):
                self.TeamName[0]=self.TeamPlayer[i][0]
                for i in range(0,5):
                    self.TeamPlayer[i].remove(self.TeamName[0])
                break
            if (self.TeamPlayer[i][0]!=self.TeamPlayer[i+1][0]):
                break
                    
        for i in range(5,10):
            self.TeamPlayer[i] = str(data["redTeam"]["picks"][i%5]["displayName"]).split(' ')
            if (i==9):
                self.TeamName[1]=self.TeamPlayer[i][0]
                for i in range(5,10):
                    self.TeamPlayer[i].remove(self.TeamName[1])
                break
            if (self.TeamPlayer[i][0]!=self.TeamPlayer[i+1][0]):
                break
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
        self.connect()

    def on_open(self, ws):
        print("Ban Pick Websocket Connected to: " + self.ip + "\n")
        self.file =  open(self.filename, "a+")
