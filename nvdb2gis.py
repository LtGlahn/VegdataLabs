# -*- coding: utf-8 -*-
"""Template for downloading data from NVDB api and saving to a GIS-like data 
    structure. This example downloads bridges (Bru) and saves to GeoJSON. """ 

import nvdb
import json
from shapely.wkt import loads
from shapely.geometry import mapping
import io
import pyshp 

def vegreferanse2shp(): 

    objektTyper =  [{
        "id": 532,
        "filter": [{
            "type": "Konnekteringslenke",
            "operator": "!=",
            "verdi": ["Konnekteringslenke"]
        }]
    }]
    
    lokasjon = {
        "vegreferanse": ["E"],
        "bbox": "262645,7027798,269974,7032413"
    }

    vegref = nvdb.query_search( objektTyper, lokasjon = lokasjon)

def hentNvdbBruer(lengde=1000):
    
    lengde = str(lengde) 
    
    objektTyper =  [{
            "id": 60,
            "antall" : 10000, 
            "filter": [{
                            "type": "Lengde",
                            "operator": ">=",
                            "verdi": [lengde]
                        },{
                            "type": "Brukategori",
                            "operator": "=",
                            "verdi": ["Vegbru"]
                        }
                    ]
        }]

    
    bruer = nvdb.query_search(objektTyper )
    bruliste = bruer.objekter()

    # Empty geojson object, this is where we store our NVDB data. 
    geojson = { "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::25833"}}, 
                'type' : 'FeatureCollection', 'features' : [ ] }

    
    for bru in bruliste:
        
        # Converting JSON structure to NVDB object class (defined in nvdb.py) 
        nvdbObj =  nvdb.Objekt( bru) 
        
        # Reading properties into temporary variables
        brunavn = nvdbObj.egenskap( egenskapstype=1080)
        lengde = nvdbObj.egenskap( egenskapstype=1313)
        nvdbId = nvdbObj.id 
        

        try:    
            geom = loads( nvdbObj.geometri(geometritype='geometriUtm33'))
            geomstring = (mapping(geom))
        except KeyError, e:
            print "Ingen geometri", brunavn, nvdbObj.id, "lengde=", nvdbObj.egenskap(egenskapstype=1313) 
            # Har noen bruer der vegen er lagt ned => intet lokasjonsobjekt 
            # i NVDB api'et. Trenger bedre håndtering av historikk... 
            
        else: 


            # Assigning to single geojson feature: 
            feature = {
                        "type": "Feature",
                        "geometry": geomstring,
                        "properties": {
                            "lengde" : lengde,
                            "brunavn" : brunavn, 
                            "nvdbId" : nvdbId
                        }
                    }



    # Appending feature to geojson feature list
            geojson['features'].append( feature ) 
    
    # Writing geojson file
    with io.open('bruer.geojson', 'w', encoding='utf8') as fn:
        data = json.dumps( geojson, ensure_ascii = False, indent = 4)
        fn.write( unicode( data))


if __name__ == '__main__': 
    
    # hentNvdbBruer( lengde=1000)
    vegreferanse2shp()
    
