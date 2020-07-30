import fut
import time
import json

config = {}

print("reading configuration")
with open('config.json', 'r', encoding='utf8') as confFile:
    config = json.load(confFile)

print("connecting to FUT ...")
start = time.time()
session = fut.Core(config['username'], config['password'], config['secret'], config['platform'])
end = time.time()
elapsed = end - start
print("connected in " + str(elapsed) + " seconds")

# check tradePile available slots
slots = 0
slots = 100 - len(session.tradepile())
print("available trade pile slots:" + str(slots))

# check credits
credit = session.keepalive()
print("you have: " + str(session.credits) + " coins")


def listPlayerOnTransferMarket(item):
    min_buy_now_price = getMinBuyNowPrice(item['resourceId'])
    print("selling item: " + str(item['id']) + " of type: " + item['itemType'] + " min:" + str(item['marketDataMinPrice']) + ", buyNow:" + str(
        min_buy_now_price))
    session.sell(item['id'], item['marketDataMinPrice'], min_buy_now_price)


def getMinBuyNowPrice(definitionId):
    itemAuctions = session.search(ctype='player', defId=definitionId)
    minBuyNowPrice = itemAuctions[0]['buyNowPrice']
    for i in range(1, len(itemAuctions) - 1):
        minBuyNowPrice = min(minBuyNowPrice, itemAuctions[i]['buyNowPrice'])
    print("minimum buy now for this player is: " + str(minBuyNowPrice))
    return minBuyNowPrice


def sortitems():
    print("working on unassigned items...")
    remaining = session.unassigned()
    for item in remaining:
        if item['itemType'] == 'misc':
            print('redeem item: ' + str(item['id']))
            session.redeemItem(item['id'])
        elif item['itemType'] == 'player':
            global slots
            session.sendToTradepile(item['id'])
            slots -= 1
            print("item: " + str(item['id']) + " " + item['itemType'] + " to be sent to trade pile")
        else:
            sent = session.sendToClub(item['id'])
            if sent:
                print("item: " + str(item['id']) + " " + item['itemType'] + " to be sent to club")
            else:
                session.quickSell(item['id'])
                print("item: " + str(item['id']) + " " + item['itemType'] + " discarded")


def reviewTradePile():
    print("reviewing trade pile and adjusting prices...")
    # session.tradepileClear()
    myTradePile = session.tradepile()
    for item in myTradePile:
        if item['itemType'] == 'player' and (item['tradeState'] == 'expired' or item['tradeState'] is None) and (
                item['buyNowPrice'] > 200 or item['buyNowPrice'] == 0):
            listPlayerOnTransferMarket(item)
    session.relist()


def trade():
    print("started investment ...")
    # session.tradepileClear()
    # session.relist()
    global credit
    print("you have: " + str(credit) + " coins")
    print("buy a normal bronze pack")
    packContents = session.buyPack(100)
    credit = session.keepalive()
    print("now you have: " + str(credit) + " coins")
    sortitems()


sortitems()

while credit >= 400 and slots >= 3:
    trade()

reviewTradePile()
