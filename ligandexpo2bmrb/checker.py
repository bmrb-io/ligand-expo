#!/usr/bin/python -u
#
# -*- coding: utf-8 -*-
#
# Read modified date from mmCIF
#

from __future__ import absolute_import

import sys
import os
import re
import datetime
#import traceback

try :
    import sas
except ImportError :
    sys.path.append( "/projects/BMRB/SAS/python" )
    import sas

#
# 
#
class UpdateChecker( sas.ContentHandler, sas.ErrorHandler ) :

    """Extract pdbx initial and modified dates, replaced by and subcomponent list. 
    Either date will do (it's an error if both are missing). For subcomponent list and 
    replaced by we only care if they exits: if they do, the chem comp is 'compound' or 
    obsolete -- we don't want either."""

    @classmethod
    def read_file( cls, filename, verbose = False ) :

        rc = None
        with open( os.path.realpath( filename ), "rU" ) as f :
            rc = cls.read( fp = f, verbose = verbose )

        return rc

    @classmethod
    def read( cls, fp, verbose = False ) :
        chk = cls( verbose = verbose )
        lex = sas.StarLexer( fp, bufsize = 0, verbose = verbose )
        p = sas.CifParser.parse( lexer = lex, content_handler = chk, error_handler = chk, verbose = verbose )
        return chk

    #
    #
    def __init__( self, verbose = False ) :
        self._verbose = bool( verbose )
        self._re_date = re.compile( r"^(\d{4})-(\d{1,2})-(\d{1,2})$" ) # 2011-05-31
        self._modified = None
        self._initial = None
        self._compound = False
        self._obsolete = False
        self._errs = False
        self._blockid = ""

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

    @property
    def initial_date( self ) :
        return self._initial

    @property
    def modified_date( self ) :
        return self._modified

    @property
    def is_compound( self ) :
        return self._compound

    @property
    def is_obsolete( self ) :
        return self._obsolete

    @property
    def __data__( self ) :
        return {
            "id" : self._blockid,
            "created" : self._initial,
            "modified" : self._modified,
            "obsolete" : self._obsolete,
            "compound" : self._compound,
            "error" : self._errs
        }

# SAS callbacks
#
    def fatalError( self, line, msg ) :
        sys.stderr.write( "ERR: fatal parse error in line %d: %s\n" % (line, msg,) )
        self._errs = True

    def error( self, line, msg ) :
        sys.stderr.write( "ERR: parse error in line %d: %s\n" % (line, msg,) )
        self._errs = True
        return True

    # warnings are errors
    #
    def warning( self, line, msg ) :
        sys.stderr.write( "ERR: parse warning in line %d: %s\n" % (line, msg,) )
        self._errs = True
        return True

#
#
    def comment( self, line, text ) :
        return False
    def startSaveFrame( self, line, name ) :
        return False
    def endSaveFrame( self, line, name ) :
        return False
    def endData( self, line, name ) :
        pass
    def startLoop( self, line ) :
        return False
    def endLoop( self, line ) :
        return False

# 
#
    def startData( self, line, name ) :
        self._blockid = name
        return False

    #
    #
    def data( self, tag, tagline, val, valline, delim, inloop ) :
        if self._verbose :
            sys.stdout.write( "Data: %s - %s\n" % (tag,val,) )

        if (val is None) or (str( val ).strip() in ("", ".", "?",)) :
            val = None

        if tag == "_chem_comp.pdbx_initial_date" :
            if self._verbose :
                sys.stdout.write( "initial date (raw): %s\n" % (val,) )
            if val is None :
                self._initial = None
                return False
            m = self._re_date.search( val )
            if not m :
                sys.stderr.write( "ERR: Invalid initial date: %s\n" % (val,) )
                self._initial = None
                return False
            if (len( m.group( 2 ) ) < 2) or (len( m.group( 3 ) ) < 2) :
                sys.stderr.write( "WARN: bad initial date format: %s (%s)\n" % (val, self._blockid) )
            self._initial = datetime.date( int( m.group( 1 ) ), int( m.group( 2 ) ), int( m.group( 3 ) ) )
            if self._verbose : 
                sys.stdout.write( "initial date (parsed): %s\n" % (self._initial,) )
            return False

        if tag == "_chem_comp.pdbx_modified_date" :
            if val is None :
                self._modified = None
                return False
            m = self._re_date.search( val )
            if not m :
                sys.stderr.write( "ERR: Invalid last-modified date: %s\n" % (val,) )
                self._modified = None
                return False
            self._modified = datetime.date( int( m.group( 1 ) ), int( m.group( 2 ) ), int( m.group( 3 ) ) )
            if self._verbose : 
                sys.stdout.write( "modified date (parsed): %s\n" % (self._modified,) )
            return False

# don't care what it was repalced with, just that it's no longer current
#
        if tag == "_chem_comp.pdbx_replaced_by" :
            if val is not None :
                self._obsolete = True
            return False

        if tag == "_chem_comp.pdbx_release_status" :
            if str( val ).strip().upper() in ("OBS","WDRN",) :
                self._obsolete = True
            return False

# ditto for subcomponents
#
        if tag == "_chem_comp.pdbx_subcomponent_list" :
            if val is not None :
                self._compound = True
            return False

# done with metadata
#  could probably ingnore errors if it's obsolete or compound
#
        if tag [:16] == "_chem_comp_atom." : 
            if (self._initial is None) and (self._modified is None) :
                sys.stderr.write( "ERR: Chem comp %s has neither inital nor modified date\n" % (self._blockid,) )
                self._errs = True
                return True
            return False

        return False

#
#

#
#
#
if __name__ == "__main__" :

    import pprint
    chk = UpdateChecker.read_file( sys.argv[1] )
    pprint.pprint( chk.__data__ )

# eof
#
