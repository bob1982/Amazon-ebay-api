import bottlenose
import xmltodict
import MySQLdb
import ConfigParser
config=ConfigParser.ConfigParser()
config.read("amazon.yaml")
def getKey(item,keys):
    cnt=len(keys)
    for idx in range(0,cnt):

        if keys[idx] in item.keys():
            item=item[keys[idx]]
        else:
            return ''
    return item



amazon=bottlenose.Amazon(config.get('Amazon','access_key'),config.get('Amazon','secret_key'),config.get('Amazon','associate_tag'),Region="IN",MaxQPS=0.9)
#response = amazon.ItemSearch(Keywords="Kindle 3G", SearchIndex="All")
#print response
#response=amazon.ItemLookup(ItemId="B01CFYRK1K",MerchantId="Amazon",ResponseGroup="Large,Offers")
#response=amazon.ItemLookup(ItemId="B00XKYDZUU",ResponseGroup="OfferFull")
#print response
#exit(0)
db=MySQLdb.connect("localhost","root","","ameb")
cursor=db.cursor()
sql="SELECT id,asin FROM ft_asin WHERE processed=0"
cursor.execute(sql)
result=cursor.fetchall()


for row in result:
    asin=row[1]
    id=row[0]

    response=amazon.ItemLookup(ItemId=asin,ResponseGroup="Large,Offers")



    xml=xmltodict.parse(response)
    items=xml['ItemLookupResponse']['Items']['Item']
    if not isinstance(items,list):
        items=[items]

    cnt=len(items)
    for idx in range(0,cnt):
        title=items[idx]['ItemAttributes']['Title']
        asin=getKey(items[idx],['ASIN'])
        title=getKey(items[idx],['ItemAttributes','Title'])
        brand=getKey(items[idx],['ItemAttributes','Brand'])
        feature = getKey(items[idx], ['ItemAttributes', 'Feature'])
        amount = getKey(items[idx], ['Offers', 'Offer', 'OfferListing', 'SalePrice', 'Amount'])
        if (len(amount) <= 0):
            amount = getKey(items[idx], ['OfferSummary', 'LowestNewPrice', 'Amount'])
        if(len(amount)<=0):
            amount=0;
        amount=int(amount)/100.0
        availability=getKey(items[idx], ['Offers', 'Offer','OfferListing','AvailabilityAttributes','AvailabilityType'])
        fba = getKey(items[idx],['Offers', 'Offer', 'OfferListing', 'IsEligibleForSuperSaverShipping'])
        amzprime = getKey(items[idx], ['Offers', 'Offer', 'OfferListing', 'IsEligibleForPrime'])
        description=getKey(items[idx], ['EditorialReviews', 'EditorialReview', 'Content'])
        images=getKey(items[idx],['ImageSets','ImageSet'])
        limage=getKey(items[idx],['MediumImage','URL'])
        description = description.encode('utf-8')
        if not isinstance(feature,list):
            feature = feature.encode('utf-8')
        else:
            fcount=len(feature)
            for fc in range(0,fcount):
                feature[fc]=feature[fc].encode('utf-8')
        img=[]
        if isinstance(images,list):
            imgcount=len(images)
            for i in range(0,imgcount):
                img.append(images[i]['LargeImage']['URL'])
        else:
            img.append(images['LargeImage']['URL'])

        # print asin
        # print title
        # print description
        # print "~".join(feature)
        # print limage
        # print amount
        # print brand
        # print "~".join(img)
        sql="INSERT INTO ft_product (id_asin,title,features,description,img,image,price,brand,availability,fba,prime,date_last_scanned) "
        sql=sql + "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())" # % (id,title,"~".join(feature),description,"~".join(img),amount,brand,availability,fba,amzprime)
        cursor.execute(sql,(id,title,"~".join(feature),description,"~".join(img),limage,amount,brand,availability,fba,amzprime))

        sql="UPDATE ft_asin SET processed=1 WHERE id=" +  str(id)
        cursor.execute(sql)
        db.commit()


print "done"





