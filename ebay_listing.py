from ebaysdk.trading import Connection as Trading
import MySQLdb
import  string
import  uuid
def escape(str):
    str=str.replace("&","-")
    return str

api=Trading(config_file='ebay.yaml',siteid='203')
#api=Trading(config_file='ebay.yaml',domain='api.sandbox.ebay.com')


#response=api.execute('GetUser',{})
#response=api.execute('GetOrders',{'NumberOfDays':30})
myitem = {
    "Item": {
        "Title": "Harry Potter and the Philosopher's Stone",
        "Description": "This is the first book in the Harry Potter series. In excellent condition!",
        "PrimaryCategory": {"CategoryID": "10364"},
        "StartPrice": "100.0",
        "CategoryMappingAllowed": "true",
        "Country": "IN",
        "ConditionID": "1000",
        "Currency": "INR",
        "DispatchTimeMax": "3",
        "ListingDuration": "Days_7",
        "ListingType": "FixedPriceItem",
        "PaymentMethods": "PaisaPayEscrow",
        "Location":"PATIALA, PB",
        #"ProductListingDetails" :{"BrandMPN":{"Brand":""}},
        #"PayPalEmailAddress": "tkeefdddder@gmail.com",
        "PictureDetails": {"GalleryType":"Gallery","GalleryURL":"sdsd","PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007"},
        "PostalCode": "147001",
        "Quantity": "1",
        "ReturnPolicy": {
            "ReturnsAcceptedOption": "ReturnsAccepted",
            "RefundOption": "MoneyBack",
            "ReturnsWithinOption": "Days_30",
            "Description": "If you are not satisfied, return the book for refund.",
            "ShippingCostPaidByOption": "Buyer"
        },
        "ShippingDetails": {
            "ShippingType": "Flat",
            "ShippingServiceOptions": {
                "ShippingServicePriority": "1",
                "ShippingService": "IN_Express",
                "ShippingServiceCost": "0.00"
            }
        },
        "Site": "India"
    }
}

myitem1 = {
    "Item": {
        "Title": "Harry Potter and the Philosopher's Stone",
        "Description": "This is the first book in the Harry Potter series. In excellent condition!",
        "PrimaryCategory": {"CategoryID": "11104"},
        "StartPrice": "1.0",
        "CategoryMappingAllowed": "true",
        "Country": "US",
        "ConditionID": "3000",
        "Currency": "USD",
        "DispatchTimeMax": "3",
        "ListingDuration": "Days_7",
        "ListingType": "FixedPriceItem",
        "PaymentMethods": "PayPal",
        "PayPalEmailAddress": "tkeefdddder@gmail.com",
        "PictureDetails": {"PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007"},
        "PostalCode": "95125",
        #"ProductListingDetails" :{"BrandMPN":{"Brand":""}},
        "Quantity": "1",
        "ReturnPolicy": {
            "ReturnsAcceptedOption": "ReturnsAccepted",
            "RefundOption": "MoneyBack",
            "ReturnsWithinOption": "Days_30",
            "Description": "If you are not satisfied, return the book for refund.",
            "ShippingCostPaidByOption": "Buyer"
        },
        "ShippingDetails": {
            "ShippingType": "Flat",
            "ShippingServiceOptions": {
                "ShippingServicePriority": "1",
                "ShippingService": "USPSMedia",
                "ShippingServiceCost": "2.50"
            }
        },
        "Site": "US"
    }
}
db=MySQLdb.connect("localhost","root","","ameb")
cursor=db.cursor()

sql="SELECT template from ft_template"
cursor.execute(sql)
result=cursor.fetchall()
row=result[0]
template=row[0]


sql="SELECT id,title,description,features,img,ebayprice,brand FROM ft_product WHERE active=1 AND ebaylisted=0"
cursor.execute(sql)
result=cursor.fetchall()

for row in result:
    id=row[0]
    title=row[1]
    description=row[2]
    features=row[3]
    img=row[4]
    price=row[5]
    brand=row[6]

    response = api.execute("GetSuggestedCategories", {"Query": escape(title)})
    dict = response.dict()
    cnt = dict["CategoryCount"]
    cnt = int(cnt)
    if cnt == 0:
        categoryid = "11104"
    else:
        categoryid = dict["SuggestedCategoryArray"]["SuggestedCategory"][0]["Category"]["CategoryID"]




    myitem["Item"]["PrimaryCategory"]["CategoryID"]=categoryid
    myitem["Item"]["Title"]="<![CDATA[" + title[:79] + "]]>"
    template=template.replace("{title}",title)
    template=template.replace("{description}","<p>" + description + "</p>")
    features=features.split("~")
    cnt=len(features)
    ptr=''
    for idx in range(0,cnt):
        ptr=ptr + "<li>" + features[idx] + "</li>\n"
    template=template.replace("{features}",ptr)

    des="<![CDATA[" + template + "]]>"
    #des=escape(des)
    myitem["Item"]["Description"]=des
    myitem["Item"]["StartPrice"]=price
    #myitem["Item"]["ProductListingDetails"]["BrandMPN"]["Brand"]=brand
    print myitem["Item"]["Description"]
    img_arr=img.split("~")
    ebay_arr=[]
    #ebay_arr.append("http://i.ebayimg.com/00/s/MjgyWDI4Mg==/z/BVcAAOSw0UdXv2CT/$_1.JPG?set_id=8800004005")
    print img_arr
    cnt=len(img_arr)
    for idx in range(0,cnt):
        pictureData = {
            "WarningLevel": "High",
            "ExternalPictureURL": img_arr[idx],
            "PictureName": escape(title[:7]) + "-" + str(idx)
        }
        response=api.execute('UploadSiteHostedPictures',pictureData)
        dict=response.dict()
        ebay_arr.append(dict["SiteHostedPictureDetails"]["FullURL"])
    print ebay_arr
    myitem["Item"]["PictureDetails"]["GalleryURL"]=ebay_arr[0]
    myitem["Item"]["PictureDetails"]["PictureURL"] = ebay_arr
    #myitem["Item"]["ProductListingDetails"]["BrandMPN"]["Brand"]=brand
    response=api.execute('AddFixedPriceItem', myitem)
    dict=response.dict()
    print dict
    itemid=dict["ItemID"]
    sql_query="UPDATE ft_product SET itemID='" + str(itemid) + "',ebaylisted=1 WHERE id=" + str(id)
    cursor.execute(sql_query)
    db.commit()
#response=api.execute('GetItem',{'ItemID':'272334238605'})
#print response.dict()
#print response.reply