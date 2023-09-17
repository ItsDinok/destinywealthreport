import requests, zipfile, os, sqlite3, json

# region Manifest Functions

def verifyManifest():
    if os.path.isfile(r"C:\\Users\\markd\\Desktop\\Misc\\manifest.pickle") == False:
        getManifest()
        return False
    else:
        return True

def getInfoOnWeapon(weaponName, data):
    weaponObject = getHashByName(weaponName)

    # TODO: assemble weapons here
    return []

def getHashByName(itemName, data):
    for itemHash, itemData in data["DestinyInventoryItemDefinition"].items():
        try:
            if itemData.get("itemName").lower() == itemName.lower():
                return data["DestinyInventoryItemDefinition"][itemHash]
        except AttributeError:
            pass

def buildDictionary(hashDictionary):
    # Connect to the manifest
    connect = sqlite3.connect(r"C:\\Users\\markd\\Desktop\\Misc\\manifest.content")
    print('Connected')

    # Create a cursor object
    cursor = connect.cursor()

    allData = {}
    # For every table name in the dictionary
    for tableName in hashDictionary.keys():
        # Get a list of all the jsons from the table
        #print(tableName)
        try:
            cursor.execute('SELECT json from ' + tableName)
        except sqlite3.OperationalError:
            cursor.execute('SELECT name FROM sqlite_schema WHERE type =\'table\'')

        #print('Generating '+ tableName +' dictionary....')

        # This returns a list of tuples: the first item in each tuple is our json
        items = cursor.fetchall()

        # Create a list of jsons
        itemJsons = [json.loads(item[0]) for item in items]

        # Create a dictionary with the hashes as keys
        # And the jsons as values
        itemDictionary = {}
        hash = hashDictionary[tableName]
        for item in itemJsons:
            itemDictionary[item[hash]] = item

        # Add that dictionary to our all_data using the name of the table
        # As a key.
        allData[tableName] = itemDictionary

    print('Dictionary Generated!')
    return allData

# Manifest hashes

hashes = {
    'DestinyActivityDefinition': 'activityHash',
    'DestinyActivityTypeDefinition': 'activityTypeHash',
    'DestinyClassDefinition': 'classHash',
    'DestinyGenderDefinition': 'genderHash',
    'DestinyInventoryBucketDefinition': 'bucketHash',
    'DestinyInventoryItemDefinition': 'itemHash',
    'DestinyProgressionDefinition': 'progressionHash',
    'DestinyRaceDefinition': 'raceHash',
    'DestinyTalentGridDefinition': 'gridHash',
    'DestinyUnlockFlagDefinition': 'flagHash',
    'DestinyHistoricalStatsDefinition': 'statId',
    'DestinyDirectorBookDefinition': 'bookHash',
    'DestinyStatDefinition': 'statHash',
    'DestinySandboxPerkDefinition': 'perkHash',
    'DestinyDestinationDefinition': 'destinationHash',
    'DestinyPlaceDefinition': 'placeHash',
    'DestinyActivityBundleDefinition': 'bundleHash',
    'DestinyStatGroupDefinition': 'statGroupHash',
    'DestinySpecialEventDefinition': 'eventHash',
    'DestinyFactionDefinition': 'factionHash',
    'DestinyVendorCategoryDefinition': 'categoryHash',
    'DestinyEnemyRaceDefinition': 'raceHash',
    'DestinyScriptedSkullDefinition': 'skullHash',
    'DestinyGrimoireCardDefinition': 'cardId'
}

hashes_trunc = {
    'DestinyInventoryItemDefinition': 'itemHash',
    'DestinyTalentGridDefinition': 'gridHash',
    'DestinyHistoricalStatsDefinition': 'statId',
    'DestinyStatDefinition': 'statHash',
    'DestinySandboxPerkDefinition': 'perkHash',
    'DestinyStatGroupDefinition': 'statGroupHash'
}

# endregion

# region Requests
baseURL = "https://www.bungie.net/Platform/Destiny2"

def getPCGRWithKey(headers, key):
    global baseURL

    searchURL = f"{baseURL}/Stats/PostGameCarnageReport/{key}/"

    response = requests.get(searchURL, headers=headers)
    return response

def getPlayerInfo(headers, id):
    global baseURL
    platform = 3

    searchURL = f"{baseURL}/{platform}/Profile/{id}/?components=200"
    response = requests.get(searchURL, headers=headers)
    # Returning -1 signifies an error has occured, it will be logged
    #print(response.text)

    if response.status_code == 200:
        playerData = response.json()
        if playerData["Response"]:
            return playerData
        else:
            print("Player not found")
            return -1
    else:
        return -1

def getManifest(headers):
    manifestURL = 'https://www.bungie.net/Platform/Destiny/Manifest/'

    # Get manifest location from json
    response = requests.get(manifestURL, headers=headers)
    manifest = response.json()
    manifestURL = 'https://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

    # Download the file, write it to 'MANZIP'
    response = requests.get(manifestURL)
    with open("MANZIP", "wb") as zip:
        zip.write(response.content)
    print("Download Complete!")

    # Extract the file contents, and rename the extracted file to 'Manifest.content'
    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'Manifest.content')
    #print('Unzipped!')[WinError 183] Cannot create a file when that file already exists: 'world_sql_content_39adcbfdc2021172e8ccf4720ca76023.content' -> 'Manifest.content'

def getActivitiesManifest(headers):
    manifestURL = "https://www.bungie.net/Platform/Destiny/Manifest/common/destiny2_content/json/en/DestinyActivityDefinition-b83e6d2c-3ddc-42b6-b434-565c3dc82769.json"
    
    # Get manifest location from json
    response = requests.get(manifestURL, headers=headers)
    manifest = response.json()
    manifestURL = "https://www.bungie.net"+manifest["Response"]["mobileWorldContentPaths"]["en"]

    # Download file and write to manzip
    response = requests.get(manifestURL)
    with open("MANZIP", "wb") as zip:
        name = zip.namelist()
        zip.write(response.content)
    os.rename(name[0], "ActivityManifest.content")
    
def getAccountIDByBungieName(bungieName, headers):
    global baseURL
    platform = 3

    searchURL = f"{baseURL}/SearchDestinyPlayer/{platform}/{bungieName}/"
    response = requests.get(searchURL, headers=headers)

    playerData = response.json()
    #print(playerData)

    # Returning -1 signifies an error has occured, it will be logged
    if response.status_code == 200:
        if playerData["Response"]:
            return playerData["Response"][0]["membershipId"]
        else:
            print("Player not found")
            return -1
    else:
        #print(response.text)
        return -1


# endregion

# region Parse functions

def discernActivityData(data):
    usefulReadableData = []
    print(len(data))

def verifyBungieName(name):
    testString = name[len(name) - 5:]
    if testString[0] == "#":
        testString = testString[4:]
        if testString.isnumeric():
            return True
        return False
    else:
        return False

def changeHashToPercentCode(name):
    newstring = ""
    for i in range(len(name)):
        if name[i] != "#":
            newstring += name[i]
        else:
            newstring += "%23"

    return newstring

# endregion