# -*- coding: utf-8 -*-
"""Template for downloading data from NVDB api and saving to a GIS-like data 
    structure. This example downloads bridges (Bru) and saves to GeoJSON. """ 

import nvdb
import json
from shapely.wkt import loads
from shapely.geometry import mapping
import io

def hentbomstasjon():
    
    objektTyper =  [{
            "id": 45,
            "antall" : 10000
        }]

    
    bomstasjon = nvdb.query_search(objektTyper )
    bomstasjon_liste = bruer.objekter()

    # Empty geojson object, this is where we store our NVDB data. 
    geojson = {'type' : 'FeatureCollection', 'features' : [ ] }

    
    for bomst in bomstasjon_liste:
        
        # Converting JSON structure to NVDB object class (defined in nvdb.py) 
        nvdbObj =  nvdb.Objekt( bomst) 
        
        # Reading properties into temporary variables
        bomtype = nvdbObj.egenskap( egenskapstype=)
        lengde = nvdbObj.egenskap( egenskapstype=1313)
        nvdbId = nvdbObj.id 
        

        try:    
            geom = loads( nvdbObj.geometri(geometritype='geometriUtm33'))
            geomstring = (mapping(geom))
        except KeyError, e:
            print "Ingen geometri", nvdbObj.id) 
            # Har noen bruer der vegen er lagt ned => intet lokasjonsobjekt 
            # i NVDB api'et. Trenger bedre håndtering av historikk... 
            
        else: 


            # Assigning to single geojson feature: 
            feature = {
                        "type": "Feature",
                        "geometry": geomstring,
                        "properties": {
                            "bomstasjontype" = nvdbObj.egenskap( egenskapstype=9390),
                            "bomst_name_CS" = nvdbObj.egenskap( egenskapstype=10714), 
                            "anlegg_name" = nvdbObj.egenskap( egenskapstype=9391), 
                            "bomst_name" = nvdbObj.egenskap( egenskapstype=1078), 
                            "valid_year" = nvdbObj.egenskap( egenskapstype=9413 ), 
                            "url" = nvdbObj.egenskap( egenskapstype=10715 ), 
                            "Innkrevningsretning" = nvdbObj.egenskap( egenskapstype=9414 ), 
                            "Bomstasjon_Id" = nvdbObj.egenskap( egenskapstype=9595 ),
                            "Bompengeanlegg_Id" = nvdbObj.egenskap( egenskapstype=9596 ), 
                            "Takst_liten_bil" = nvdbObj.egenskap( egenskapstype=1820 ), 
                            "Takst_stor_bil" = nvdbObj.egenskap( egenskapstype=1819 ), 
                            "rushtidtakst_liten" = nvdbObj.egenskap( egenskapstype=9410 ), 
                            "Tidsdifferensiert_takst" = nvdbObj.egenskap( egenskapstype=9409 ), 
                            "rushtidtakst_liten" =  nvdbObj.egenskap( egenskapstype=9411), 
                            "Rushtid_morgen_fra" =  nvdbObj.egenskap( egenskapstype=9407 ), 
                            "Rushtid_morgen_til" =  nvdbObj.egenskap( egenskapstype=9408 ),
                            "Rushtid" ettermiddag_fra =  nvdbObj.egenskap( egenskapstype=9405 ), 
                            "Rushtid" ettermiddag, til =  nvdbObj.egenskap( egenskapstype=9406 ), 
                            "Timesregel" =  nvdbObj.egenskap( egenskapstype=9412 ), 
                            "Gratis_HC" =  nvdbObj.egenskap( egenskapstype=9404 ), 
                            "Etableringsyear" =  nvdbObj.egenskap( egenskapstype=10271 ), 
                            "Eier" =  nvdbObj.egenskap( egenskapstype=7992), 
                            "Vedlikeholdsansvarlig" =  nvdbObj.egenskap( egenskapstype=5799 )
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
