--
-- main table
--
insert into chem_comp."Chem_comp" (
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
"Sf_framecode" ) 

select 
id,
coalesce(name,id),
upper(type),
case when upper(pdbx_ambiguous_flag)='Y' then 'yes' else 'no' end,
--pdbx_initial_date,
--pdbx_modified_date,
CURRENT_DATE,
CURRENT_DATE,
pdbx_release_status,
pdbx_replaced_by,
pdbx_replaces,
one_letter_code,
three_letter_code,
number_atoms_all,
number_atoms_nh,
case when upper(mon_nstd_flag)='Y' then 'yes' else 'no' end,
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
case when upper(pdbx_model_coordinates_missing_flag)='Y' then 'yes' else 'no' end,
pdbx_ideal_coordinates_details,
case when upper(pdbx_ideal_coordinates_missing_flag)='Y' then 'yes' else 'no' end,
pdbx_model_coordinates_db_code,
pdbx_processing_site,
'NEED_ACC_NO',
'PDB',
'chem_comp',
'chem_comp' || id

from ligand_expo.chem_comp 
where pdbx_replaced_by is null and pdbx_subcomponent_list is null
and id not in (select "ID" from chem_comp."Chem_comp");

--
-- post-cooking: set inital and modified date on insert
--
update chem_comp."Chem_comp" set "BMRB_code"="ID" where "BMRB_code" is NULL;
update chem_comp."Chem_comp" set "PDB_code"="ID" where "PDB_code" is NULL;

--
--
--
insert into chem_comp."Chem_comp_descriptor" (
"Comp_ID",
"Descriptor",
"Type",
"Program",
"Program_version",
"Entry_ID")

select
comp_id,
descriptor,
type,
program,
program_version,
'NEED_ACC_NO'

from ligand_expo.pdbx_chem_comp_descriptor
where comp_id not in (select distinct "Comp_ID" from chem_comp."Chem_comp_descriptor");

--
-- post-cook: ideally we want the row where program = ALATIS but PDB doesn't have that
--
update chem_comp."Chem_comp" set "InChI_code"=
 (select distinct "Descriptor" from chem_comp."Chem_comp_descriptor" where upper("Type")='INCHI' and "Comp_ID"=chem_comp."Chem_comp"."ID" 
 and "Descriptor" is not NULL order by "Descriptor" limit 1)
where "InChI_code" is NULL;

update chem_comp."Chem_comp_descriptor" 
  set "Sf_ID"=(select "Sf_ID" from chem_comp."Chem_comp" where "ID"=chem_comp."Chem_comp_descriptor"."Comp_ID")
  where "Sf_ID" is NULL;

--
--
--
insert into chem_comp."Chem_comp_identifier" (
"Comp_ID",
"Identifier",
"Type",
"Program",
"Program_version",
"Entry_ID")

select
comp_id,
identifier,
type,
program,
program_version,
'NEED_ACC_NO'

from ligand_expo.pdbx_chem_comp_identifier
where comp_id not in (select distinct "Comp_ID" from chem_comp."Chem_comp_identifier");

--
update chem_comp."Chem_comp_identifier" 
  set "Sf_ID"=(select "Sf_ID" from chem_comp."Chem_comp" where "ID"=chem_comp."Chem_comp_identifier"."Comp_ID")
  where "Sf_ID" is NULL;

--
--
--

insert into chem_comp."PDBX_chem_comp_feature" (
"Comp_ID",
"Type",
"Value",
"Source",
"Support",
"Entry_ID" )

select
comp_id,
type,
value,
source,
support,
'NEED_ACC_NO'

from ligand_expo.pdbx_chem_comp_feature
where comp_id not in (select distinct "Comp_ID" from chem_comp."PDBX_chem_comp_feature");

--
update chem_comp."PDBX_chem_comp_feature" 
  set "Sf_ID"=(select "Sf_ID" from chem_comp."Chem_comp" where "ID"=chem_comp."PDBX_chem_comp_feature"."Comp_ID")
  where "Sf_ID" is NULL;

--
-- atoms
--
insert into chem_comp."Chem_comp_atom" (
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
"Entry_ID") 

select
comp_id,
atom_id,
alt_atom_id,
type_symbol,
pdbx_stereo_config,
charge,
partial_charge,
cast( pdbx_align as integer ),
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
pdbx_ordinal,
'NEED_ACC_NO'

from ligand_expo.chem_comp_atom 
where comp_id not in (select distinct "Comp_ID" from chem_comp."Chem_comp_atom");

--
-- post-cook take 2
--
update chem_comp."Chem_comp" set "Number_atoms_all"=
 (select count(*) from chem_comp."Chem_comp_atom" where "Comp_ID"=chem_comp."Chem_comp"."ID") 
 where "Number_atoms_all" is NULL;

update chem_comp."Chem_comp" set "Number_atoms_nh"=
 (select count(*) from chem_comp."Chem_comp_atom" where "Comp_ID"=chem_comp."Chem_comp"."ID" and "Type_symbol"<>'H') 
 where "Number_atoms_nh" is NULL;

update chem_comp."Chem_comp_atom" set "BMRB_code"="Atom_ID" where "BMRB_code" is NULL;

update chem_comp."Chem_comp_atom" set "PDB_atom_ID"="Atom_ID" where "PDB_atom_ID" is NULL;

update chem_comp."Chem_comp_atom" 
  set "Sf_ID"=(select "Sf_ID" from chem_comp."Chem_comp" where "ID"=chem_comp."Chem_comp_atom"."Comp_ID")
  where "Sf_ID" is NULL;

--
--
--
insert into chem_comp."Chem_comp_bond" (
"ID",
"Value_order",
"Atom_ID_1",
"Atom_ID_2",
"Aromatic_flag",
"Stereo_config",
"Ordinal",
"Comp_ID",
"Entry_ID")

select
pdbx_ordinal,
value_order,
atom_id_1,
atom_id_2,
pdbx_aromatic_flag,
pdbx_stereo_config,
pdbx_ordinal,
comp_id,
'NEED_ACC_NO'

from ligand_expo.chem_comp_bond 
where comp_id not in (select distinct "Comp_ID" from chem_comp."Chem_comp_bond");

--
-- post-cook take 3
--
update chem_comp."Chem_comp" set "Aromatic"=case when
 (select count(*) from chem_comp."Chem_comp_bond" where "Aromatic_flag"='yes' and "Comp_ID"=chem_comp."Chem_comp"."ID") > 0 
  then 'yes' else 'no' end
 where "Aromatic" is NULL;

update chem_comp."Chem_comp_bond" 
  set "Sf_ID"=(select "Sf_ID" from chem_comp."Chem_comp" where "ID"=chem_comp."Chem_comp_bond"."Comp_ID")
  where "Sf_ID" is NULL;

--
--
--
insert into chem_comp."Chem_comp_tor" (
"ID",
"Atom_ID_1",
"Atom_ID_2",
"Atom_ID_3",
"Atom_ID_4",
"Comp_ID",
"Entry_ID")

select
cast( id as integer ),
atom_id_1,
atom_id_2,
atom_id_3,
atom_id_4,
comp_id,
'NEED_ACC_NO'

from ligand_expo.chem_comp_tor 
where comp_id not in (select distinct "Comp_ID" from chem_comp."Chem_comp_tor");

--
--
--
insert into chem_comp."Chem_comp_angle" (
"Atom_ID_1",
"Atom_ID_2",
"Atom_ID_3",
"Comp_ID",
"Entry_ID")

select
atom_id_1,
atom_id_2,
atom_id_3,
comp_id,
'NEED_ACC_NO'

from ligand_expo.chem_comp_angle where 
comp_id not in (select distinct "Comp_ID" from chem_comp."Chem_comp_angle");


/*


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
        "Chem_comp",
        "Entity_common_name",
        "Entity_systematic_name",
        "Entity_comp_index",
        "Entity"
    ]

    #
    #
    @classmethod
    def convert( cls, dsn, create = False, verbose = False ) :

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
#        if create :
        cnv.verbose = True
        cnv.create_tables()

        return cnv

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

    # (re-)create NMR-STAR
    #
    def create_tables( self ) :

#        self._verbose = True
        curs = self._conn.cursor()
        ALLTABLES = self.STARTABLES[:]
        qry = "select tagcategory,min(dictionaryseq)" \
            + " from dict.adit_item_tbl" \
            + " where originalcategory in ('entity')" \
            + " group by tagcategory" \
            + " order by min(dictionaryseq)"
        curs.execute( qry )
        while True :
            row = curs.fetchone()
            if row is None : break
            ALLTABLES.append( row[0] )

# not sure why it's there
#
        ALLTABLES.append( "Upload_data" )

# drop
#
        curs.execute( "drop schema if exists chem_comp cascade" )
        curs.execute( "create schema chem_comp" )
        curs.execute( "create sequence chem_comp.bondid_seq" )
        curs.execute( "create sequence chem_comp.entityid_seq" )
        curs.execute( "create sequence chem_comp.sfid_seq" )

# recreate
#
        creat = 'create table chem_comp."%s" (%s)'
        cols = []
        qry = 'select tagfield,dbtype from dict.adit_item_tbl where tagcategory=%s order by dictionaryseq'
        for table in reversed( ALLTABLES ) :
            del cols[:]
            curs.execute( qry, (table,) )
            while True :
                row = curs.fetchone()
                if row is None : break

# dictionary uses boolean for what previously was yes/no char(3) but the values are still yes/no
# float: store as text so we don't have to worry about round-offs and significant digits
#
                if (row[1].lower() == "float") \
                or row[1].lower().startswith( "char" ) \
                or row[1].lower().startswith( "varchar" ) \
                or row[1].lower().startswith( "vchar" ) \
                or row[1].lower().startswith( "boolean" ) \
                or row[1].lower().startswith( "text" ) :
                    dbtype = "text"

                elif row[1].lower().startswith( "date" ) :
                    dbtype = "date"

                elif row[1].lower().startswith( "int" ) :
                    dbtype = "integer"

                else :
                    sys.stderr.write( "Unsupported DBTYPE %s for _%s.%s" % (row[1], table, row[0],) )
                    dbtype = "text"

                if (table == "Chem_comp_bond") and (row[0] == "ID") :
                    cols.append( '"%s" %s default nextval(\'chem_comp.bondid_seq\')' % (row[0],dbtype,) )
                elif (table == "Entity") and (row[0] == "ID") :
                    cols.append( '"%s" %s default nextval(\'chem_comp.entityid_seq\')' % (row[0],dbtype,) )
                elif row[0] == "Sf_ID" and (table in ("Entity","Chem_comp") ) :
                    cols.append( '"%s" %s default nextval(\'chem_comp.sfid_seq\')' % (row[0],dbtype,) )
                else :
                    cols.append( '"%s" %s' % (row[0],dbtype,) )

            if len( cols ) < 1 : raise Exception( "No columns for %s" % (table,) )

            colstr = ",".join( c for c in cols )
            sql = creat % (table,colstr)
            if self._verbose : sys.stdout.write( sql )
            curs.execute( sql )

# there's PK/FK info in the dictionary, in unknown state
#


        curs.execute( "commit" )
        curs.close()
#        self._verbose = False

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

            self._conn.commit()

        except :
            sys.stderr.write( "\nRollback! Exception %s %s\n\n" % (( insert and "inserting" or "updating"), compid,) )
            self._conn.rollback()
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
                else :
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


*/

