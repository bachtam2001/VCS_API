import json
import requests
import time
import threading
class VCSTimer:
    def __init__(self):
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        self.load_config()
        self.live = ""
        self.dragon = {"timer": "", "type": "None"}
        self.baron = {"timer": ""}
        self.gold = {"blue": "2.5k","red":"2.5k"}
        self.crawlData()
        
    def load_config(self):
        self.ip = self._config["OBS_IP"]
        self.url = "http://"+self.ip+":"
        self.replay = self._config["Ingame_Replay_Port"]
        self.ocr = self._config["Ingame_OCR_Port"]
        self.dragonpath = self._config["Dragon_Path"]
    
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
        
    def getTimeLive(self):
        while True:
            try:
                rp = requests.get(self.url+self.replay+"/replay/playback", verify=False, timeout=1)
            except:
                self.live = "00:00"
                #print("Refresh Game Time Failed.\n")
                continue
            if (rp.status_code!=200):
                continue
            data = rp.json() 
            self.live = self.convertLoLTime(data["time"])
        
    def getGold(self):
        while True:
            try:
                rp = requests.get(self.url+self.ocr+"/api/teams", verify=False, timeout=1)
            except:
                self.gold = {"blue": "2.5k","red":"2.5k"}
                #print("Refresh Gold Failed.\n")
                continue
            if (rp.status_code!=200):
                continue
            data = rp.json() 
            self.gold["blue"] = str(data[0]["Gold"]/1000)+"k"
            self.gold["red"] = str(data[1]["Gold"]/1000)+"k"
            time.sleep(0.5)
        
    def getTimeObject(self):
        while True:
            try:
                rp = requests.get(self.url+self.ocr+"/api/objectives", verify=False, timeout=1)
            except:
                self.dragon = {"timer": "00:00", "type": self.dragonpath + "None.PNG" }
                self.baron = {"timer": "00:00"}
                #print("Refresh Object Timer Failed.\n")
                continue
            if (rp.status_code!=200):
                continue
            data = rp.json()
            if (data[0]["Cooldown"] <= 1000):
                if (data[0]["IsAlive"]):
                    self.dragon["timer"] = "LIVE"
                else:
                    self.dragon["timer"] = self.convertLoLTime(data[0]["Cooldown"])
            if (data[0]["Type"]!=None):
                self.dragon["type"] = self.dragonpath + str(data[0]["Type"]) + ".PNG"
            else:
                self.dragon["type"] = self.dragonpath + "None.PNG"
            if (data[1]["Cooldown"] <= 1000):            
                if (data[1]["IsAlive"]):
                    self.baron["timer"] = "LIVE"
                else:
                    self.baron["timer"] = self.convertLoLTime(data[1]["Cooldown"])
            time.sleep(0.5)
            
    def crawlData(self):
        Timer1 = threading.Thread(target=self.getTimeLive)
        Timer2 = threading.Thread(target=self.getGold)
        Timer3 = threading.Thread(target=self.getTimeObject)
        Timer1.start()
        Timer2.start()
        Timer3.start()