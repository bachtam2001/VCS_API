from ast import Return
import json
import threading
import time
import requests
from urllib3 import Retry


class VCSIngame:
    def __init__(self, database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        self.load_config()
        self.db = database
        self.setData()  
        self.OBS1_API = False
        eventThread = threading.Thread(target=self.getEvent)
        timeThread = threading.Thread(target=self.getTimeLive)
        goldThread = threading.Thread(target=self.getGold)
        eventThread.start()        
        timeThread.start()
        goldThread.start()

    def load_config(self):
        obs1_ip = self._config["OBS1_IP"] 
        obs3_ip = self._config["OBS3_IP"]        
        self.OBS1_API = self._config["OBS1_API"]        
        port = self._config["Ingame_Port"]
        self.obs1_url = "http://"+obs1_ip+":"+port+"/"
        self.obs3_url = "http://"+obs3_ip+":"+port+"/"
        self.VmixAPI = "http://" + self._config["Vmix_IP"] + ":" + self._config["Vmix_Port"] + "/api/?Function="
        self.topiconpath = self._config["Icon_Path"]
        self.timericonpath = self._config["Timer_Path"]
        self.overlaypath = self._config["Overlay_Path"]

    def setData(self):
        self.events = []
        self.timer = 0
        # -- Timer --
        self.barontimer = 1200
        self.heraldtimer = 480
        self.dragontimer = 300
        self.dragontype = self.timericonpath+"None.png"
        self.heraldicon = self.timericonpath+"Herald.png"
        self.heraldbackground = self.timericonpath+"BG.png"
        self.gold = {"blue": 2500,"red": 2500}


        self.NumDragonBlue = 1
        self.NumDragonRed = 1

    def convertLoLTime(self,sec):
        timer = ""
        m, s = divmod(int(sec), 60)
        m = int(m)
        s = int(s)
        if (m<10):
            timer += "0"
            timer += str(m)
        else:
            timer += str(m)
        timer += ":"
        if (s<10):
            timer += "0"
            timer += str(s)
        else:
            timer += str(s)
        return timer

    def convertObjectTime(self,sec):
        if (sec==0):
            return ""
        elif (sec<self.timer):
            return "LIVE"
        else:
            return self.convertLoLTime(sec-self.timer)

    def convertLoLGold(self,gold):
        return str((int(gold/100)*100)/1000)+"k"

    def getTimeLive(self):
        while True:
            try:
                rp1 = requests.get(self.obs1_url+"/Timer", verify=False, timeout=1)
            except:
                rp1 = None
            try:
                rp3 = requests.get(self.obs3_url+"/Timer", verify=False, timeout=1)
            except:
                rp3 = None
            if (rp1==None and rp3==None): continue
            if (not self.OBS1_API and rp3 == None):continue
            if (self.OBS1_API and rp1 == None):continue
            if (not self.OBS1_API):
                timer_obs3 = rp3.json()
                self.timer = timer_obs3["Time"]
                self.barontimer = timer_obs3["Baron"]
                self.heraldtimer = timer_obs3["Herald"]
                self.dragontimer = timer_obs3["Dragon"]
                self.dragontype = self.timericonpath+timer_obs3["DragonType"]+".png"
            else:
                timer_obs1 = rp1.json()
                self.timer = timer_obs1["Time"]
                self.barontimer = timer_obs1["Baron"]
                self.heraldtimer = timer_obs1["Herald"]
                self.dragontimer = timer_obs1["Dragon"]
            self.parseTimeEvent()
            time.sleep(0.1)
            
    def parseTimeEvent(self):            
        if (self.timer >= 1200):
            self.HeraldIcon = self.topiconpath + "Baron.png"
        else:
            self.HeraldIcon = self.topiconpath + "Herald.png"

        if (self.heraldtimer == 0):
            self.heraldicon = self.timericonpath+"None.png"
            self.heraldbackground = self.timericonpath+"None.png"
        else:
            self.heraldicon = self.timericonpath+"Herald.png"
            self.heraldbackground = self.timericonpath+"BG.png"

    def getGold(self):
        while True:
            try:
                rp1 = requests.get(self.obs1_url+"/Gold", verify=False, timeout=1)
            except:
                rp1 = None
            try:
                rp3 = requests.get(self.obs3_url+"/Gold", verify=False, timeout=1)
            except:
                rp3 = None
            if (rp1==None and rp3==None): continue
            if (not self.OBS1_API and rp3 == None):continue
            if (self.OBS1_API and rp1 == None):continue
            if (not self.OBS1_API):
                data = rp3.json()
                self.gold["blue"] = data["blue"]
                self.gold["red"] = data["red"]
            else:
                data = rp1.json()
                self.gold["blue"] = data["blue"]
                self.gold["red"] = data["red"]
            time.sleep(0.1)

    def getEvent(self):
        while True:
            try:
                rp1 = requests.get(self.obs1_url+"/Event", verify=False, timeout=1)
            except:
                rp1 = None
            try:
                rp3 = requests.get(self.obs3_url+"/Event", verify=False, timeout=1)
            except:
                rp3 = None
            if (rp1==None and rp3==None): continue
            if (not self.OBS1_API and rp3 == None):continue
            if (self.OBS1_API and rp1 == None):continue
            if (not self.OBS1_API):
                events = rp3.json()
                self.events = events
            else:
                events = rp1.json()
                self.events = events   
            time.sleep(0.1)

    def getScoreBar(self):
        BlueBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0,
            "Baron": 0,
            "Dragon": 0,
            "HeraldIcon": self.topiconpath + "baron.png",
            "TurretIcon": self.topiconpath + "turret.png",
            "DragonIcon": self.topiconpath + "dragon.png"
        }
        RedBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0,
            "Baron": 0,
            "Dragon": 0,
            "HeraldIcon": self.topiconpath + "baron.png",
            "TurretIcon": self.topiconpath + "turret.png",
            "DragonIcon": self.topiconpath + "dragon.png"
        }
        TurretBlue = []
        TurretRed = []
        Bounty = False
        BountyBlue = False
        BountyRed = False
        for event in self.events:
            if (event["eventname"] == "OnChampionKill"):
                if (event["sourceTeam"] == "Order"):
                    BlueBar["Kill"] += 1
                elif (event["sourceTeam"] == "Chaos"):
                    RedBar["Kill"] += 1
            elif (event["eventname"] == "OnTurretDie"):
                if (event["source"]=="Obelisk"):continue
                if (event["sourceTeam"] == "Order"):
                    if (event["source"] not in TurretRed):
                        TurretRed.append(event["source"])
                    RedBar["Turret"] = len(TurretRed)
                elif (event["sourceTeam"] == "Chaos"):
                    if (event["source"] not in TurretBlue):
                        TurretBlue.append(event["source"])
                    BlueBar["Turret"] = len(TurretBlue)
            elif (event["eventname"] == "OnKillDragon_Spectator"): # Dragon Event
                if (event["sourceTeam"] == "Order"):
                    if (event["other"] == "SRU_Dragon_Elder"): # Elder Blue Event
                        continue
                    BlueBar["Dragon"] += 1
                elif (event["sourceTeam"] == "Chaos"):
                    if (event["other"] == "SRU_Dragon_Elder"): # Elder Red Event
                        continue
                    RedBar["Dragon"] += 1
            elif (event["eventname"] == "OnKillWorm_Spectator"): #Baron Event
                if (event["sourceTeam"] == "Order"):
                    BlueBar["Baron"] += 1
                elif (event["sourceTeam"] == "Chaos"):
                    RedBar["Baron"] += 1
            elif (event["eventname"] == "OnNeutralMinionKill" and event["other"] == "SRU_RiftHerald17.1.1"):
                if (self.timer < 1200):
                    if (event["sourceTeam"] == "Order"):
                        BlueBar["Baron"] += 1
                    elif (event["sourceTeam"] == "Chaos"):
                        RedBar["Baron"] += 1
            elif (event["eventname"] == "OnObjectiveBountySoon" and event["eventTime"]+15<self.timer):
                    Bounty = True
            elif (event["eventname"] == "OnObjectiveBountyEnded" and event["eventTime"] < self.timer):
                    Bounty = False
                    
        if (Bounty):
            if (self.gold["blue"]>self.gold["red"]):
                BountyBlue = True
            else:
                BountyRed = True
                
        if (self.timer >= 1200):
            if (BountyBlue):
                BlueBar["HeraldIcon"] = self.topiconpath + "baron_bounty.png"
                RedBar["HeraldIcon"] = self.topiconpath + "baron.png"
            elif (BountyRed):
                BlueBar["HeraldIcon"] = self.topiconpath + "baron.png"
                RedBar["HeraldIcon"] = self.topiconpath + "baron_bounty.png"
            else:
                BlueBar["HeraldIcon"] = self.topiconpath + "baron.png"
                RedBar["HeraldIcon"] = self.topiconpath + "baron.png"
        else:
            if (BountyBlue):
                BlueBar["HeraldIcon"] = self.topiconpath + "herald_bounty.png"
                RedBar["HeraldIcon"] = self.topiconpath + "herald.png"
            elif (BountyRed):
                BlueBar["HeraldIcon"] = self.topiconpath + "herald.png"
                RedBar["HeraldIcon"] = self.topiconpath + "herald_bounty.png"
            else:
                BlueBar["HeraldIcon"] = self.topiconpath + "herald.png"
                RedBar["HeraldIcon"] = self.topiconpath + "herald.png"

        if (BountyBlue):
            BlueBar["DragonIcon"] = self.topiconpath + "dragon_bounty.png"
            BlueBar["TurretIcon"] = self.topiconpath + "turret_bounty.png"
        elif (BountyRed):
            RedBar["DragonIcon"] = self.topiconpath + "dragon_bounty.png"
            RedBar["TurretIcon"] = self.topiconpath + "turret_bounty.png"
            
        return BlueBar,RedBar

    def getDragon(self):
        DragonBlue = []
        DragonRed = []
        for event in self.events:
            if (event["eventname"] == "OnKillDragon_Spectator"): # Dragon Event
                if (event["sourceTeam"] == "Order"):
                    if (event["other"] == "SRU_Dragon_Elder"): # Elder Blue Event
                        continue
                    DragonBlue.append(self.timericonpath + event["other"][11:] + ".png")
                elif (event["sourceTeam"] == "Chaos"):
                    if (event["other"] == "SRU_Dragon_Elder"): # Elder Red Event
                        continue
                    DragonRed.append(self.timericonpath + event["other"][11:] + ".png")
                    
        if (len(DragonBlue) == 4):
            DragonBlue.append(DragonBlue[3])
        elif (len(DragonRed) == 4):
            DragonRed.append(DragonRed[3])

        for i in range(5):
            if (i >= len(DragonBlue)):
                DragonBlue.append(self.timericonpath + "None.png")
            if (i >= len(DragonRed)):
                DragonRed.append(self.timericonpath + "None.png")
        return DragonBlue,DragonRed
    
    def getObject(self):
        Baron = []
        Elder = []
        BaronData = {
            "TimerRemain" : 0,
            "PowerPlay" : 0,
            "GoldOnBaron" : 0,
            "TeamTaken" : 0,
            "Background" : 0,
        }
        ElderData = {
            "TimerRemain" : 0,
            "TeamTaken" : 0,
            "Background" : 0,
        }
        for event in self.events:
            if (event["eventname"] == "OnKillWorm_Spectator"):
                Baron.append(event)
            elif (event["eventname"] == "OnKillDragon_Spectator" and event["other"] == "SRU_Dragon_Elder"):
                Elder.append(event)
                
        if (len(Baron) == 0):
            BaronData["TimerRemain"] = 0
            BaronData["PowerPlay"] = 0
            BaronData["GoldOnBaron"] = 0
            BaronData["TeamTaken"] = ""
            BaronData["Background"] = self.timericonpath+"None.png"
        elif (Baron[-1]["eventTime"]+180>self.timer):
            BaronData["TimerRemain"] = Baron[-1]["eventTime"] + 180
            BaronData["GoldOnBaron"] = Baron[-1]["gold@team"]
            BaronData["TeamTaken"] = ("Blue" if Baron[-1]["sourceTeam"] == "Order" else "Red")
            BaronData["Background"] = self.timericonpath+"Baron_BG_" + BaronData["TeamTaken"] + ".png"
            if (BaronData["TeamTaken"] == "Blue"):
                BaronData["PowerPlay"] = (self.gold["blue"]-self.gold["red"]) - BaronData["GoldOnBaron"]
            elif (BaronData["TeamTaken"] == "Red"):
                BaronData["PowerPlay"] = (self.gold["red"]-self.gold["blue"]) - BaronData["GoldOnBaron"]
        else:
            BaronData["TimerRemain"] = 0
            BaronData["PowerPlay"] = 0
            BaronData["GoldOnBaron"] = 0
            BaronData["TeamTaken"] = ""
            BaronData["Background"] = self.timericonpath+"None.png"
        
        if (len(Elder) == 0):
            ElderData["TimerRemain"] = 0
            ElderData["TeamTaken"] = ""
            ElderData["Background"] = self.timericonpath+"None.png"
        elif (Elder[-1]["eventTime"]+150>self.timer):
            ElderData["TimerRemain"] = Elder[-1]["eventTime"] + 150
            ElderData["TeamTaken"] = ("Blue" if Elder[-1]["sourceTeam"] == "Order" else "Red")
            ElderData["Background"] = self.timericonpath+"Dragon_BG_" + ElderData["TeamTaken"] + ".png"
        else:
            ElderData["TimerRemain"] = 0
            ElderData["TeamTaken"] = ""
            ElderData["Background"] = self.timericonpath+"None.png"
        return BaronData, ElderData
    
    def getOverlay(self):
        Ace = []
        Data = {
            "Ace": self.overlaypath + "None.png",
        }
        for event in self.events:
            if (event["eventname"] == "OnAce"):
                Ace.append(event)
        if (len(Ace) == 0):
            return Data
        elif (Ace[-1]["eventTime"]+10>self.timer and Ace[-1]["eventTime"]<self.timer):
            Data["Ace"] = self.overlaypath + "ace00001.png"
            return Data
        else:
            return Data
                
    def vmixfunc(self, func, input, selectedname = "", value = "", ):
        url = self.VmixAPI + func + "&Input=" + input + "&SelectedName=" + selectedname + "&Value=" + value 
        try:
            requests.get(url)
        except:
            pass
