#!/usr/bin/python -u
#
# -*- coding: utf-8 -*-
#
# make entity from chem_comp
#  just a wrapper for an SQL script really
# This needs the DB made and populated by cif2star, the 2 should probably be merged
#

from __future__ import absolute_import

import sys
import os
import psycopg2
import traceback
import re
import argparse

#
#
def insert_record( curs, compid, verbose = False ) :

    curs.execute( "alter sequence chem_comp.atomid_seq restart with 1" )

    sql = """insert into chem_comp."Entity" 
("Sf_category","Sf_framecode","Entry_ID","BMRB_code","Name","Type",
"Number_of_nonpolymer_components","Nonpolymer_comp_ID","Nonpolymer_comp_label",
"Paramagnetic","Formula_weight")
select 'entity','entity_'||"ID",'NEED_ACC_NO',"BMRB_code",
case when "Name" is null then 'entity_'||"ID" else "Name" end,
case when upper("Name")='WATER' then 'water' else 'non-polymer' end,
1,"ID",'chem_comp_'||"ID","Paramagnetic","Formula_weight"
from chem_comp."Chem_comp" where "ID"=%s"""

    if verbose : 
        sys.stdout.write( sql % (compid,) )
    curs.execute( sql, (compid,) )
    if verbose : 
        sys.stdout.write( ": %d\n" % (curs.rowcount,) )

    sql = """insert into chem_comp."Entity_common_name" ("Name","Type","Entry_ID")
select "Name",'BMRB','NEED_ACC_NO' from chem_comp."Chem_comp" where "ID"=%s"""

    if verbose : 
        sys.stdout.write( sql % (compid,) )
    curs.execute( sql, (compid,) )
    if verbose : 
        sys.stdout.write( ": %d\n" % (curs.rowcount,) )

    sql = """insert into chem_comp."Entity_systematic_name" ("Name","Naming_system","Entry_ID")
select "Name",'BMRB','NEED_ACC_NO' from chem_comp."Chem_comp" where "ID"=%s"""

    if verbose : 
        sys.stdout.write( sql % (compid,) )
    curs.execute( sql, (compid,) )
    if verbose : 
        sys.stdout.write( ": %d\n" % (curs.rowcount,) )

    sql = """insert into chem_comp."Entity_systematic_name" ("Name","Naming_system","Entry_ID")
select coalesce("Three_letter_code","ID"),'Three letter code','NEED_ACC_NO' from chem_comp."Chem_comp" where "ID"=%s"""

    if verbose : 
        sys.stdout.write( sql % (compid,) )
    curs.execute( sql, (compid,) )
    if verbose : 
        sys.stdout.write( ": %d\n" % (curs.rowcount,) )

    sql = """insert into chem_comp."Entity_comp_index" ("ID","Auth_seq_ID","Comp_ID","Comp_label","Entry_ID")
values (1,1,%s,%s,'NEED_ACC_NO')"""

    if verbose : 
        sys.stdout.write( sql % (compid,"chem_comp_" + compid) )
    curs.execute( sql, (compid,"chem_comp_" + compid) )
    if verbose : 
        sys.stdout.write( ": %d\n" % (curs.rowcount,) )

# non-polymer entities don't have entity_poly
#
#    sql = """insert into chem_comp."Entity_poly_seq" ("Mon_ID","Num","Comp_index_ID","Entry_ID")
#values(%s,1,1,'NEED_ACC_NO')"""
#
#    if verbose : print (sql % (compid)),
#    curs.execute( sql, (compid,) )
#    if verbose : print ":", curs.rowcount

# entity_atom_list is redundant for monomer entities like these
# and we don't know how to make it for polymer ones (unless they're all standard residues)
# it doesn't exist in ~97% of BMRB entries
#
#    sql = """insert into chem_comp."Entity_atom_list" ("Comp_index_ID","Comp_ID","Atom_ID","Entry_ID")
#select 1,"Comp_ID","Atom_ID",'NEED_ACC_NO' from chem_comp."Chem_comp_atom" where "Comp_ID"=%s
#order by "Atom_ID"
#"""
#
#    if verbose : 
#        sys.stdout.write( sql % (compid,) )
#    curs.execute( sql, (compid,) )
#    if verbose : 
#        sys.stdout.write( ": %d\n" % (curs.rowcount,) )
#

# entity_bond is intended for unusual bonds only in 3.1 schema. whatever that means
#
#"""insert into "Entity_bond" ("ID","Type","Value_order","Comp_index_ID_1","Comp_ID_1","Atom_ID_1"
#"Comp_index_ID_2","Comp_ID_2","Atom_ID_2","Entry_ID")
#select "ID","Type","Value_order",1,"Comp_ID","Atom_ID_1",1,"Comp_ID","Atom_ID_2",'NEED_ACC_NO'
#from chem_comp."Chem_comp_bond"
#"""




#
#
#
if __name__ == "__main__" :


    ap = argparse.ArgumentParser( description = "load/update ligand DB" )
    ap.add_argument( "-v", "--verbose", help = "print lots of messages to stdout", dest = "verbose",
        action = "store_true", default = False )
    ap.add_argument( "-d", "--dsn", help = "psycopg2 DSN", dest = "ligand_dsn", required = True )

    args = ap.parse_args()

    conn = psycopg2.connect( dsn )
    curs = conn.cursor()
    curs2 = conn.cursor()

    sql = """select "ID" from chem_comp."Chem_comp" where "ID" not in 
(select "Nonpolymer_comp_ID" from chem_comp."Entity")"""
    if args.verbose : 
        sys.stdout.write( sql )
        sys.stdout.write( "\n" )
    curs.execute( sql )
    while True :
        row = curs.fetchone()
        if row == None : break
        if args.verbose :
            sys.stdout.write( row[0] )
            sys.stdout.write( "\n" )
        try :
            curs2.execute( "begin" )
            insert_record( curs2, row[0], verbose = args.verbose )
            conn.commit()

        except :
            sys.stderr.write( "Rollback! Exception inserting %s" % (row[0],) )
            conn.rollback()
            traceback.print_exc()

    curs2.close()
    curs.close()
    conn.close()

# eof
#
