import requests, discord, asyncio, datetime
from discord.ext import commands

#
#
#

# discord bot token
botToken = ""

# riotApi to use Riot Developer APIs
riotAPI = ""

# list of summoners to monitor TFT ranked data
watchedSummoners = ["DRAGON PULSE","Amumu Main","Randomdude2468"]

# discord channel to get notications
channelId = ""

#
#
#

bot = commands.Bot(command_prefix='!')
watchedSummonerData = {}
tftLp = {}
latestVersion = requests.get("https://ddragon.leagueoflegends.com/realms/na.json").json()["v"]

def getSummoner(summonerName):
    return requests.get("https://na1.api.riotgames.com/tft/summoner/v1/summoners/by-name/"+ summonerName + "?api_key=" + riotAPI,timeout=10).json()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="TFT Monitor", url='https://www.twitch.tv/muffincheez'))
    print('=> Logged in as {0.user}'.format(bot))

# store summoner data
print("[PENGU] Pulling summoner data of " + str(len(watchedSummoners)) + " players ...")
for x in watchedSummoners:
    tftLp[x] = {}
    summonerData = getSummoner(x)
    watchedSummonerData[x] = {"id":summonerData["id"],"accountId":summonerData["accountId"],"puuid":summonerData["puuid"],"name":summonerData["name"],"profileIconId":summonerData["profileIconId"],"summonerLevel":summonerData["summonerLevel"]}
print("[PENGU] Finished pulling summoner data of " + str(len(watchedSummoners)) + " players ...")

async def background_task():
    await bot.wait_until_ready()

    print("[PENGU] Beginning rank monitoring for " + str(len(watchedSummoners)) + " players.")
    while(True):
        for summoner in watchedSummoners:
            summonerData = watchedSummonerData[summoner]
            if "name" in summonerData:
                await checkLp(summonerData)
            await asyncio.sleep(5)
        print(tftLp)
        await asyncio.sleep(20)

async def checkLp(summoner):
    tftData = requests.get("https://na1.api.riotgames.com/tft/league/v1/entries/by-summoner/" + summoner["id"]+ "?api_key=" + riotAPI,timeout=10).json()

    for league in tftData:
        queueType = league["queueType"].replace("_"," ").replace("SR","").replace("5x5","")
        currentLp = league["leaguePoints"]
        currentRank = league["tier"] + " " + league["rank"]

        rankIcons = {"IRON":"https://static.wikia.nocookie.net/leagueoflegends/images/f/fe/Season_2022_-_Iron.png","BRONZE":"https://static.wikia.nocookie.net/leagueoflegends/images/e/e9/Season_2022_-_Bronze.png","SILVER":"https://static.wikia.nocookie.net/leagueoflegends/images/4/44/Season_2022_-_Silver.png","GOLD":"https://static.wikia.nocookie.net/leagueoflegends/images/8/8d/Season_2022_-_Gold.png","PLATINUM":"https://static.wikia.nocookie.net/leagueoflegends/images/3/3b/Season_2022_-_Platinum.png","DIAMOND":"https://static.wikia.nocookie.net/leagueoflegends/images/e/ee/Season_2022_-_Diamond.png","MASTER":"https://static.wikia.nocookie.net/leagueoflegends/images/e/eb/Season_2022_-_Master.png","GRANDMASTER":"https://static.wikia.nocookie.net/leagueoflegends/images/f/fc/Season_2022_-_Grandmaster.png","CHALLENGER":"https://static.wikia.nocookie.net/leagueoflegends/images/0/02/Season_2022_-_Challenger.png"}

        try:
            # if rank changed
            if tftLp[summoner["name"]][queueType]["rank"] != currentRank:
                print(summoner["name"] + " rank update: " + tftLp[summoner["name"]][queueType]["rank"] + " --> " + currentRank)
                embed=discord.Embed(timestamp=datetime.datetime.utcnow(), color=0xff00ff)
                embed.set_author(name="🚨 " + summoner.upper() + " TFT RANK UPDATE 🚨",icon_url="https://ddragon.leagueoflegends.com/cdn/" + latestVersion + "/img/profileicon/" + str(summoner["profileIconId"]) + ".png")
                embed.add_field(name=queueType,value=tftLp[summoner][queueType]["rank"] + " **----->** " + currentRank)
                embed.set_footer(text="powered by shdw 👻",icon_url="https://i.imgur.com/ri6NrsN.png")
                embed.set_image(url=rankIcons[league["tier"]])
                await bot.get_channel(int(channelId)).send(embed=embed)

            # if GAINED lp
            elif tftLp[summoner["name"]][queueType]["leaguePoints"] < currentLp:
                print(summoner["name"] + " gained " + str(currentLp - tftLp[summoner["name"]][queueType]["leaguePoints"]) + "LP!")
                embed=discord.Embed(description="**+" + str(currentLp - tftLp[summoner["name"]][queueType]["leaguePoints"]) + "** LP in " + queueType,timestamp=datetime.datetime.utcnow(), color=0x62C979)
                embed.set_author(name="🚨 " + summoner.upper() + " TFT LP UPDATE 🚨",icon_url="https://ddragon.leagueoflegends.com/cdn/" + latestVersion + "/img/profileicon/" + str(summoner["profileIconId"]) + ".png")
                embed.add_field(name=queueType,value=currentRank + " - " + str(currentLp) + " LP")
                embed.set_footer(text="powered by shdw 👻",icon_url="https://i.imgur.com/ri6NrsN.png")
                embed.set_thumbnail(url="https://i.imgur.com/0m1B3Et.png")
                await bot.get_channel(int(channelId)).send(embed=embed)

            # if LOST lp
            elif tftLp[summoner["name"]][queueType]["leaguePoints"] > currentLp:
                print(summoner["name"] + " lost " + str(tftLp[summoner["name"]][queueType]["leaguePoints"] - currentLp) + "LP!")
                embed=discord.Embed(description="*-" + str(tftLp[summoner["name"]][queueType]["leaguePoints"] - currentLp) + "* LP in " + queueType,timestamp=datetime.datetime.utcnow(), color=0xE7548C)
                embed.set_author(name="🚨 " + summoner.upper() + " TFT LP UPDATE 🚨",icon_url="https://ddragon.leagueoflegends.com/cdn/" + latestVersion + "/img/profileicon/" + str(summoner["profileIconId"]) + ".png")
                embed.add_field(name=queueType,value=currentRank + " - " + str(currentLp) + " LP")
                embed.set_footer(text="powered by shdw 👻",icon_url="https://i.imgur.com/ri6NrsN.png")
                embed.set_thumbnail(url="https://i.imgur.com/bTORHF3.png")
                await bot.get_channel(int(channelId)).send(embed=embed)

        except Exception as e:
            #print(e)
            pass

        tftLp[summoner["name"]][queueType] = {"leaguePoints":currentLp,"rank":currentRank}

bot.loop.create_task(background_task())
bot.run(botToken)
