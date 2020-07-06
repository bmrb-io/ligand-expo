--
-- NMR-STAR tables for ligand expo
--
-- normally NMR-STAR tables are built for the dictionary
-- however there are several reasons why having a DDL script for these here
--  is a better option
--
--

drop schema if exists chem_comp cascade;
create schema chem_comp;

--
-- SF IDs are DB-global
--
create sequence chem_comp.sfid_seq
    start with 1
    increment by 1
    no minvalue
    no maxvalue
    cache 1;

CREATE TABLE chem_comp."Chem_comp" (
    "Sf_category" text not null default 'chem_comp',
    "Sf_framecode" text,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Sf_ID" integer DEFAULT nextval('chem_comp.sfid_seq'),
    "ID" text primary key,
    "Provenance" text,
    "Name" text,
    "Type" text,
    "BMRB_code" text,
    "PDB_code" text,
    "Ambiguous_flag" text,
    "Initial_date" date,
    "Modified_date" date,
    "Release_status" text,
    "Replaced_by" text,
    "Replaces" text,
    "One_letter_code" text,
    "Three_letter_code" text,
    "Number_atoms_all" integer,
    "Number_atoms_nh" integer,
    "Atom_nomenclature_source" text,
    "PubChem_code" text,
    "Subcomponent_list" text,
    "InChI_code" text,
    "Mon_nstd_flag" text,
    "Mon_nstd_class" text,
    "Mon_nstd_details" text,
    "Mon_nstd_parent" text,
    "Mon_nstd_parent_comp_ID" text,
    "Std_deriv_one_letter_code" text,
    "Std_deriv_three_letter_code" text,
    "Std_deriv_BMRB_code" text,
    "Std_deriv_PDB_code" text,
    "Std_deriv_chem_comp_name" text,
    "Synonyms" text,
    "Formal_charge" text,
    "Paramagnetic" text,
    "Aromatic" text,
    "Formula" text,
    "Formula_weight" text,
    "Formula_mono_iso_wt_nat" text,
    "Formula_mono_iso_wt_13C" text,
    "Formula_mono_iso_wt_13C_15N" text,
    "Image_file_name" text,
    "Image_file_format" text,
    "Topo_file_name" text,
    "Topo_file_format" text,
    "Struct_file_name" text,
    "Struct_file_format" text,
    "Stereochem_param_file_name" text,
    "Stereochem_param_file_format" text,
    "Model_details" text,
    "Model_erf" text,
    "Model_source" text,
    "Model_coordinates_details" text,
    "Model_coordinates_missing_flag" text,
    "Ideal_coordinates_details" text,
    "Ideal_coordinates_missing_flag" text,
    "Model_coordinates_db_code" text,
    "Processing_site" text,
    "Vendor" text,
    "Vendor_product_code" text,
    "Details" text,
    "DB_query_date" date,
    "DB_last_query_revised_last_date" date
);

CREATE TABLE chem_comp."Chem_comp_atom" (
    "Atom_ID" text,
    "BMRB_code" text,
    "PDB_atom_ID" text,
    "Alt_atom_ID" text,
    "Auth_atom_ID" text,
    "Type_symbol" text,
    "Isotope_number" integer,
    "Chirality" text,
    "Stereo_config" text,
    "Charge" text,
    "Partial_charge" text,
    "Oxidation_number" text,
    "Unpaired_electron_number" integer,
    "Align" integer,
    "Aromatic_flag" text,
    "Leaving_atom_flag" text,
    "Substruct_code" text,
    "Ionizable" text,
    "Drawing_2D_coord_x" text,
    "Drawing_2D_coord_y" text,
    "Model_Cartn_x" text,
    "Model_Cartn_x_esd" text,
    "Model_Cartn_y" text,
    "Model_Cartn_y_esd" text,
    "Model_Cartn_z" text,
    "Model_Cartn_z_esd" text,
    "Model_Cartn_x_ideal" text,
    "Model_Cartn_y_ideal" text,
    "Model_Cartn_z_ideal" text,
    "PDBX_ordinal" integer,
    "Details" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Comp_ID" text not null,
    primary key ("Comp_ID", "Atom_ID"),
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

--
-- 
--
CREATE TABLE chem_comp."Chem_comp_bond" (
    "ID" integer,
    "Type" text,
    "Value_order" text,
    "Atom_ID_1" text,
    "Atom_ID_2" text,
    "Aromatic_flag" text,
    "Stereo_config" text,
    "Ordinal" integer,
    "Details" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NO_ACC_NUM',
    "Comp_ID" text not null,
    primary key ("Comp_ID", "ID"),
    unique("Comp_ID","Atom_ID_1", "Atom_ID_2"),
    foreign key ("Comp_ID","Atom_ID_1") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID","Atom_ID_2") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

--
-- there doesn't seem to be any data in this one
--
CREATE TABLE chem_comp."Chem_comp_angle" (
    "ID" integer,
    "Atom_ID_1" text,
    "Atom_ID_2" text,
    "Atom_ID_3" text,
    "Details" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Comp_ID" text not null,
    primary key ("Comp_ID", "ID"),
    unique ("Atom_ID_1", "Atom_ID_2","Atom_ID_3"),
    foreign key ("Comp_ID","Atom_ID_1") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID","Atom_ID_2") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID","Atom_ID_3") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

--
-- or this one
--
CREATE TABLE chem_comp."Chem_comp_tor" (
    "ID" integer,
    "Atom_ID_1" text,
    "Atom_ID_2" text,
    "Atom_ID_3" text,
    "Atom_ID_4" text,
    "Details" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Comp_ID" text not null,
    primary key ("Comp_ID", "ID"),
    unique ("Atom_ID_1", "Atom_ID_2","Atom_ID_3","Atom_ID_4"),
    foreign key ("Comp_ID","Atom_ID_1") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID","Atom_ID_2") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID","Atom_ID_3") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID","Atom_ID_4") references chem_comp."Chem_comp_atom" ("Comp_ID","Atom_ID") on delete cascade,
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

CREATE TABLE chem_comp."Chem_comp_descriptor" (
    "Descriptor" text not null,
    "Type" text not null,
    "Program" text,
    "Program_version" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Comp_ID" text not null,
--    primary key ("Comp_ID", "Descriptor", "Type"),
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

CREATE TABLE chem_comp."Chem_comp_identifier" (
    "Identifier" text not null,
    "Type" text not null,
    "Program" text,
    "Program_version" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Comp_ID" text not null,
--    primary key ("Comp_ID", "Identifier", "Type"),
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

CREATE TABLE chem_comp."PDBX_chem_comp_feature" (
    "Type" text,
    "Value" text,
    "Source" text,
    "Support" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Comp_ID" text not null,
    primary key ("Comp_ID", "Type", "Value"),
    foreign key ("Comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

--
-- should map pdbx_chem_comp_synonyms sometime...
--
--CREATE TABLE chem_comp."Chem_comp_common_name" (
--    "Name" text,
--    "Type" text,
--    "Sf_ID" integer DEFAULT nextval('chem_comp.sfid_seq'::regclass),
--    "Entry_ID" text,
--    "Comp_ID" text
--);
--


--
-- entity IDs are per-entry and not unique here. no entry ids here either 
-- so for primary key we'll use linked comp_id: there's 1 entity per 1 chem comp here.
-- keys are problematic in child tables too
--
-- someday I should rewrite the code to generate entity saveframes on the fly 
-- instead of pre-caching them in the database
--
CREATE TABLE chem_comp."Entity" (
    "Sf_category" text not null default 'entity',
    "Sf_framecode" text,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Sf_ID" integer DEFAULT nextval('chem_comp.sfid_seq'),
    "ID" integer not null DEFAULT 1,
    "BMRB_code" text,
    "Name" text,
    "Type" text,
    "Polymer_common_type" text,
    "Polymer_type" text,
    "Polymer_type_details" text,
    "Polymer_strand_ID" text,
    "Polymer_seq_one_letter_code_can" text,
    "Polymer_seq_one_letter_code" text,
    "Target_identifier" text,
    "Polymer_author_defined_seq" text,
    "Polymer_author_seq_details" text,
    "Ambiguous_conformational_states" text,
    "Ambiguous_chem_comp_sites" text,
    "Nstd_monomer" text,
    "Nstd_chirality" text,
    "Nstd_linkage" text,
    "Nonpolymer_comp_ID" text primary key,
    "Nonpolymer_comp_label" text,
    "Number_of_monomers" integer,
    "Number_of_nonpolymer_components" integer default 1,
    "Paramagnetic" text,
    "Thiol_state" text,
    "Src_method" text,
    "Parent_entity_ID" integer,
    "Fragment" text,
    "Mutation" text,
    "EC_number" text,
    "Calc_isoelectric_point" text,
    "Formula_weight" text,
    "Formula_weight_exptl" text,
    "Formula_weight_exptl_meth" text,
    "Details" text,
    "DB_query_date" date,
    "DB_query_revised_last_date" date,
    foreign key ("Nonpolymer_comp_ID") references chem_comp."Chem_comp" ("ID") on delete cascade
);

--
-- there is only one
--
CREATE TABLE chem_comp."Entity_comp_index" (
    "ID" integer not null default 1,
    "Auth_seq_ID" text,
    "Comp_ID" text not null,
    "Comp_label" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Entity_ID" integer not null,
    foreign key ("Comp_ID") references chem_comp."Entity" ("Nonpolymer_comp_ID") on delete cascade
);

CREATE TABLE chem_comp."Entity_common_name" (
    "Name" text not null,
    "Type" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Entity_ID" integer not null default 1
);

CREATE TABLE chem_comp."Entity_systematic_name" (
    "Name" text not null,
    "Naming_system" text,
    "Sf_ID" integer,
    "Entry_ID" text not null default 'NEED_ACC_NO',
    "Entity_ID" integer not null default 1
);
