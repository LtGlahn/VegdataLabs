# -*- coding: utf-8 -*-
import pdb
import logging
from nvdb import query
from nvdb import query_search
from nvdb import csv_skriv
from nvdb import Objekt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

objekttyper = [{'id': 67, 'antall': 10000}]
lokasjon = {'fylke': [3]}
alletunnellop = query_search(objekttyper, lokasjon)

csv_list = []

tunnellop_nr = 0
for tunnellop in alletunnellop.objekter():

    tunnellop_nr += 1
    logger.info('Bearbeider tunnelløp %s av %s' % (tunnellop_nr, alletunnellop.antall))
    tunnellop = Objekt(tunnellop)
    aadt = []
    hgv = []
    aar = []
    veglenker = []
    tunnel = ''
    trafikkmengdeID = []
    vegnummer = []

    try:
        tunnellop.assosiasjoner(581)
    except KeyError:
        logger.warning('tunnellop (# %s) har ingen mor-tunnel' % tunnellop.id)
    else:
        for i in tunnellop.assosiasjoner(581):
            try:
                tunnel = Objekt(query(i['relasjon']['uri']))
            except Exception, e:
                logger.error('Tunnellop (# %s) har referanse til tunnel som '
                             'ikke er tilgjengelig: %s' % (tunnellop.id, e))
            else:
                pass
                #row['lengde'] += tunnellop.lengde()
        
        if tunnellop.veglenker() not in veglenker:
            veglenker += tunnellop.veglenker()
                    
        if not tunnel: 
            logger.warning('Tunnelløpå (# %s) har ingen morobjekt-tunneller' % tunnellop.id) 

    try: 
        for vegref in tunnellop.data['lokasjon']['vegReferanser']:
            nr = vegref['kategori'] + vegref['status'] + str(vegref['nummer'])
            if nr not in vegnummer: 
                vegnummer.append( nr) 
    except KeyError: 
        logger.warning('tunnellop (# %s) har ingen vegreferanser' % tunnellop.id)    
            
    if veglenker:
        objekttyper = [{
            'id': 540, 
            'antall': 10000
        }]
        lokasjon = {'veglenker': veglenker}
        trafikkmengder = query_search(objekttyper, lokasjon)
            
        if trafikkmengder.antall == 0:
            logger.warning('Tunnelløp (# %s) har ingen trafikkmengdedata' % tunnellop.id) 
        else: 
            
            for trafikkmengde in trafikkmengder.objekter():
                trafikkmengde = Objekt(trafikkmengde)
                aadt.append( str(trafikkmengde.egenskap(4623, verdi=0))) 
                hgv.append( str(trafikkmengde.egenskap(4624, verdi=0))) 
                aar.append( str(trafikkmengde.egenskap(4621, verdi=0))) 
                trafikkmengdeID.append( str( trafikkmengde.id) )
                
        if trafikkmengder.antall > 1: 
            logger.warning('Tunnelløp (# %s) har mer enn ett trafikkmengdeobjekt' % tunnellop.id) 
        
    else:
        logger.warning('tunnellop (# %s) har ingen veglenker' % tunnellop.id)
                
    try:
        tunnelnavn = tunnel.egenskap(5225)
        skiltet_lengde = tunnel.egenskap(8945)
        parallelle_lop = tunnel.egenskap(3947)
    except KeyError:
        logger.error('Tunnel (# %s) har ingen egenskaper' % tunnel.id)
        skiltetlengde = None
        tunnelnavn = None
        antlop = None
    
    fylke = tunnellop.lokasjon('fylke')
    kommune = tunnellop.lokasjon('kommune')
    tunnellopNavn = tunnellop.egenskap(1081, verdi=None)
    lengde = tunnellop.lengde()
    tunnellopID = tunnellop.id
    trafikkmengdeID = ",".join(trafikkmengdeID)
    aadt = ",".join( aadt) 
    hgv = ",".join( hgv) 
    aar = ",".join( aar) 
    vegnr = ",".join( vegnummer ) 

    csv_row = [
        tunnelnavn, tunnellopNavn, vegnr, tunnellopID, fylke, kommune, skiltet_lengde, lengde, 
        parallelle_lop, aadt, hgv, aar, trafikkmengdeID
    ]
    csv_list.append(csv_row)
    
csv_header = [
    u'Tunnelnavn', u'Tunnelløp navn', u'Vegnummer', u'Tunnelløp ID', u'Fylke', u'Kommune', u'Skiltet lengde tunnel', u'Lengde tunnelløp', 
    u'Antall parallelle hovedløp', 'AADT', u'Andel tunge kjøretøy', u'Gjelder for år', u'Trafikkmengde ID'
] 
csv_list.insert(0, csv_header)

csv_skriv('tunneler_med_trafikkmengde.csv', csv_list)
