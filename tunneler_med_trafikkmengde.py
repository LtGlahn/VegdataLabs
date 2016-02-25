# -*- coding: utf-8 -*-
import pdb
import logging
from nvdb import query
from nvdb import query_search
from nvdb import csv_skriv
from nvdb import Objekt
from nvdbinbrowser import visNvdbId 


logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

objekttyper = [{'id': 67, 'antall': 10000}]
lokasjon = {'region': [1, 2, 3, 4, 5]}
alletunnellop = query_search(objekttyper, lokasjon)

csv_list = []

tunnellop_nr = 0
fellestrafikk = { } 
# Debugging
names = [ 'Strind', 'Grills']
nyliste = [] 
for tunnellop in alletunnellop.objekter():
    tunnellop2 = Objekt(tunnellop)    
    navn = tunnellop2.egenskap(1081, verdi=None)
    if navn and navn[0:6] in names: 
        nyliste.append( tunnellop)

#for tunnellop in nyliste: 
for tunnellop in alletunnellop.objekter():

    tunnellop_nr += 1
    # logger.info('Bearbeider tunnelløp %s av %s' % (tunnellop_nr, alletunnellop.antall))
    tunnellop = Objekt(tunnellop)
    aadt = -1
    hgv = -1
    aar = -1
    veglenker = []
    tunnel = ''
    trafikkmengdeID = []
    vegnummer = []
    envegmed = []
    vegrefobjektID = []
    kommentar = []
    veglenkerTunnel = []
    tunnelloplenke = visNvdbId(tunnellop.id, returnlink=True)
    
    # Tomt trafikkmengde-objekt (strandsoner i Oppdal) 
    trafikkmengde = query_search( [{'id':516}], {'kommune':[1634]} )

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
                
        if not tunnel: 
            logger.warning('Tunnelløpå (# %s) har ingen morobjekt-tunneller' % tunnellop.id) 

    if tunnel: 
        try:
            tunnelnavn = tunnel.egenskap(5225)
            skiltet_lengde = tunnel.egenskap(8945)
            parallelle_lop = tunnel.egenskap(3947)
            veglenkerTunnel = tunnel.veglenker()
        except (KeyError):
            logger.error('Tunnel (# %s) har ingen egenskaper' % tunnel.id)
            skiltetlengde = None
            tunnelnavn = None
            antlop = None
            
    veglenker = tunnellop.veglenker()
    fylke = tunnellop.lokasjon('fylke')
    kommune = tunnellop.lokasjon('kommune')
    fylkenr = []
    tunnellopNavn = tunnellop.egenskap(1081, verdi=None)
    lengde = tunnellop.lengde()
    tunnellopID = tunnellop.id
    
    vegreferansesok1 = [] 
    vegreferansesok2 = [] 
    trafikkmengdekommentar = ''



    try: 
        for vegref in tunnellop.data['lokasjon']['vegReferanser']:
            nr = vegref['kategori'] + vegref['status'] + str(vegref['nummer'])
            if vegref['fylke'] not in fylkenr: 
                fylkenr.append( vegref['fylke'] )
                       
            vegref1 = vegref['kategori'] + vegref['status'] + \
                str(vegref['nummer']) + 'HP' + str(vegref['hp']) + 'M' + \
                str(vegref['fraMeter']) + '-' + str(vegref['tilMeter']) 
                
            vegref2 = vegref['kategori'] + vegref['status'] + \
                str(vegref['nummer']) + 'HP' + str(vegref['hp']) 

            if nr not in vegnummer: 
                vegnummer.append( nr) 

            if vegref1 not in vegreferansesok1: 
                vegreferansesok1.append( str(vegref1)  ) 
                
            if vegref2 not in vegreferansesok2: 
                vegreferansesok2.append( str(vegref2)) 

    except KeyError: 
        logger.warning(u'tunnellop (# %s) har ingen vegreferanser' % tunnellop.id)    
        
    if not veglenker and veglenkerTunnel:
        veglenker = veglenkerTunnel
        logger.warning('Tunnelløp (# %s) har ingen veglenker, henter data fra tunnel (# )' % (tunnellop.id, tunnel.id))
  

    if veglenker: 
        objekttyper = [{
            'id': 540, 
            'antall': 10000
        }]
        lokasjon = {'veglenker': veglenker}
        trafikkmengder = query_search(objekttyper, lokasjon)
        
    else: 
        logger.warning('Tunnelløp (# %s) har ingen veglenker' % tunnellop.id)
 
            
    if trafikkmengder.antall == 0:
        logger.info( 'Tunnellop (# %s) har ingen trafikkmengdedata paa veglenker' % tunnellop.id)
        trafikkmengdekommentar =  'Ingen trafikkmengde paa tunnellop veglenker'
        
        if len( vegreferansesok1) > 0: 
        
            lokasjon2 = { 'fylke' : fylkenr, 'vegreferanse' : vegreferansesok1 } 
            trafikkmengder = query_search(objekttyper, lokasjon2 )
            
            if trafikkmengder.antall > 0: 
                logger.info( 'Fant trafikkmengdedata ut fra vegreferanse meterverdi for tunnel #%s' % tunnellop.id ) 
                trafikkmengdekommentar =  'Trafikkmengde ut fra vegreferanse meterverdi'
        
            else: 
                logger.warning(' Fant INGEN trafikkmengdedata ut fra vegreferanse meterverdi for tunnellop #%s' % tunnellop.id ) 

                if tunnel: 
                    lokasjonTunnel = {'veglenker': veglenkerTunnel}
                    trafikkmengder = query_search(objekttyper, lokasjonTunnel)
                    if trafikkmengder.antall > 0:
                        logger.info( 'Hentet trafikkmengde-data fra tunnel (# %s) for lop (# %s) ' % (tunnel.id, tunnellop.id))
                        trafikkmengdekommentar =   'Hentet trafikkmengdedata fra mor-tunnel'
                    else:
                        trafikkmengdekommentar = 'Provde ALT: Veglenker, vegreferanse og mortunnel-veglenker'
                        # visNvdbId( tunnellop.id ) 
                        
    if trafikkmengdekommentar:
        kommentar.append(trafikkmengdekommentar)
        
    
    
    if trafikkmengder.antall > 0:
        
        for trafikkmengde in trafikkmengder.objekter():
            trafikkmengde = Objekt(trafikkmengde)
            aadt = max(aadt,  int(trafikkmengde.egenskap(4623, verdi=0))) 
            hgv  = max(hgv, int(trafikkmengde.egenskap(4624, verdi=0))) 
            aar  = max(aar, int(trafikkmengde.egenskap(4621, verdi=0))) 
            trafikkmengdeID.append( str( trafikkmengde.id) )
            
    if trafikkmengder.antall > 1: 
        logger.info('Tunnellop (# %s) har mer enn ett trafikkmengdeobjekt' % tunnellop.id) 

    
    objekttyper[0]['id'] = 532
        
    vegreferanser = query_search(objekttyper, lokasjon) 
    if vegreferanser.antall == 0: 
        logger.warning('Fant ingen vegreferanser for tunnellop (# %s) Veglenker: %s' % (tunnellop.id, veglenker))
        
        envegmed.append('Gjetning - begge retninger')
        
        if tunnel: 
            lokasjonTunnel = {'veglenker': veglenkerTunnel}
            vegreferanser = query_search(objekttyper, lokasjonTunnel)
            if vegreferanser.antall > 0:
                logger.info( 'Hentet vegreferansedata fra tunnel (# %s) for lop (# %s) ' % (tunnel.id, tunnellop.id))
                kommentar.append( 'Hentet vegreferanse fra tunnel')
            
            else: 
                logger.warning('Fant ingen vegreferanser for TUNNEL (# %) mor til lop (# %s)' % (tunnel.id, tunnellop.id)) 

    if vegreferanser.antall > 0: 
        for vegref in vegreferanser.objekter():
            vegref = Objekt(vegref)
            
            # retning = vegref.egenskap(4707, verdi='Begge retninger')
            retning = vegref.egenskap(4707, verdi=u' ')
            retning = retning.strip()
            
            # Må legge på defaultverdi "Begge retninger"
            if not retning.strip():
                retning = 'Begge retninger'
            
            if retning not in envegmed: 
                envegmed.append( retning) 
        
            if vegref.id not in vegrefobjektID: 
                vegrefobjektID.append( str(vegref.id)) 
                
            # if str(vegref.id)  == '446810542': 
                # pdb.set_trace()
        
        
        
    
    trafikkmengdeID = ",".join(trafikkmengdeID)
    #aadt = ",".join( aadt) 
    #hgv = ",".join( hgv) 
    #aar = ",".join( aar)
    if aadt == -1: 
        aadt = None
    if hgv == -1: 
        hgv = None
    if aar == -1:
        aar = None
    vegnr = ",".join( vegnummer ) 
    retning = ",".join( envegmed ) 
    vegrefId = ",".join( vegrefobjektID ) 
    kommentar = ",".join( kommentar  ) 
    
   

    csv_row = [
        tunnelnavn, tunnellopNavn, vegnr, tunnellopID, fylke, kommune, skiltet_lengde, lengde, 
        parallelle_lop, aadt, hgv, aar, trafikkmengdeID, retning, kommentar, tunnelloplenke
    ]
    csv_list.append(csv_row)
    
csv_header = [
    u'Tunnelnavn', u'Tunnelløp navn', u'Vegnummer', u'Tunnelløp ID', u'Fylke', 
    u'Kommune', u'Skiltet lengde tunnel', u'Lengde tunnelløp', 
    u'Antall parallelle hovedløp', 'AADT', u'Andel tunge kjøretøy', 
    u'Gjelder for år', u'Trafikkmengde ID',u'Enveg?',u'Kommentar', u'Lenke'
] 
csv_list.insert(0, csv_header)

csv_skriv('tunneler_med_trafikkmengde.csv', csv_list)
