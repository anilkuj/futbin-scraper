import requests
import bs4
import pandas as pd



# Fixa spelarnamn
res = requests.get('https://www.futbin.com/19/players?page=1&player_rating=74-99')
soup = bs4.BeautifulSoup(res.text, features='lxml')

# ta fram namn
names = soup.select('td > div > div > a')

# ta fram antal sidor
pages = soup.select('.page-link')

# räkna fram hur många sidor som ska gås igenom
sistaSidan = (len(pages))
antalSidor = pages[sistaSidan-2].get_text()

# initiera lista med alla namn
listName = []
listLink = []

# spara namn och fullständig länk till lista
for name in names:
    name = name.get_text()
    listName.append(name)

for name in names:
    link = name.get('href')
    link = "https://www.futbin.com" + link
    listLink.append(link)
    
############

############

# ta fram namn för resterande sidor på hemsidan
for page in range(int(antalSidor)):
    print(f"{page+1}/{int(antalSidor)-1}")
    # Fixa spelarnamn
    res = requests.get(f'https://www.futbin.com/19/players?page={page+2}&player_rating=74-99')
    soup = bs4.BeautifulSoup(res.text, features='lxml')

    # ta fram namn
    names = soup.select('td > div > div > a')
    
    # spara namn och fullständig länk till lista
    for name in names:
        name = name.get_text()
        listName.append(name)

    for name in names:
        link = name.get('href')
        link = "https://www.futbin.com" + link
        listLink.append(link)
    

############

# init databas
database = {}

# Fixa så att alla spelarstats sparas
playerCounter = 0
for links in listLink:
    # FIXA VARJE SPELARES STATS
    res = requests.get(links)
    soup = bs4.BeautifulSoup(res.content, features='lxml')
    
    # spara ner stats och vad det är för stats
    stats = soup.select('.stat_val')
    statText = soup.select('div.stat_holder_sub.left_stat_name > span')
    
    # ID
    IDtext = soup.select('#page-data')
    spelarID = IDtext[0].get('data-player-id').strip()
    
    # INFO
    infoStats = soup.select('.table-row-text')
    infoText = soup.select('tr > th')
    
    # Header name
    hName = soup.select('.header_name')
    headerName = hName[0].getText().strip()
    
    # förklarar vart i processen det är
    print(str(playerCounter+1) + "/" + str(len(listLink)), end=": ") 
    print(headerName)

    # lägg alla stats i en dict
    tempStats = {}
    
    # lägg info i en temporär dict
    statsCounter = 0
    for i in infoText:
        namnPåInfo = i.getText().strip()
        värdePåInfo = infoStats[statsCounter].getText().strip()
        
        # visa endast cm på längd
        if namnPåInfo == "Height":
            värdePåInfo = värdePåInfo[:3]
        
        # lägg till i tempStats
        tempStats.update({namnPåInfo : värdePåInfo})
        statsCounter += 1
    
    # lägg stats, headerName och ID i samma temporära dict
    counter = 0
    for i in statText:
        namnPåStats = (i.getText().strip())
        värdePåStats = (stats[counter].getText().strip())
        tempStats.update({namnPåStats : värdePåStats, "ID" : spelarID, "Header Name": headerName})
        counter += 1

    # uppdatera databasen för spelaren
    database.update({tempStats['ID'] : tempStats})
    playerCounter += 1
    
############
# skriv till excel

df = pd.DataFrame(database).T
df.to_excel('Futbin - FIFA 19.xlsx')

input("Klar ")
