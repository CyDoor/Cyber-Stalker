import sys
import cgi
import requests

def main():
    pass

def emailStalk(email, apiKey):
    url = "https://api.fullcontact.com/v2/person.json?email=%s&apiKey=%s" %(email, apiKey)
    r = requests.get(url).json()
    if r["status"] == 200:
        return jsonToMaltego(r)
    else:
        return noResults()
    return None

def phoneStalk(phone, apiKey):
    url = "https://api.fullcontact.com/v2/person.json?phone=%s&apiKey=%s" %(phone, apiKey)
    r = requests.get(url).json()
    if r["status"] == 200:
        return jsonToMaltego(r)
    else:
        return noResults()
    return None

def twitterStalk(twitter, apiKey):
    url = "https://api.fullcontact.com/v2/person.json?twitter=%s&apiKey=%s" %(twitter, apiKey)
    r = requests.get(url).json()
    if r["status"] == 200:
        return jsonToMaltego(r)
    else:
        return noResults()
    return None

def facebookUsernameStalk(facebookUsername, apiKey):
    url = "https://api.fullcontact.com/v2/person.json?facebookUsername=%s&apiKey=%s" %(facebookUsername, apiKey)
    r = requests.get(url).json()
    if r["status"] == 200:
        return jsonToMaltego(r)
    else:
        return noResults()
    return None

def facebookIDStalk(facebookId, apiKey):
    url = "https://api.fullcontact.com/v2/person.json?facebookId=%s&apiKey=%s" %(facebookId, apiKey)
    r = requests.get(url).json()
    if r["status"] == 200:
        return jsonToMaltego(r)
    else:
        return noResults()
    return None

def noResults():
    xml = u""
    xml += "<MaltegoMessage>"
    xml += "<MaltegoTransformResponseMessage>"
    xml += "<Entities>"
    xml += "</Entities>"
    xml += "</MaltegoTransformResponseMessage>"
    xml += "</MaltegoMessage>"
    return xml

def jsonToMaltego(json):
    photoURL = ""
    xml = u""
    xml += "<MaltegoMessage>"
    xml += "<MaltegoTransformResponseMessage>"
    #get contactInfo
    xml += "<Entities>"

    if json.get("demographics"):
        if json["demographics"].get("locationDeduced"):
            deducedLocation = json["demographics"]["locationDeduced"]["deducedLocation"]
            normalizedLocation = json["demographics"]["locationDeduced"]["normalizedLocation"]
            xml += insertEntity(deducedLocation, "maltego.Location")
            xml += insertEntity(normalizedLocation, "maltego.Location")
        if json["demographics"].get("locationGeneral"):
            locationGeneral = json["demographics"]["locationGeneral"]
            xml += insertEntity(locationGeneral, "maltego.Location")

    #get photos
    if json.get("photos"):
        for photo in json["photos"]:
            if not photoURL and photo["isPrimary"]:
                photoURL = photo["url"]
            xml += insertImage(photo["url"], photo["type"], photo["isPrimary"])

    if json.get("contactInfo"):
        ##if full name exists get it
        if json["contactInfo"].get("fullName"):
            fullName = json["contactInfo"]["fullName"]
            lastName = ""
            xml += insertPerson(fullName, lastName, photoURL)
        ##if websites exist get it
        if json["contactInfo"].get("websites"):
            for url in json["contactInfo"]["websites"]:
                xml += insertEntity(url["url"], "maltego.Website")
        ##if chats exist get it
        #TODO

    if json.get("socialProfiles"):
        parts = ["id", "url", "username"]
        for social in json["socialProfiles"]:
            if social["type"] == "twitter":
                for p in parts:
                    if not p in social:
                        social[p] = "None"
                xml += insertTwitter(social["url"], social["username"], social["id"])
            elif social["type"] == "facebook":
                for p in parts:
                    if not p in social:
                        social[p] = "None"
                xml += insertFacebook(social["url"], social["username"], photoURL, social["url"])
            else:
                xml += insertEntity(social["url"], "maltego.Website")
    if json.get("organizations"):
        for organization in json["organizations"]:
            try:
                xml += insertEntity(organization["name"], "maltego.Phrase")
            except:
                pass
    xml += "</Entities>"
    xml += "</MaltegoTransformResponseMessage>"
    xml += "</MaltegoMessage>"
    f = open("xmlSample.xml", "w")
    f.write(xml)
    return xml

def insertEntity(value, entity):
    xml = u""
    xml += "<Entity Type='"+entity+"'>"
    xml += "<Value>"+cgi.escape(value)+"</Value>"
    xml += "</Entity>"
    return xml

def insertPerson(fullname, lastname, photoURL):
    xml = u""
    xml += "<Entity Type='maltego.Person'>"
    xml += "<Value>"+fullname+"</Value>"
    xml += "<AdditionalFields>"
    xml += "<Field Name='person.fullname'>"+fullname+"</Field>"
    xml += "<Field Name='person.firstnames'>"+fullname.split(" ")[0]+"</Field>"
    try:
        xml += "<Field Name='person.lastname'>"+fullname.split(" ")[1]+"</Field>"
    except:
        pass
    xml += "</AdditionalFields>"
    if photoURL:
        xml += "<IconURL>"+photoURL+"</IconURL>"
    xml += "</Entity>"
    return xml

def insertFacebook(value, username, photoURL, url):
    xml = u""
    xml += "<Entity Type='maltego.affiliation.Facebook'>"
    xml += "<Value>"+value+"</Value>"
    xml += "<AdditionalFields>"
    xml += "<Field Name='person.name' DisplayName='name'>"+username+"</Field>"
    xml += "<Field Name='affiliation.profile-url' DisplayName='Profile URL'>"+url+"</Field>"
    xml += "</AdditionalFields>"
    if photoURL:
        xml += "<IconURL>"+photoURL+"</IconURL>"
    xml += "</Entity>"
    return xml

def insertTwitter(url, name, id):
    xml = u""
    xml += "<Entity Type='maltego.affiliation.Twitter'>"
    xml += "<Value>"+name+"</Value>"
    xml += "<AdditionalFields>"
    xml += "<Field Name='affiliation.profile-url' DisplayName='Profile URL'>"+url+"</Field>"
    xml += "<Field Name='affiliation.uid' DisplayName='UID'>"+id+"</Field>"
    xml += "<Field Name='twitter.screen-name' DisplayName='Screen Name'>"+name+"</Field>"
    xml += "</AdditionalFields>"
    xml += "</Entity>"
    return xml


def insertImage(value, displayName, primary):
    xml = u""
    xml += "<Entity Type='maltego.Image'>"
    xml += "<Value>"+displayName+"</Value>"
    xml += "<AdditionalFields>"
    xml += "<Field Name='properties.image' DisplayName='description'>"+displayName+str(primary)+"</Field>"
    xml += "<Field Name='fullImage' DisplayName='URL'>"+value+"</Field>"
    xml += "</AdditionalFields>"
    xml += "<Weight>0</Weight>"
    xml += "</Entity>"
    return xml


if __name__ == "__main__":
    apiKey = "d4bca894ef1a57ca"
    email = sys.argv[1]
    print emailStalk(email, apiKey)
    #phone = sys.argv[1]
    #print phoneStalk(phone, apiKey)
    #twitter = sys.argv[1]
    #print twitterStalk(twitter, apiKey)
    #facebook = sys.argv[1]
    #print facebookUsernameStalk(facebook, apiKey)
    #facebookId = sys.argv[1]
    #print facebookIDStalk(facebookId, apiKey)
