#!/usr/bin/python -u
#
# -*- coding: utf-8 -*-
#
# check BMRB entries for unknown chem. comps
# it's easy with "bmrbeverything" database 
#

from __future__ import absolute_import

import sys
import psycopg2
import argparse

#
#
#
if __name__ == "__main__" :

    ap = argparse.ArgumentParser( description = "load/update ligand DB" )
    ap.add_argument( "-v", "--verbose", help = "print lots of messages to stdout", dest = "verbose",
        action = "store_true", default = False )
    ap.add_argument( "-d", "--dsn", help = "BMRB 'everything' database (pycopg2 DSN)", dest = "dsn", required = True )

    args = ap.parse_args()

    db = psycopg2.connect( args.dsn )
    curs = db.cursor()

    qry = 'select distinct "ID",cast("Entry_ID" as numeric)' \
        + ' from macromolecules."Chem_comp"' \
        + ' where "ID" not in (select distinct "ID" from chemcomps."Chem_comp")' \
        + ' order by cast("Entry_ID" as numeric)'

    curs.execute( qry )
    while True :
        row = curs.fetchone()
        if row is None : break
        cnt += 1
        sys.stdout.write( "%s : %s\n" % tuple( row ) )

    curs.close()
    db.close()

    sys.stdout.write( "BMRB chem comps not in Ligand Expo: %d\n" % (cnt,) )

# eof
#
