import requests
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from datetime import datetime, date

load_dotenv()
types = {
    "Food":"fbfe2eea-aa2b-442f-9966-fefcf970ecd5"
}
header = {
    "Authorization": "Bearer " + str(os.getenv("NOTION_AUTH")),
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_weeklyDB():
    url = "https://api.notion.com/v1/databases/" + str(os.getenv("WEEKLY_DB"))+"/query"
    payload = { "page_size": 100 }
    response = requests.post(url, json=payload, headers=header)
    return response.json()

def get_monthlyDB(id):
    url = "https://api.notion.com/v1/databases/" + str(id)+"/query"
    payload = { "page_size": 100 }
    response = requests.post(url, json=payload, headers=header)
    return response.json()

class expense:
  def __init__(self, name, cost, date, catergory, id):
    self.name = name
    self.cost = cost
    self.date = date
    self.catergory = catergory
    self.id = id

class month:
  def __init__(self,id):
    self.id = id
    self.food = []
    self.drink = []
    self.dis = []
    self.clothes = []
    self.travel = []
    self.other = []
    self.rent = []
    #self.categories = [self.food,self.drink,self.dis,self.clothes,self.travel,self.other]

def categorise(expense,month):
    match expense.catergory:
        case "Food":    
            month.food.append(expense)
        case "Drink":
            month.drink.append(expense)
        case "Discretionary":
            month.dis.append(expense)
        case "Clothes":
            month.clothes.append(expense)
        case "Travel":
            month.travel.append(expense)
        case "Other":
            month.other.append(expense)
        case "Rent":
            month.rent.append(expense)


def monthIt():
    jul23 = month(os.getenv("JULY_DB"))
    aug23 = month(os.getenv("AUG_DB"))
    sep23 = month(os.getenv("SEPT_DB"))
    oct23 = month(os.getenv("OCT_DB"))
    nov23 = month(os.getenv("NOV_DB"))
    dec23 = month(os.getenv("DEC_DB"))
    jun23 = month(0)

    months23 = [jun23,jul23,aug23,sep23,oct23,nov23,dec23]

    for i in db:
        if i.date < "2023-07-01":
            categorise(i,months23[0])
        elif i.date < "2023-08-01":
            categorise(i,months23[1])
        elif i.date < "2023-09-01":
            categorise(i,months23[2])
        elif i.date < "2023-10-01":
            categorise(i,months23[3])
        elif i.date < "2023-11-01":
            categorise(i,months23[4])
        elif i.date < "2023-12-01":
            categorise(i,months23[5])
        elif i.date < "2024-01-01":
            categorise(i,months23[6])

    return months23


def currentMonth(months):
    if date.today() < date(2023,7,1):
        return months[0]
    elif date.today() < date(2023,8,1):
        return months[1]
    elif date.today() < date(2023,9,1):
        return months[2]
    elif date.today() < date(2023,10,1):
        return months[3]
    elif date.today() < date(2023,11,1):
        return months[4]
    elif date.today() < date(2023,12,1):
        return months[5]
    elif date.today() < date(2024,1,1):
        return months[6]


def makeGraph(month):
    foodCost = sum(i.cost for i in month.food)
    drinkCost = sum(i.cost for i in month.drink)
    disCost = sum(i.cost for i in month.dis)
    clothesCost = sum(i.cost for i in month.clothes)
    travelCost = sum(i.cost for i in month.travel)
    otherCost = sum(i.cost for i in month.other)
    rentCost = sum(i.cost for i in month.rent)


    labels = ['Food', 'Drink', 'Discretionary', 'Clothes', 'Travel','Other','Rent']
    values = [foodCost, drinkCost, disCost, clothesCost, travelCost, otherCost, rentCost]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values,hole=.3)])
    #fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20)
    fig.show()
    #fig.write_html("graphs/pie.html")
    fig.write_image("graphs/pie.svg")


db= []
save = get_weeklyDB()
for i in save["results"]:
    if i["properties"]["Name"]["title"]:
       db.append(expense(i["properties"]["Name"]["title"][0]["text"]["content"],i["properties"]["Amount"]["number"],i["properties"]["Date"]['date']['start'],i["properties"]["Catergory"]["select"]["name"],i["id"]))
    else:
        break

months = monthIt()
current = currentMonth(months)
#makeGraph(current)

save = get_monthlyDB(current.id)



pageIDs = []
#["properties"]["Name"]["title"]

#for category in save["results"]:
#    for i in category["properties"]["Weekly Expenses"]["relation"]:
#        pageIDs.append(i["id"])

#get category page ids:
for i in save["results"]:
        if i["properties"]["Name"]["title"]:
            pageIDs.append([i["properties"]["Name"]["title"][0]["text"]["content"],i["id"]])

print(pageIDs)


def update_page(page_id: str, category: str, month: month):
    url = f"https://api.notion.com/v1/pages/{page_id}"
     
    match category:
        case "Food":    
            cost = sum(i.cost for i in month.food)
            relation = [{"id":i.id} for i in month.food]
        case "Drink":
            cost = sum(i.cost for i in month.drink)
            relation = [{"id":i.id} for i in month.drink]
        case "Discretionary":
            cost = sum(i.cost for i in month.dis)
            relation = [{"id":i.id} for i in month.dis]
        case "Clothes":
            cost = sum(i.cost for i in month.clothes)
            relation = [{"id":i.id} for i in month.clothes]
        case "Travel":
            cost = sum(i.cost for i in month.travel)
            relation = [{"id":i.id} for i in month.travel]
        case "Other":
            cost = sum(i.cost for i in month.other)
            relation = [{"id":i.id} for i in month.other]
        case "Rent":
            cost = sum(i.cost for i in month.rent)
            relation = [{"id":i.id} for i in month.rent]

    payload = {
        "properties": {
            'Total':{
                'number':cost
            },
            'Weekly Expenses':{
                'relation':relation
            }
        }
    }   
    res = requests.patch(url, json=payload, headers=header)
    return res

for i in pageIDs:
    print(i[0])
    print(update_page(i[1],i[0],current))

