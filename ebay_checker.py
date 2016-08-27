from ebaysdk.trading import Connection as Trading
import MySQLdb
import  string
import  uuid
def escape(str):
    str=str.replace("&","-")
    return str

api=Trading(config_file='ebay.yaml',siteid='203')
request={}
request["ActiveList"]={"Include":"true"}
request["ActiveList"]={"ListingType":"FixedPriceItem"}
request["ActiveList"]={"Pagination":{"EntriesPerPage":1}}
request["ActiveList"]={"Pagination":{"PageNumber":1}}

db=MySQLdb.connect("localhost","root","","ameb")
cursor=db.cursor()

response=api.execute("GetMyeBaySelling",request)
xml=response.dict()
print xml
pages=xml["ActiveList"]["PaginationResult"]["TotalNumberOfPages"]
print  "pages=" + str(pages)
items=xml["ActiveList"]["ItemArray"]["Item"]
cnt=len(items)
for idx in range(0,cnt):
    itemid=items[idx]["ItemID"]
    price=items[idx]["BuyItNowPrice"]["value"]
    sql_query="SELECT id,ebayprice from ft_product WHERE itemID='" + str(itemid) + "'"
    cursor.execute(sql_query)
    results=cursor.fetchall()
    if len(results)==0:
        continue
    row=results[0]
    id=row[0]
    eprice=row[1]
    diff=eprice-float(price)
    diff=abs(diff)
    if diff<=1:
        continue
    api.execute("ReviseFixedPriceItem",{"Item":{"ItemID":itemid,"StartPrice":eprice}})
    print "ebay=" + str(eprice)

print "done"

