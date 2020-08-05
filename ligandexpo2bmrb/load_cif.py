#!/usr/bin/python -u
#
# -*- coding: utf-8 -*-
#
# Load Ligand Expo data into pdbx(-ish) schema
# 
#

from __future__ import absolute_import

import sys
import os
import psycopg2
import re
import traceback
import pprint
import argparse

try :
    import sas
except ImportError :
    sys.path.append( "/projects/BMRB/SAS/python" )
    import sas

from checker import UpdateChecker

#
#
#
class CifLoader( sas.ContentHandler, sas.ErrorHandler ) :

# mmcif db tables
# create with `psql .. -f PDBX.sql` beforehand
# order is important: foreign keys
#
    TABLES = [
        "chem_comp_angle",
        "chem_comp_bond",
        "chem_comp_chir",
        "chem_comp_chir_atom",
        "chem_comp_plane",
        "chem_comp_plane_atom",
        "chem_comp_tor",
        "chem_comp_tor_value",
        "pdbx_chem_comp_atom_edit",
        "pdbx_chem_comp_atom_feature",
        "pdbx_chem_comp_audit",
        "pdbx_chem_comp_bond_edit",
        "pdbx_chem_comp_descriptor",
        "pdbx_chem_comp_feature",
        "pdbx_chem_comp_identifier",
        "pdbx_chem_comp_import",
        "chem_comp_atom",
        "chem_comp"
    ]

    #
    #
    @classmethod
    def update_chem_comps( cls, ligand_dir, dsn, verbose = False ) :

        cifdir = os.path.realpath( ligand_dir )
        if not os.path.isdir( cifdir ) : 
            raise IOError( "Not found/not a dir: %s" % (cifdir,) )

        db = psycopg2.connect( dsn )
        curs = db.cursor()
        curs2 = db.cursor()
        qry = "select pdbx_initial_date,pdbx_modified_date from ligand_expo.chem_comp where upper(id)=%s"

        ldr = cls( curs = curs2, verbose = verbose )

# keep IDs for clean-up later
#
        compids = []
        stats = { "total" : 0, "new" : 0, "updated" : 0, "obsolete" : 0, "compound" : 0, "failed" : 0 }

        for (root, dirs, files) in os.walk( cifdir ) :
            if "FULL" in dirs :
                dirs.remove( "FULL" )
            if "REMOVED" in dirs :
                dirs.remove( "REMOVED" )

            for comp in files :
                (compid, ext) = os.path.splitext( comp )
                if ext != ".cif" : continue
                compid = str( compid ).upper()

                infile = os.path.join( root, comp )

                chk = UpdateChecker.read_file( filename = infile, verbose = False ) # verbose )
                if verbose :
                    sys.stdout.write( "CC: %s in %s-%s\n" % (compid,root,comp,) )
                    pprint.pprint( chk.__data__ )

                stats["total"] += 1
                if chk.has_errors :
                    stats["failed"] += 1
                    sys.stderr.write( "Errors parsing %s\n" % (filename,) )
                    continue
                if chk.is_compound :
                    stats["compound"] += 1
                    continue
                if chk.is_obsolete :
                    stats["obsolete"] += 1
                    continue

                compids.append( compid )
                updated = False
                if verbose : 
                    sys.stdout.write( qry % (compid,) )
                    sys.stdout.write( "\n" )

                curs.execute( qry, (compid,) )
                row = curs.fetchone()
                if verbose : 
                    pprint.pprint( row )
                if row is None : 
                    updated = True
                    stats["new"] += 1
                else :
                    if chk.modified_date is not None :
                        if row[1] is not None :
                            if chk.modified_date > row[1] : updated = True
                        else : updated = True
                    else :
                        if chk.initial_date is not None :
                            if row[0] is not None :
                                if chk.initial_date > row[0] : updated = True
                            else : updated = True
                        else :
                            sys.stderr.write( "This should never happen: chem comp %s has no dates and we got here" % (compid,) )

                if updated :
                    if verbose : 
                        sys.stdout.write( "-- updated, loading\n" )
                    for table in CifLoader.TABLES :
                        if table != "chem_comp" :
                            sql = "delete from ligand_expo.%s " % (table,)
                            sql += "where upper(comp_id)=%s"
                            if verbose : 
                                sys.stdout.write( sql % (compid,) )
                            curs.execute( sql, (compid,) )
                            if verbose : 
                                sys.stdout.write( " : %d\n" % (curs.rowcount,) )
                    sql = "delete from ligand_expo.chem_comp where upper(id)=%s"
                    if verbose : 
                        sys.stdout.write( sql % (compid,) )
                    curs.execute( sql, (compid,) )
                    if verbose : 
                        sys.stdout.write( " : %d\n" % (curs.rowcount,) )

                    with open( infile, "rU" ) as inf :
                        lex = sas.StarLexer( inf, bufsize = 0, verbose = verbose )
                        curs.execute( "begin" )
                        try :
                            p = sas.CifParser.parse( lexer = lex, content_handler = ldr, error_handler = ldr, verbose = verbose )
                        except :
                            curs.execute( "rollback" )
                            sys.stderr.write("ERR: Rollback in %s: Exception:\n" % (infile) )
                            pprint.pprint( sys.exc_info() )
                            traceback.print_exc()

                    compids.append( compid )
                    if ldr.has_errors :
                        sys.stderr.write( "ERR: Rollback: errors in %s\n" % (compid,) )
                        curs.execute( "rollback" )
                    else :
                        curs.execute( "commit" )
                        if verbose : sys.stdout-write( "--- Committed\n" )
                        compids.append( compid )

        curs2.close()
# done updating, collect garbage
#
        obsolete = []
        idstr = "','".join( i for i in compids )
        qry = "select upper(id) from ligand_expo.chem_comp where upper(id) not in ('%s')" % (idstr,)
        curs.execute( qry )
        while True :
            row = curs.fetchone()
            if row is None : break
            obsolete.append( row[0] )

        stats["obsolete"] = len( obsolete )

# "on delete cascade" should take care of child tables
#
        idstr = "','".join( i for i in obsolete )
        sql = "delete from ligand_expo.chem_comp where upper(id) in ('%s')" % (idstr,)
        curs.execute( sql )
#        if verbose :
        sys.stdout.write( "%s : %d rows\n" % (sql,curs.rowcount) )

        sql = """delete from chem_comp."Chem_comp" where "ID" in ('%s')""" % (idstr,)
        curs.execute( sql )
#        if verbose :
        sys.stdout.write( "%s : %d rows\n" % (sql,curs.rowcount) )

        curs.close()
        db.close()
        pprint.pprint( stats )

    #
    #
    def __init__( self, curs, verbose = False ) :
        self._curs = curs
        self._verbose = bool( verbose )
        self._re_flag = re.compile( ".+_flag$" )
        self._blockid = ""
        self._sfname = ""
        self._table = ""
        self._first_tag = ""
        self._row = -1
        self._data = {}
        self._types = {}
        self._errs = False

    @property
    def verbose( self ) :
        """verbose flag"""
        return bool( self._verbose )
    @verbose.setter
    def verbose( self, flag ) :
        self._verbose = bool( flag )

    @property
    def has_errors( self ) :
        return self._errs


# callbacks
#
    def fatalError( self, line, msg ) :
        sys.stderr.write( "ERR: fatal parse error in line %d: %s\n" % (line,msg,) )
        self._errs = True

    def error( self, line, msg ) :
        sys.stderr.write( "ERR: parse error in line %d: %s\n" % (line,msg,) )
        self._errs = True
        return True

    def warning( self, line, msg ) :
        sys.stderr.write( "ERR: parse warning in line %d: %s\n" % (line,msg,) )
        self._errs = True
        return True

    def comment( self, line, text ) :
        return False
    def startSaveFrame( self, line, name ) :
        return False
    def endSaveFrame( self, line, name ) :
        return False

# real ones
#
    # just in case: bomb out if there's a 2nd data block
    # comp ids are all caps
    #
    def startData( self, line, name ) :
        if self._blockid != "" : return True
        if self._verbose : 
            sys.stdout.write( "++ data block %s\n" % (name,) )
        self._blockid = name.upper()
        return False

    def endData( self, line, name ) :
        if len( self._data ) > 0 :
            self._commit_row()
        self._blockid = ""
        self._table = ""
        self._first_tag = ""
        self._row = -1
        self._data = {}
        self._types = {}

    def startLoop( self, line ) :
        if len( self._data ) > 0 :
            if self._verbose : 
                sys.stdout.write( "start loop in line %d, sizeof data = %d\n" % (line,len( self._data )) )
            self._commit_row()
        self._table = ""
        self._first_tag = ""
        self._row = -1
        self._data = {}
        self._types = {}
        return False

    def endLoop( self, line ) :
        return False

    def data( self, tag, tagline, val, valline, delim, inloop ) :

# In CIF
#   parser fakes start/end and fires the callbacks for loops, but not for free tags.
# There may be
#   free tag after free tag but different table, or
#   free tag after free tag, same table
#
        if self._verbose : 
            sys.stdout.write( "%s : %s @ %d\n" % (tag, val, tagline) )
        table = tag.split( "." )[0].lstrip( "_" )
        col = tag.split( "." )[1]

# skip unmapped tables
#
        if not table in self.TABLES : return False

        if (table == "chem_comp") and (col == "id") : val = val.upper()
        if col == "comp_id" : val = val .upper()

        if self._table == "" :
            self._table = table
            self._first_tag = tag
            if self._verbose : 
                sys.stdout.write( "* 1st table %s (%s)\n" % (self._table, self._first_tag) )
        elif self._table != table :
            if self._verbose : 
                sys.stdout.write( "** new table %s (was %s), 1st tag: %s\n" % (table, self._table, tag) )
            self._commit_row()
            self._table = table
            self._first_tag = tag
            self._data = {}
            self._types = {}
# same table
        if inloop :
            if self._first_tag == tag :
                self._row += 1
                if len( self._data ) > 0 :
                    if self._verbose : 
                        sys.stdout.write( "new loop row\n" )
                    self._commit_row()
                    self._data = {}

        self._data[col] = val

        return False

    #
    #
    def _fetch_types( self ) :
        if self._verbose : 
            sys.stdout.write( "_fetch_types()\n" )
            pprint.pprint( self._data )
        sql = "select " + ",".join( self._data.keys() ) \
            + " from ligand_expo." + self._table + " limit 1"
        self._curs.execute( sql )
        for i in range( 0, len( self._curs.description ) ) :
            self._types[self._curs.description[i][0]] = self._curs.description[i][1]

        if self._verbose : 
            sys.stdout.write( "%s \n" % (sql,) )
            pprint.pprint( self._types )

#
#
    def _commit_row( self ) :

        if len( self._types ) < 1 : self._fetch_types()

        if self._verbose : 
            sys.stdout.write( "commit row\n" )
            pprint.pprint( self._data )
            pprint.pprint( self._types )

        sql = "insert into ligand_expo." + self._table + " (" + ",".join( self._data.keys() ) + ") values ("

        vals = []
        for i in self._data.keys() :
            sql += "%s,"
            if (self._data[i] == ".") or (self._data[i] == "?") : vals.append( None )
            else :
                if self._types[i.lower()] == psycopg2.NUMBER :
                    x = float( self._data[i] )   # check (will throw exception)
                vals.append( self._data[i] )
        sql = sql.rstrip( "," )
        sql += ")"
        if self._verbose : 
            sys.stdout.write( sql % tuple( vals ) )
            sys.stdout.write( "\n" )
        try : self._curs.execute( sql, tuple( vals ) )
        except :
            print "Exception!"
            sys.stderr.write( sql % tuple( vals ) )
            sys.stderr.write( "\n" )
            raise

#
#
#
#
#
#
if __name__ == "__main__" :

    ap = argparse.ArgumentParser( description = "load/update ligand DB" )
    ap.add_argument( "-v", "--verbose", help = "print lots of messages to stdout", dest = "verbose",
        action = "store_true", default = False )
    ap.add_argument( "-i", "--input", help = "input directory", dest = "ligand_dir", required = True )
    ap.add_argument( "-d", "--dsn", help = "psycopg2 DSN", dest = "ligand_dsn", required = True )

    args = ap.parse_args()

    rc = CifLoader.update_chem_comps( ligand_dir = args.ligand_dir, dsn = args.ligand_dsn, verbose = args.verbose )


# eof
#
