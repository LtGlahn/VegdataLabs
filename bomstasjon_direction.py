# -*- coding: utf-8 -*-
"""Template for downloading data from NVDB api and  augmenting with 
    road net information from Visveginfo-service. 
    
    This example downloads toll stations (bomstasjon) and saves to GeoJSON. """

import requests
import nvdb
import json
from shapely.wkt import loads
from shapely.geometry import mapping
import io
import xmltodict 
import pdb

def visveginfo_direction( veglenkeID, fra, nvdbObjId=1):
    """Fetching data from Visveginfo-service

    In visveginfo-documentation, parameter veglenkeID == reflinkoid (integer) 
    and fra == rellen (float, in range [0..1], non-dimentional linear reference)
    
    nvdbObjId is for debugging purposes, so you can track where things go wrong. 
    Supposedly this is  the ID of the toll station (bomstasjon) you want to  
    want to 
    
    http://visveginfo-static.opentns.org/help.htm#GetRoadReferenceForNVDBReference
    http://data.norge.no/data/statens-vegvesen/visveginfo-komplekse-sp%C3%B8rringer-p%C3%A5-vegnett
    """
    
    url = 'http://visveginfo-static.opentns.org/RoadInfoService/GetRoadReferenceForNVDBReference'
    params = { 'reflinkoid' : veglenkeID, 'rellen' : fra } 
    
    proxyDict = {
              "http"  : 'http://your.proxy.url.or.ip:8080',
              "https" : 'http://your.proxy.url.or.ip:8080'
            }
    
    
    # r = requests.get( url, params,  proxies = proxyDict ) 
    r = requests.get( url, params  ) 

    if not r.ok:
        print "Fetching data from Visveginfo FAILED for %s veglenke=%d FRA=%f" % (nvdbObjId, veglenkeID, fra) 

    else: 
        
        try: 
            roadData = xmltodict.parse( r.text)
            direction = roadData['RoadReference']['RoadnetHeading']
        except KeyError:
            print "Could not find direction from this visveginfo response"
            print r.text
        else: 

            return direction

    return None



def hentbomstasjon():

    objektTyper =  [{
            "id": 45,
            "antall" : 10000
        }]


    bomstasjon = nvdb.query_search(objektTyper )
    bomstasjon_liste = bomstasjon.objekter()

    # Empty geojson object, this is where we store our NVDB data.
    geojson = {'type' : 'FeatureCollection', 'features' : [ ] }

    for bomst in bomstasjon_liste:

        # Converting JSON structure to NVDB object class (defined in nvdb.py)
        nvdbObj =  nvdb.Objekt( bomst)

        try:
            geom = loads( nvdbObj.geometri(geometritype='geometriWgs84'))
            geomstring = (mapping(geom))
            veglenker = nvdbObj.veglenker()

        except KeyError, e:
            print "Ingen geometri", nvdbObj.id
            # Har noen bruer der vegen er lagt ned => intet lokasjonsobjekt
            # i NVDB api'et. Trenger bedre håndtering av historikk...

        else:


            direction = visveginfo_direction( veglenker[0]['id'], veglenker[0]['fra'], nvdbObj.id)

            # Assigning to single geojson feature:
            feature = {
                        "type": "Feature",
                        "geometry": geomstring,
                        "properties": {
                            "bomstasjontype" : nvdbObj.egenskap( egenskapstype=9390, verdi=None),
                            "bomst_name_CS" : nvdbObj.egenskap( egenskapstype=10714, verdi=None),
                            "anlegg_name" : nvdbObj.egenskap( egenskapstype=9391, verdi=None),
                            "bomst_name" : nvdbObj.egenskap( egenskapstype=1078, verdi=None),
                            "valid_year" : nvdbObj.egenskap( egenskapstype=9413 , verdi=None),
                            "url" : nvdbObj.egenskap( egenskapstype=10715 , verdi=None),
                            "Innkrevningsretning" : nvdbObj.egenskap( egenskapstype=9414 , verdi=None),
                            "Bomstasjon_Id" : nvdbObj.egenskap( egenskapstype=9595 , verdi=None),
                            "Bompengeanlegg_Id" : nvdbObj.egenskap( egenskapstype=9596 , verdi=None),
                            "Takst_liten_bil" : nvdbObj.egenskap( egenskapstype=1820 , verdi=None),
                            "Takst_stor_bil" : nvdbObj.egenskap( egenskapstype=1819 , verdi=None),
                            "rushtidtakst_liten" : nvdbObj.egenskap( egenskapstype=9410 , verdi=None),
                            "Tidsdifferensiert_takst" : nvdbObj.egenskap( egenskapstype=9409 , verdi=None),
                            "rushtidtakst_liten" :  nvdbObj.egenskap( egenskapstype=9411, verdi=None),
                            "Rushtid_morgen_fra" :  nvdbObj.egenskap( egenskapstype=9407 , verdi=None),
                            "Rushtid_morgen_til" :  nvdbObj.egenskap( egenskapstype=9408 , verdi=None),
                            "Rushtid_ettermiddag_fra" :  nvdbObj.egenskap( egenskapstype=9405 , verdi=None),
                            "Rushtid_ettermiddag_til" :  nvdbObj.egenskap( egenskapstype=9406 , verdi=None),
                            "Timesregel" :  nvdbObj.egenskap( egenskapstype=9412 , verdi=None),
                            "Gratis_HC" :  nvdbObj.egenskap( egenskapstype=9404 , verdi=None),
                            "Etableringsyear" :  nvdbObj.egenskap( egenskapstype=10271 , verdi=None),
                            "Eier" :  nvdbObj.egenskap( egenskapstype=7992, verdi=None),
                            "Vedlikeholdsansvarlig" :  nvdbObj.egenskap( egenskapstype=5799 , verdi=None),
                            "RoadnetHeading" : direction 
                        }
                    }



    # Appending feature to geojson feature list
            geojson['features'].append( feature )

    # Writing geojson file
    with io.open('bomst.geojson', 'w', encoding='utf8') as fn:
        data = json.dumps( geojson, ensure_ascii = False, indent = 4)
        fn.write( unicode( data))


if __name__ == '__main__':

    hentbomstasjon( )
