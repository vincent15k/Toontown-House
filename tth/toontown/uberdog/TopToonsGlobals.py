from toontown.quest.Quests import *

CHALLENGE_NONE = 0
CHALLENGE_COGS = 1
CHALLENGE_BLDG = 2
CHALLENGE_OFFICE = 3
CHALLENGE_FACTORY = 4
CHALLENGE_BOSS = 5

QuestList = [CogQuest, CogTrackQuest, CogLevelQuest, BuildingQuest,
             CogdoQuest, FactoryQuest]
             
if config.GetBool('want-top-toons-bosses', False):
    QuestList.extend([BossQuest, VPQuest, CFOQuest, CJQuest, CEOQuest])

class Challenge:
    def __init__(self, challengeType, quest, reward):
        self.challengeType = challengeType
        self.quest = quest
        self.reward = reward
        
    def doesCogCount(self, cog):
        return 0
        
    def doesBuildingCount(self, bldg):
        return 0
        
    def doesOfficeCount(self, office):
        return 0
        
    def doesFactoryCount(self, factory):
        return 0
        
    def doesBossCount(self, boss):
        return 0
        
    def getAmount(self):
        return self.quest.getNumQuestItems()
        
    def __repr__(self):
        return self.quest.getDefaultQuestDialog()
        
class CogChallenge(Challenge):
    def doesCogCount(self, cog):
        cog = cog.copy()
        cog['activeToons'] = [0]
        return self.quest.doesCogCount(0, cog, 0, [0])
                
class BuildingChallenge(Challenge):
    def doesBuildingCount(self, building):
        track = building['track']
        height = building['height']
        return self.quest.doesBuildingCount(0, track, height, 0, [0])
        
class OfficeChallenge(Challenge):
    def doesOfficeCount(self, office):
        return self.quest.doesOfficeCount(0, office, 0, [0])
        
class FactoryChallenge(Challenge):
    def doesFactoryCount(self, factory):
        if isinstance(self.quest, FactoryQuest) and factory == 'factory':
            return 1
            
        if isinstance(self.quest, MintQuest) and factory == 'mint':
            return 1
            
        return 0
        
class BossChallenge(Challenge):
    def doesBossCount(self, boss):
        return self.quest.doesBossCount(boss)
        
def getChallenge(seed):
    quest, challengeType, reward = generateQuest(QuestList, seed)
    
    if challengeType == CHALLENGE_COGS:
        return CogChallenge(CHALLENGE_COGS, quest, reward)
        
    elif challengeType == CHALLENGE_BLDG:
        return BuildingChallenge(CHALLENGE_BLDG, quest, reward)
        
    elif challengeType == CHALLENGE_OFFICE:
        return OfficeChallenge(CHALLENGE_OFFICE, quest, reward)
        
    elif challengeType == CHALLENGE_FACTORY:
        return FactoryChallenge(CHALLENGE_FACTORY, quest, reward)
        
    elif challengeType == CHALLENGE_BOSS:
        return BossChallenge(CHALLENGE_BOSS, quest, reward)
