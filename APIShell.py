import APIScripts, json, requests

header  = {
    "X-API-KEY" : "7cd7a431b72d483284ca18a47f735c77"
}

"""
data = APIScripts.getPCGRWithKey(key="13624323721", headers=header)

APIScripts.discernActivityData(data=data)
print(data["Response"]["activityDetails"])
print(len(data["Response"]["activityDetails"]))
"""

# Generate dictionary to search with
# Get hash from pulled PGCR
# Search dictionary with hash to determine activity name

# dictionary = APIScripts.buildDictionary(APIScripts.hashes)
# activityHash = data["Response"]["activityDetails"]["directorActivityHash"]
# print(dictionary[activityHash])

# Get enhancement core values
name = input("Enter Bungie name: ")
# if APIScripts.verifyBungieName()
name = APIScripts.changeHashToPercentCode(name)

id = APIScripts.getAccountIDByBungieName(name, headers=header)

baseURL = "https://www.bungie.net/Platform/Destiny2"
platform = 3
searchURL = f"{baseURL}/{platform}/Profile/{id}/?components=102"
response = requests.get(searchURL, headers=header)
# Returning -1 signifies an error has occured, it will be logged
#print(response.text)

if response.status_code == 200:
    playerData = response.json()

manifestDictionary = APIScripts.buildDictionary(APIScripts.hashes)
enhancementCoreHash = APIScripts.getHashByName(itemName="Enhancement Core", data=manifestDictionary)

characterData = playerData["Response"]["profileInventory"]["data"]["items"]

coreCount = 0
coreLocations = []

for i in range(len(characterData)):
    if characterData[i]["itemHash"] == 3853748946:
        coreLocations.append(characterData[i])
        coreCount += int(characterData[i]["quantity"])

toPrint = f"Number of enhancement cores: {coreCount}"
print(toPrint)