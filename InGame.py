import asyncio
import logging
import json
import threading
import requests
from datetime import datetime
import time

class VCSIngame:
    def __init__(self):
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        self.load_config()
        self.setData()  
        eventThread = threading.Thread(target=self.start)
        timeThread = threading.Thread(target=self.getTimeLive)
        goldThread = threading.Thread(target=self.getGold)
        eventThread.start()        
        timeThread.start()
        goldThread.start()

    def load_config(self):
        self.ip = self._config["OBS_IP"]        
        self.port = self._config["Ingame_Event_Port"]
        self.VmixAPI = "http://" + self._config["Vmix_IP"] + ":" + self._config["Vmix_Port"] + "/api/?Function="
        self.obsreplayurl = "http://"+self.ip+":" + self._config["Ingame_Replay_Port"]
        self.obsocrurl = "http://"+self.ip+":" + self._config["Ingame_OCR_Port"]
        self.topiconpath = self._config["Icon_Path"]
        self.timericonpath = self._config["Timer_Path"]

    def setData(self):
        self.event = None
        self.json = ""
        self.timer = 0
        # -- Timer --
        self.barontimer = 1200
        self.heraldtimer = 480
        self.dragontimer = 300
        self.rehaldicon = self.timericonpath+"Herald.png"
        self.rehaldbackground = self.timericonpath+"BG.png",
        # -- Baron Eaten --
        self.barontimeremain = 0
        self.baronteamtaken = ""
        self.baronteamname = ""
        self.goldonbaron = 0
        self.baronpowerplay = 0
        self.baronbackground = self.timericonpath+"None.png",
        # -- Dragon Eaten --
        self.eldertimeremain = 0
        self.elderteamname = ""
        self.elderbackground = self.timericonpath+"None.png",

        self.vmixfunc("SetImage","DragonTimer","DragonIcon.Source",self.timericonpath+"None.png")
        self.elderate = False
        self.gold = {"blue": 2500,"red": 2500}
        self.BlueBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0,
            "Baron": 0,
            "Dragon": 0,
            "HeraldIcon": self.topiconpath+"herald.png",
        }

        self.RedBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0,
            "Baron": 0,
            "Dragon": 0,
            "HeraldIcon": self.topiconpath+"herald.png"
        }      

        self.NumDragonBlue = 1
        self.NumDragonRed = 1
        self.BlueDragon = {
            "dragon1": self.topiconpath + "None.png",
            "dragon2": self.topiconpath + "None.png",
            "dragon3": self.topiconpath + "None.png",
            "dragon4": self.topiconpath + "None.png",
            "dragonsoul": self.topiconpath + "None.png",
        }
        self.RedDragon = {
            "dragon1": self.topiconpath + "None.png",
            "dragon2": self.topiconpath + "None.png",
            "dragon3": self.topiconpath + "None.png",
            "dragon4": self.topiconpath + "None.png",
            "dragonsoul": self.topiconpath + "None.png",
        }

    def convertLoLTime(self,sec):
        timer = ""
        m, s = divmod(sec, 60)
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
        return str(gold/1000)+"k"

    def getTimeLive(self):
        while True:
            try:
                rp = requests.get(self.obsreplayurl+"/replay/playback", verify=False, timeout=1)
            except:
                continue
            if (rp.status_code!=200):
                continue
            data = rp.json()
            self.timer = int(data["time"])
            self.parseTimeEvent()
            time.sleep(0.1)
            
    def parseTimeEvent(self):
        if (self.barontimeremain > 0):
            if (self.baronteamtaken == "Blue"):
                self.baronpowerplay = (self.gold["blue"]-self.gold["red"]) - self.goldonbaron
            elif (self.baronteamtaken == "Red"):
                self.baronpowerplay = (self.gold["red"]-self.gold["blue"]) - self.goldonbaron
        elif (self.barontimeremain <= self.timer):
            self.baronpowerplay = 0
            self.goldonbaron = 0
            self.baronteamtaken = ""
            self.baronteamname = ""
            self.baronbackground = self.timericonpath+"None.png",

        if (self.timer == 1200):
            self.heraldtimer = 0
            self.rehaldicon = self.timericonpath+"None.png"
            self.rehaldbackground = self.timericonpath+"None.png"
            self.BlueBar["HeraldIcon"] = self.topiconpath + "Baron.png"
            self.RedBar["HeraldIcon"] = self.topiconpath + "Baron.png"
            self.BlueBar["Baron"] = 0
            self.RedBar["Baron"] = 0
            
    def getGold(self):
        while True:
            try:
                rp = requests.get(self.obsocrurl+"/api/teams", verify=False, timeout=1)
            except:
                continue
            if (rp.status_code!=200):
                continue
            data = rp.json()
            if (data[0]["Gold"]-self.gold["blue"]<=3000 and data[0]["Gold"]-self.gold["blue"]>=0):
                    self.gold["blue"] = data[0]["Gold"]
            if (data[1]["Gold"]-self.gold["red"]<=3000 and data[1]["Gold"]-self.gold["red"]>=0):
                    self.gold["red"] = data[1]["Gold"]
            time.sleep(0.1)

    def start(self):
        while True:
            asyncio.run(self.process())
            time.sleep(1)

    async def process(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            print("Live Event API Connected\n")
            while not self.reader.at_eof():
                data = await self.reader.readline()
                self.parseData(data)
            try:
                self.writer.close()
                print("Live Event API Disconnected\n")
            except Exception as msg:
                #print("Live Event API Connect Error\n")
                print(msg)
                return
        except Exception as msg:
            #print(msg)
            return

            
    def parseData(self, data):
        if (data==b'}\n'):
            self.json += data.decode("utf-8")
            self.parseJSON()
            self.json = ""
        else:
            self.json += data.decode("utf-8")

    def parseJSON(self):
        try:
            self.event = json.loads(self.json)
        except Exception as msg:
            self.event = None
            #print(msg)
            return
        if (self.event["eventname"] == "OnGameStart"):
            self.setData()
        elif (self.event["eventname"] == "OnChampionKill"):
            if (self.event["sourceTeam"] == "Order"):
                self.BlueBar["Kill"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.RedBar["Kill"] += 1
        elif (self.event["eventname"] == "OnTurretDie"):
            if (self.event["sourceTeam"] == "Order"):
                self.RedBar["Turret"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.BlueBar["Turret"] += 1
        elif (self.event["eventname"] == "OnKillDragon_Spectator"): # Dragon Event
            if ((self.NumDragonBlue==4 and self.event["sourceTeam"] == "Order") or (self.NumDragonRed==4 and self.event["sourceTeam"] == "Chaos")):
                self.dragontimer = self.timer + 360
                if (not self.elderate):
                    self.vmixfunc("SetImage","DragonTimer","DragonIcon.Source",self.timericonpath+"Elder.png")
                else:
                    self.elderate = True
            elif ((self.NumDragonBlue + self.NumDragonRed)>=4):
                self.dragontimer = self.timer + 300
            else: 
                self.dragontimer = self.timer + 300
                self.vmixfunc("SetImage","DragonTimer","DragonIcon.Source",self.timericonpath+"None.png")

            if (self.event["sourceTeam"] == "Order"):
                self.BlueBar["Dragon"] += 1
                if (self.event["other"] == "SRU_Dragon_Elder"): # Elder Blue Event
                    self.eldertimeremain = self.timer + 150
                    # self.vmixfunc("OverlayInput4In","Elder Team 1")
                    return
                self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.topiconpath + self.event["other"][11:]+".png"
                if (self.NumDragonBlue==4):
                    self.BlueDragon["dragonsoul"] = self.topiconpath + self.event["other"][11:] + ".png"
                self.NumDragonBlue += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.RedBar["Dragon"] += 1
                if (self.event["other"] == "SRU_Dragon_Elder"): # Elder Red Event
                    # self.vmixfunc("OverlayInput4In","Elder Team 2")
                    return
                self.RedDragon["dragon"+str(self.NumDragonRed)] = self.topiconpath + self.event["other"][11:] + ".png"
                if (self.NumDragonRed==4):
                    self.RedDragon["dragonsoul"] = self.topiconpath + self.event["other"][11:] + ".png"
                self.NumDragonRed += 1
        elif (self.event["eventname"] == "OnKillWorm_Spectator"): #Baron Event
            self.barontimeremain = self.timer + 180
            self.baronteamname = self.event["source"].split(" ")[0]
            if (self.event["sourceTeam"] == "Order"):
                   self.BlueBar["Baron"] += 1
                   self.baronteamtaken = "Blue"
                   self.baronbackground = self.timericonpath+"Baron_BG_Blue.png"
                   self.goldonbaron = self.gold["blue"] - self.gold["red"]
                   # self.vmixfunc("OverlayInput3In","Baron Team 1")
            elif (self.event["sourceTeam"] == "Chaos"):
                   self.RedBar["Baron"] += 1
                   self.baronteamtaken = "Red"
                   self.baronbackground = self.timericonpath+"Baron_BG_Red.png"
                   self.goldonbaron = self.gold["red"] - self.gold["blue"]
                   # self.vmixfunc("OverlayInput3In","Baron Team 2")
            self.barontimer = self.timer + 360
            
        elif (self.event["eventname"] == "OnNeutralMinionKill" and self.event["other"] == "SRU_RiftHerald17.1.1"):
            if (self.event["sourceTeam"] == "Order"):
                self.BlueBar["Baron"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.RedBar["Baron"] += 1
                
            if (self.timer <= 825):
                self.heraldtimer = self.timer + 360
            else:
                self.heraldtimer = 0
                self.rehaldicon = self.timericonpath+"None.png"
                self.rehaldbackground = self.timericonpath+"None.png"

    def vmixfunc(self, func, input, selectedname = "", value = "", ):
        url = self.VmixAPI + func + "&Input=" + input + "&SelectedName=" + selectedname + "&Value=" + value 
        try:
            requests.get(url)
        except:
            pass