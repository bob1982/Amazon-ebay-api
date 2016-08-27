import bottlenose
import xmltodict
import MySQLdb

db=MySQLdb.connect("localhost","root","","ameb")
cursor=db.cursor()

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
for page in range(0,1):
    p=page+1
    response=amazon.BrowseNodeLookup(BrowseNodeId=1350381031,ResponseGroup='TopSellers')
    #response=amazon.ItemSearch(BrowseNode=976390031,ItemPage=p,ResponseGroup='TopSellers')
    #response=amazon.ItemSearch(BrowseNode=1,Searchindex='Books',ItemPage=p,Sort='psrank',ResponseGroup='Small')
    print response
    xml = xmltodict.parse(response)
    items=xml['BrowseNodeLookupResponse']['BrowseNodes']['BrowseNode']['TopSellers']['TopSeller']
    print items

    cnt=len(items)
    for idx in range(0,cnt):
        asin=items[idx]['ASIN']
        sql="INSERT IGNORE INTO ft_asin (asin,date_added,processed,valid) VALUES('" + asin + "',NOW(),0,0)"
        cursor.execute(sql)
db.commit()
print "done"


