#!/usr/bin/python -u
#
# -*- coding: utf-8 -*-
#
# convert Ligand Expo from mmCIF to NMR-STAR 3.1 schema
#
# there is a tag map in NMR-STAR dictionary, 
# but in this case it's easier to not use it
#
# FIXME: I originally thought to use in-place updates but never got a round tuit
# so this only does delete + insert but some of the update code is still here.
# there are other left over partial refactorings that should be cleaned up too
#

from __future__ import absolute_import

import sys
from datetime import date
import psycopg2
import re
import traceback
import pprint
import argparse

#
# just a namespace wrapper
#
class Cif2Nmr( object ) :

    UNMAPPED_CIFTABLES = [
        "ligand_expo.chem_comp_chir",
        "ligand_expo.chem_comp_chir_atom",
        "ligand_expo.chem_comp_plane",
        "ligand_expo.chem_comp_plane_atom",
        "ligand_expo.chem_comp_tor_value",
        "ligand_expo.pdbx_chem_comp_atom_edit",
        "ligand_expo.pdbx_chem_comp_atom_feature",
        "ligand_expo.pdbx_chem_comp_audit",
        "ligand_expo.pdbx_chem_comp_bond_edit",
        "ligand_expo.pdbx_chem_comp_import",
        "ligand_expo.pdbx_chem_comp_synonyms"
    ]

#
# order is important b/c of foreign keys
#
    STARTABLES = [
        "Chem_comp_angle",
        "Chem_comp_tor",
        "Chem_comp_bond",
        "Chem_comp_atom",
        "PDBX_chem_comp_feature",
        "Chem_comp_identifier",
        "Chem_comp_descriptor",
        "Chem_comp"
    ]

    #
    #
    @classmethod
    def convert( cls, dsn, verbose = False ) :

        stats = { "total" : 0, "new" : 0, "updated" : 0, "conflicts" : 0 }

# where is redundant since we're not loading obsolete and compound ones
#
        cifqry = "select id,pdbx_initial_date,pdbx_modified_date from ligand_expo.chem_comp" \
                + " where pdbx_replaced_by is null and pdbx_subcomponent_list is null order by id"

        strqry = 'select "ID","Initial_date","Modified_date" from chem_comp."Chem_comp" where "ID"=%s'

        dbconnection = psycopg2.connect( dsn )
        cifcurs = dbconnection.cursor()
        strcurs = dbconnection.cursor()

        cnv = cls( conn = dbconnection, verbose = verbose )

        if verbose :
            sys.stdout.write( "%s\n" % (cifqry,) )

        cifcurs.execute( cifqry )
        while True :
            cifrow = cifcurs.fetchone()
            if cifrow is None : break

            if verbose :
                pprint.pprint( cifrow )

            stats["total"] += 1

            if verbose : 
                sys.stdout.write( "%s\n" % (strqry % (row1[0],),) )

            strcurs.execute( strqry, (cifrow[0],) )
            strrow = strcurs.fetchone()
            if strrow is None :
                cnv.update_record( cifrow[0], insert = True )
                stats["new"] += 1

#               break

            else :
                if verbose : 
                    pprint.pprint( strrow )
#
# The logic: BMRB comps start w/ initial date = modified date = the date comp was converted from pdbx
# if pdbx modified (or initial though that's unlikely) date > bmrb modified date, pdbx comp's been updated
#  if bmrb modified date == initial date, we didn't update our comp, it's ok to replace it with pdb's new version
#  otherwise generate an error message and have somebody see if there's a conflict & resolve it.
#
# And there can be nulls.
#
                try : 
                    if cifrow[1] is None : pdb_initial = date( 1970, 1, 1 )
                    else : pdb_initial = cifrow[1]
                    if cifrow[2] is None : pdb_modified = date( 1970, 1, 1 )
                    else : pdb_modified = cifrow[2]

                    if strrow[1] is None : bmrb_initial = date( 1970, 1, 1 )
                    else : bmrb_initial = strrow[1]
                    if strrow[2] is None : bmrb_modified = date( 1970, 1, 1 )
                    else : bmrb_modified = strrow[2]

                    if (pdb_initial > bmrb_modified) or (pdb_modified > bmrb_modified) :
                        stats["updated"] += 1
                        if bmrb_initial == bmrb_modified :
                            if verbose : 
                                sys.stdout.write( "Replacing %s\n" % (cifrow[0],) )
                            cnv.delete_chem_comp( cifrow[0] )
                            cnv.update_record( cifrow[0], insert = True )
                        else :
                            stats["conflicts"] += 1
                            sys.stderr.write( "Conflict in chem comp %s: PDB updated %s, BMRB updated %s\n" \
                                % (cifrow[0], pdb_modified, bmrb_modified,) )
                except :
                    sys.stderr.write( "Exception in PDB %s BMRB %s\n" % (cifrow[0],strrow[0],) )
                    raise

#               break


        dbconnection.commit()
        strcurs.close()
        cifcurs.close()
        dbconnection.close()

        pprint.pprint( stats )
        return cnv

    #
    #
    def __init__( self, conn, verbose = False ) :

        self._conn = conn
        self._verbose = bool( verbose )


    #
    #
    def delete_chem_comp( self, compid ) :

        curs = self._conn.cursor()
        curs.execute( "begin" )

        for table in self.STARTABLES :
            sql = "delete from chem_comp.\"%s\"" % (table)
            if table == "Chem_comp" : sql += " where \"ID\"=%s"
            else : sql += " where \"Comp_ID\"=%s"

            if self._verbose : 
                sys.stdout.write( sql % (compid,) )
            curs.execute( sql, (compid,) )
            if self._verbose : 
                sys.stdout.write( ": %d\n" % (curs.rowcount,) )

        curs.execute( "commit" )
        curs.close()

    # Update one chem. comp
    #
    def update_record( self, compid, insert = False ) :

        curs = self._conn.cursor()
        curs.execute( "begin" )
        try :
            self.update_chem_comp( compid, insert = insert )
            self.update_cc_descriptor( compid, insert = insert )
            self.update_cc_identifier( compid, insert = insert )
            self.update_cc_feature( compid, insert = insert )
            self.update_cc_atom( compid, insert = insert )
            self.update_cc_bond( compid, insert = insert )
            self.update_cc_tor( compid, insert = insert )
            self.update_cc_angle( compid, insert = insert )

# post-cook
#
            curs.execute( "update chem_comp.\"Chem_comp\" set \"BMRB_code\"=\"ID\" where \"ID\"=%s", (compid,) )
            curs.execute( "update chem_comp.\"Chem_comp\" set \"PDB_code\"=\"ID\" where \"ID\"=%s", (compid,) )

            curs.execute( "select count(*) from chem_comp.\"Chem_comp_atom\" where \"Comp_ID\"=%s", (compid,) )
            row = curs.fetchone()
            if row is None : raise Exception( "Null atom count in %s" % compid )
            if int( row[0] ) > 0 :
                curs.execute( "update chem_comp.\"Chem_comp\" set \"Number_atoms_all\"=%s where \"ID\"=%s", (row[0], compid,) )

            curs.execute( "select count(*) from chem_comp.\"Chem_comp_atom\" where \"Comp_ID\"=%s and \"Type_symbol\"<>'H'", (compid,) )
            row = curs.fetchone()
            curs.execute( "update chem_comp.\"Chem_comp\" set \"Number_atoms_nh\"=%s where \"ID\"=%s", (row[0], compid,) )

            curs.execute( "select count(*) from chem_comp.\"Chem_comp_bond\" where \"Aromatic_flag\"='yes' and \"Comp_ID\"=%s", (compid,) )
            row = curs.fetchone()
            if int( row[0] ) > 0 :
                curs.execute( "update chem_comp.\"Chem_comp\" set \"Aromatic\"='yes' where \"ID\"=%s", (compid,) )
            else :
                curs.execute( "update chem_comp.\"Chem_comp\" set \"Aromatic\"='no' where \"ID\"=%s", (compid,) )

            curs.execute( "update chem_comp.\"Chem_comp_atom\" set \"BMRB_code\"=\"Atom_ID\" where \"Comp_ID\"=%s", (compid,) )
            curs.execute( "update chem_comp.\"Chem_comp_atom\" set \"PDB_atom_ID\"=\"Atom_ID\" where \"Comp_ID\"=%s", (compid,) )

# FIXME: we want the one where "program"='ALATIS' but PDB doesn have that as of 2020-06-24
# just pick the top one
#
            curs.execute( "select distinct \"Descriptor\" from chem_comp.\"Chem_comp_descriptor\" where \"Type\"='InChI' and \"Comp_ID\"=%s", (compid,) )
            row = curs.fetchone()
            if row is not None :
                curs.execute( "update chem_comp.\"Chem_comp\" set \"InCHi_code\"=%s where \"ID\"=%s", (row[0], compid,) )
#        curs.execute( """update chem_comp.\"Chem_comp\" set \"InCHi_code\"=
#(select distinct \"Descriptor\" from chem_comp.\"Chem_comp_descriptor\" where \"Type\"='InChI' and \"Comp_ID\"=%s limit 1) 
#where \"ID\"=%s""",  (compid, compid,) )

# normalize to uppercase
#
            curs.execute( "update chem_comp.\"Chem_comp\" set \"Type\"=upper(\"Type\") where \"ID\"=%s", (compid,) )

# reset datestamps on new records
#
            if insert :
                curs.execute( "update chem_comp.\"Chem_comp\" set \"Initial_date\"=%s where \"ID\"=%s", (date.today(),compid,) )
                curs.execute( "update chem_comp.\"Chem_comp\" set \"Modified_date\"=%s where \"ID\"=%s", (date.today(),compid,) )

            conn.commit()

        except :
            sys.stderr.wriet( "\nRollback! Exception %s %s\n\n" % (( insert and "inserting" or "updating"), compid,) )
            conn.rollback()
            traceback.print_exc()

####################################################
    #
    # update one db table
    #
    def update_table( self, qry, sql, compid, insert = False ) :

        if self._verbose : 
            sys.stdout.write( "* %s\n" % (qry % (str( compid ),),) )

        vals = []
        curs = self._conn.cursor()
        curs2 = self._conn.cursor()
        curs.execute( qry, (compid,) )
        while True :
            del vals[:]
            row = curs.fetchone()
            if self._verbose: 
                pprint.pprint( row )
            if row is None : return
            for i in range( len( row ) ) :
                if row[i] is None : vals.append( None )
                val = str( row[i] ).strip()
                if val in ("", ".", "?") : vals.append( None )

# _flag tags
                elif curs.description[i][0][-5:] == "_flag" :
                    if val.upper() == "N" : vals.append( "no" )
                    elif val.upper() == "Y" : vals.append( "yes" )
                    else : vals.append( val )
                else : vals.append( val )

# if not insert, sql will end in "where comp_id=?"

            if not insert : vals.append( compid )

            if self._verbose : 
                sys.stdout.write( sql % tuple( vals ) )
            curs2.execute( sql, tuple( vals ) )
            if self._verbose : 
                sys.stdout.write( ": %d\n" % (curs2.rowcount,) )

        curs2.close()
        curs.close()

#########################################################
    #
    # "update" doesn't actually work on multi-row tables.
    #
    def update_chem_comp( self, compid, insert = False ) :

        qry = """select 
id,
coalesce(name,id),
type,
pdbx_ambiguous_flag,
pdbx_initial_date,
pdbx_modified_date,
pdbx_release_status,
pdbx_replaced_by,
pdbx_replaces,
one_letter_code,
three_letter_code,
number_atoms_all,
number_atoms_nh,
mon_nstd_flag,
mon_nstd_class,
mon_nstd_details,
mon_nstd_parent,
mon_nstd_parent_comp_id,
pdbx_synonyms,
pdbx_formal_charge,
formula,
formula_weight,
model_details,
model_erf,
model_source,
pdbx_model_coordinates_details,
pdbx_model_coordinates_missing_flag,
pdbx_ideal_coordinates_details,
pdbx_ideal_coordinates_missing_flag,
pdbx_model_coordinates_db_code,
pdbx_processing_site
    from ligand_expo.chem_comp where id=%s and pdbx_replaced_by is null and pdbx_subcomponent_list is null"""

        if insert :
            sql = """insert into chem_comp."Chem_comp" (
"ID",
"Name",
"Type",
"Ambiguous_flag",
"Initial_date",
"Modified_date",
"Release_status",
"Replaced_by",
"Replaces",
"One_letter_code",
"Three_letter_code",
"Number_atoms_all",
"Number_atoms_nh",
"Mon_nstd_flag",
"Mon_nstd_class",
"Mon_nstd_details",
"Mon_nstd_parent",
"Mon_nstd_parent_comp_ID",
"Synonyms",
"Formal_charge",
"Formula",
"Formula_weight",
"Model_details",
"Model_erf",
"Model_source",
"Model_coordinates_details",
"Model_coordinates_missing_flag",
"Ideal_coordinates_details",
"Ideal_coordinates_missing_flag",
"Model_coordinates_db_code",
"Processing_site",
"Entry_ID",
"Provenance",
"Sf_category",
"Sf_framecode"
        ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'NEED_ACC_NO','PDB','chem_comp',%s)"""

        else :
            sql = """update chem_comp."Chem_comp" set 
"ID"=%s,
"Name"=%s,
"Type"=%s,
"Ambiguous_flag"=%s,
"Initial_date"=%s,
"Modified_date"=%s,
"Release_status"=%s,
"Replaced_by"=%s,
"Replaces"=%s,
"One_letter_code"=%s,
"Three_letter_code"=%s,
"Number_atoms_all"=%s,
"Number_atoms_nh"=%s,
"Mon_nstd_flag"=%s,
"Mon_nstd_class"=%s,
"Mon_nstd_details"=%s,
"Mon_nstd_parent"=%s,
"Mon_nstd_parent_comp_ID"=%s,
"Synonyms"=%s, 
"Formal_charge"=%s,
"Formula"=%s,
"Formula_weight"=%s,
"Model_details"=%s,
"Model_erf"=%s,
"Model_source"=%s,
"Model_coordinates_details"=%s,
"Model_coordinates_missing_flag"=%s,
"Ideal_coordinates_details"=%s,
"Ideal_coordinates_missing_flag"=%s,
"Model_coordinates_db_code"=%s,
"Processing_site"=%s
        where "ID"=%s"""

        if self._verbose : 
            sys.stdout.write( qry % (compid,) )

        curs = conn.cursor()
        curs.execute( qry, (compid,) )
        row = curs.fetchone()
        if row is None : return
# raise Exception( "No ligand_expo.chem_comp row for %s" % (compid) )
        if self._verbose : 
            pprint.pprint( row )

        vals = []
        for i in range( len( row ) ) :
            val = row[i]
            if val is None : vals.append( None )
            val = str( val ).strip()
            if val  in ("", ".", "?") : vals.append( None )

# _flag tags: Y/N -> yes/no

            elif curs.description[i][0][-5:] == "_flag" :
                if val.upper() == "N" : vals.append( "no" )
                elif val.upper() == "Y" : vals.append( "yes" )
                else : vals.append( val )

            else : vals.append( val )

# framecode is the last one when inserting

        if insert : vals.append( "chem_comp_%s" % compid )
        else : vals.append( compid )
        if self._verbose : 
            sys.stdout.write( sql % tuple( vals ) )
        curs.execute( sql, tuple( vals ) )
        if self._verbose : 
            sys.stdout.write( ": %d\n" % (curs.rowcount,) )

        curs.close()

#############################################################
    #
    #
    def update_cc_descriptor( self, compid, insert = False ) :

        qry = """select
comp_id,
descriptor,
type,
program,
program_version
         from ligand_expo.pdbx_chem_comp_descriptor where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."Chem_comp_descriptor" (
"Comp_ID",
"Descriptor",
"Type",
"Program",
"Program_version",
"Entry_ID"
        ) values (%s,%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."Chem_comp_descriptor" set
"Comp_ID"=%s,
"Descriptor"=%s,
"Type"=%s,
"Program"=%s,
"Program_version"=%s
        where "Comp_ID"=%s"""

        self.update_table( qry, sql, compid, insert = insert )

######################################################################
    #
    #
    def update_cc_identifier( self, compid, insert = False ) :

        qry = """select
comp_id,
identifier,
type,
program,
program_version
         from ligand_expo.pdbx_chem_comp_identifier where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."Chem_comp_identifier" (
"Comp_ID",
"Identifier",
"Type",
"Program",
"Program_version",
"Entry_ID"
        ) values (%s,%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."Chem_comp_identifier" set
"Comp_ID"=%s,
"Identifier"=%s,
"Type"=%s,
"Program"=%s,
"Program_version"=%s
        where "Comp_ID"=%s"""

        self.update_table( qry, sql, compid, insert = insert )

########################################################################
    #
    #
    def update_cc_feature( self, compid, insert = False ) :
        qry = """select
comp_id,
type,
value,
source,
support
         from ligand_expo.pdbx_chem_comp_feature where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."PDBX_chem_comp_feature" (
"Comp_ID",
"Type",
"Value",
"Source",
"Support",
"Entry_ID"
        ) values (%s,%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."PDBX_chem_comp_feature" set
"Comp_ID"=%s,
"Type"=%s,
"Value"=%s,
"Source"=%s,
"Support"=%s
        where "Comp_ID"=%s"""

        self.update_table( qry, sql, compid, insert = insert )

##################################################################
    #
    #
    def update_cc_atom( self, compid, insert = False ) :
        qry = """select
comp_id,
atom_id,
alt_atom_id,
type_symbol,
pdbx_stereo_config,
charge,
partial_charge,
pdbx_align,
pdbx_aromatic_flag,
pdbx_leaving_atom_flag,
substruct_code,
model_cartn_x,
model_cartn_x_esd,
model_cartn_y,
model_cartn_y_esd,
model_cartn_z,
model_cartn_z_esd,
pdbx_model_cartn_x_ideal,
pdbx_model_cartn_y_ideal,
pdbx_model_cartn_z_ideal,
pdbx_ordinal
        from ligand_expo.chem_comp_atom where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."Chem_comp_atom" (
"Comp_ID",
"Atom_ID",
"Alt_atom_ID",
"Type_symbol",
"Stereo_config",
"Charge",
"Partial_charge",
"Align",
"Aromatic_flag",
"Leaving_atom_flag",
"Substruct_code",
"Model_Cartn_x",
"Model_Cartn_x_esd",
"Model_Cartn_y",
"Model_Cartn_y_esd",
"Model_Cartn_z",
"Model_Cartn_z_esd",
"Model_Cartn_x_ideal",
"Model_Cartn_y_ideal",
"Model_Cartn_z_ideal",
"PDBX_ordinal",
"Entry_ID"
        ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."Chem_comp_atom" set
"Comp_ID"=%s,
"Atom_ID"=%s,
"Alt_atom_ID"=%s,
"Type_symbol"=%s,
"Stereo_config"=%s,
"Charge"=%s,
"Partial_charge"=%s,
"Align"=%s,
"Aromatic_flag"=%s,
"Leaving_atom_flag"=%s,
"Substruct_code"=%s,
"Model_Cartn_x"=%s,
"Model_Cartn_x_esd"=%s,
"Model_Cartn_y"=%s,
"Model_Cartn_y_esd"=%s,
"Model_Cartn_z"=%s,
"Model_Cartn_z_esd"=%s,
"Model_Cartn_x_ideal"=%s,
"Model_Cartn_y_ideal"=%s,
"Model_Cartn_z_ideal"=%s,
"PDBX_ordinal"=%s
        where "Comp_ID"=%s"""

        if self._verbose : 
            sys.stdout.write( qry % (compid,) )
        vals = []
        curs = conn.cursor()
        curs2 = conn.cursor()

        curs.execute( qry, (compid,) )
        while True :
            row = curs.fetchone()
            if row is None : return
            del vals[:]
            for i in range( len( row ) ) :
                if row[i] is None : vals.append( None )
                val = str( row[i] ).strip()
                if val in ("", ".", "?") : vals.append( None )

# _flag tags

                elif curs.description[i][0][-5:] == "_flag" :
                    if val.upper() == "N" : vals.append( "no" )
                    elif val.upper() == "Y" : vals.append( "yes" )
                    else : vals.append( val )
                else : vals.append( val )

            if not insert : vals.append( compid )

            if self._verbose : 
                sys.stdout.write( sql % tuple( vals ) )
            curs2.execute( sql, tuple( vals ) )
            if self._verbose : 
                sys.stdout.write( ": %d\n" % (curs2.rowcount,) )

        curs2.close()
        curs.close()

####################################################################
    #
    #
    def update_cc_bond( self, compid, insert = False ) :

        qry = """select
value_order,
atom_id_1,
atom_id_2,
pdbx_aromatic_flag,
pdbx_stereo_config,
pdbx_ordinal,
comp_id
        from ligand_expo.chem_comp_bond where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."Chem_comp_bond" (
"Value_order",
"Atom_ID_1",
"Atom_ID_2",
"Aromatic_flag",
"Stereo_config",
"Ordinal",
"Comp_ID",
"Entry_ID"
        ) values (%s,%s,%s,%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."Chem_comp_bond" set
"Value_order"=%s,
"Atom_ID_1"=%s,
"Atom_ID_2"=%s,
"Aromatic_flag"=%s,
"Stereo_config"=%s,
"Ordinal"=%s,
"Comp_ID"=%s
        where "Comp_ID"=%s"""

        if self._verbose : 
            sys.stdout.write( qry % (compid,) )
            sys.stdout.write( "\n" )

        vals = []
        curs = conn.cursor()

# reset bond numbers (mmCIF doesn; thave 'em)
#
        curs.execute( "alter sequence chem_comp.bondid_seq restart with 1" )

        curs2 = conn.cursor()

        curs.execute( qry, (compid,) )
        while True :
            row = curs.fetchone()
            if row is None : return
# raise Exception( "No ligand_expo.chem_comp row for %s" % (compid) )

            del vals[:]
            for i in range( len( row ) ) :
                if row[i] is None : vals.append( None )
                val = str( row[i] ).strip()
                if val in ("", ".", "?") : vals.append( None )

# _flag tags

                elif curs.description[i][0][-5:] == "_flag" :
                    if val.upper() == "N" : vals.append( "no" )
                    elif val.upper() == "Y" : vals.append( "yes" )
                    else : vals.append( val )
                else : vals.append( val )

            if not insert : vals.append( compid )

            if self._verbose : 
                sys.stdout.write( sql % tuple( vals ) )
            curs2.execute( sql, tuple( vals ) )
            if self._verbose : 
                sys.stdout.write( ": %d\n" % (curs2.rowcount,) )

            curs2.execute( """update chem_comp."Chem_comp_bond" set "ID"="Ordinal" where "Comp_ID"=%s""", (compid,) )

            curs2.close()
            curs.close()

###################################################################
    #
    #
    def update_cc_tor( self, compid, insert = False ) :
        qry = """select
id,
atom_id_1,
atom_id_2,
atom_id_3,
atom_id_4,
comp_id
        from ligand_expo.chem_comp_tor where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."Chem_comp_tor" (
"ID",
"Atom_ID_1",
"Atom_ID_2",
"Atom_ID_3",
"Atom_ID_4",
"Comp_ID",
"Entry_ID"
        ) values ( %s%s,%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."Chem_comp_tor" set
"ID"=%s,
"Atom_ID_1"=%s,
"Atom_ID_2"=%s,
"Atom_ID_3"=%s,
"Atom_ID_4"=%s,
"Comp_ID"=%s
        where "Comp_ID"=%s"""

        self.update_table( qry, sql, compid, insert = insert )

####################################################################
    #
    #
    def update_cc_angle( self, compid, insert = False ) :

        qry = """select
atom_id_1,
atom_id_2,
atom_id_3,
comp_id
        from ligand_expo.chem_comp_angle where comp_id=%s"""

        if insert :
            sql = """insert into chem_comp."Chem_comp_angle" (
"Atom_ID_1",
"Atom_ID_2",
"Atom_ID_3",
"Comp_ID",
"Entry_ID"
        ) values (%s,%s,%s,%s,'NEED_ACC_NO')"""

        else :
            sql = """update chem_comp."Chem_comp_angle" set
"Atom_ID_1"=%s,
"Atom_ID_2"=%s,
"Atom_ID_3"=%s,
"Comp_ID"=%s
        where "Comp_ID"=%s"""

#Unmapped: ['value_angle', 'value_angle_esd', 'value_dist', 'value_dist_esd']
        self.update_table( qry, sql, compid, insert = insert )

#
# this is for finding unmapped columns
#
#def map_tags( curs, src, dst ) :
#    sql = "select * from %s limit 1" % (src)
#    srccols = []
#    curs.execute( sql )
#    row = curs.fetchone()
#    for i in curs.description : srccols.append( i[0] )
#
#    sql = "select * from \"%s\" limit 1" % (dst)
#    cols = {}
#    curs.execute( sql )
#    row = curs.fetchone()
#    for i in curs.description : 
#        for j in srccols :
#            if j.lower() == i[0].lower() :
#                cols[j] = i[0]
#                srccols.remove( j )
#                break
#    print "Map:", cols
#    print "Unmapped:", srccols

#
#
#
if __name__ == "__main__" :

    ap = argparse.ArgumentParser( description = "convert ligand DB from mmCIF to NMR-STAR" )
    ap.add_argument( "-v", "--verbose", help = "print lots of messages to stdout", dest = "verbose",
        action = "store_true", default = False )
    ap.add_argument( "-d", "--dsn", help = "psycopg2 DSN", dest = "ligand_dsn", required = True )

    args = ap.parse_args()

    cnv = Cif2Nmr.convert( dsn = args.ligand_dsn, verbose = args.verbose )

#
#
