import bottlenose
import MySQLdb
import xmltodict

def getKey(item,keys):
    cnt=len(keys)
    for idx in range(0,cnt):

        if keys[idx] in item.keys():
            item=item[keys[idx]]
        else:
            return ''
    return item


config = {
    'access_key': 'AKIAIBQFAULRRIOEHZ4Q',
    'secret_key': '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',
    'associate_tag': 'redtoad-10',
    'locale': 'us'
}
amazon=bottlenose.Amazon(config['access_key'],config['secret_key'],config['associate_tag'],Region="IN",MaxQPS=0.9)


db=MySQLdb.connect("localhost","root","","ameb")
cursor=db.cursor()
sql="SELECT ft_product.id,id_asin,asin,shipping,ebay_fee_percentage,paisapay_fee_percentage from ft_product,ft_asin WHERE active=1 AND id_asin=ft_asin.id AND date_last_scanned<(NOW()- INTERVAL 2 MINUTE)"
#sql="SELECT ft_product.id,id_asin,asin from ft_product,ft_asin WHERE id_asin=ft_asin.id "
cursor.execute(sql)
results=cursor.fetchall()
for row in results:
    id=row[0]
    asin=row[2]
    shipping=row[3]
    e_fp=row[4]
    p_fp=row[5]




    response = amazon.ItemLookup(ItemId=asin, ResponseGroup="Offers")
    print response
    xml = xmltodict.parse(response)
    items = xml['ItemLookupResponse']['Items']['Item']
    if not isinstance(items, list):
        items = [items]
    cnt = len(items)
    for idx in range(0,cnt):
        amount = getKey(items[idx], ['Offers', 'Offer','OfferListing', 'SalePrice','Amount'])
        if len(amount)<=0:
            amount = getKey(items[idx], ['Offers', 'Offer', 'OfferListing', 'Price', 'Amount'])
        if(len(amount)<=0):
            amount = getKey(items[idx], ['OfferSummary', 'LowestNewPrice', 'Amount'])
        amount = int(amount) / 100.0

        availability = getKey(items[idx], ['Offers', 'Offer', 'OfferListing', 'AvailabilityAttributes', 'AvailabilityType'])

        total = amount + shipping
        total = total + total * (e_fp + p_fp) / 100.0
        fee = total * (e_fp + p_fp) / 100.0
        total = amount + shipping + fee
        e_ff = total * e_fp / 100.0
        p_ff = total * p_fp / 100.0
        profit = total - amount - fee

        sql="UPDATE ft_product SET ebayprice="  + str(total) + ",ebay_final_fee=" +  str(e_ff) + ",paisapay_final_fee=" + str(p_ff) + ",profit=" + str(profit) + ",price=" + str(amount) + ",availability='" + str(availability) + "',date_last_scanned=NOW() WHERE id=" + str(id)
        print sql
        cursor.execute(sql)

db.commit()
