--
-- basic db schema for RCSB ligand expo
--

drop schema if exists ligand_expo cascade;
create schema ligand_expo;

-- chem_comp

create table ligand_expo.chem_comp (
formula text,
formula_weight text,
id text primary key,
model_details text,
model_erf text,
model_source text,
mon_nstd_class text,
mon_nstd_details text,
mon_nstd_flag text,
mon_nstd_parent text,
mon_nstd_parent_comp_id text,
name text,
number_atoms_all integer,
number_atoms_nh integer,
one_letter_code text,
pdbx_ambiguous_flag text,
pdbx_component_no text,
pdbx_formal_charge text,
pdbx_ideal_coordinates_details text,
pdbx_ideal_coordinates_missing_flag text,
pdbx_initial_date date,
pdbx_model_coordinates_db_code text,
pdbx_model_coordinates_details text,
pdbx_model_coordinates_missing_flag text,
pdbx_modification_details text,
pdbx_modified_date date,
pdbx_processing_site text,
pdbx_release_status text,
pdbx_replaced_by text,
pdbx_replaces text,
pdbx_subcomponent_list text,
pdbx_synonyms text,
pdbx_type text,
three_letter_code text,
type text );

-- chem_comp_atom

create table ligand_expo.chem_comp_atom (
alt_atom_id text,
atom_id text,
charge text,
comp_id text,
model_Cartn_x text,
model_Cartn_x_esd text,
model_Cartn_y text,
model_Cartn_y_esd text,
model_Cartn_z text,
model_Cartn_z_esd text,
partial_charge text,
pdbx_align text,
pdbx_alt_atom_id text,
pdbx_alt_comp_id text,
pdbx_aromatic_flag text,
pdbx_component_atom_id text,
pdbx_component_comp_id text,
pdbx_leaving_atom_flag text,
pdbx_model_Cartn_x_ideal text,
pdbx_model_Cartn_y_ideal text,
pdbx_model_Cartn_z_ideal text,
pdbx_ordinal integer,
pdbx_stereo_config text,
substruct_code text,
type_symbol text,
unique( comp_id, atom_id ),
foreign key( comp_id ) references ligand_expo.chem_comp( id ));

-- chem_comp_angle

create table ligand_expo.chem_comp_angle (
atom_id_1 text,
atom_id_2 text,
atom_id_3 text,
comp_id text,
value_angle text,
value_angle_esd text,
value_dist text,
value_dist_esd text,
foreign key( comp_id, atom_id_1 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_2 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_3 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- chem_comp_bond

create table ligand_expo.chem_comp_bond (
atom_id_1 text,
atom_id_2 text,
comp_id text,
pdbx_aromatic_flag text,
pdbx_ordinal integer,
pdbx_stereo_config text,
value_dist text,
value_dist_esd text,
value_order text,
foreign key( comp_id, atom_id_1 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_2 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- chem_comp_chir

create table ligand_expo.chem_comp_chir (
atom_config text,
atom_id text,
comp_id text,
id text,
number_atoms_all integer,
number_atoms_nh integer,
volume_flag text,
volume_three text,
volume_three_esd text,
unique (comp_id, atom_id, id ),
foreign key( comp_id, atom_id ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- chem_comp_chir_atom

create table ligand_expo.chem_comp_chir_atom (
atom_id text,
chir_id text,
comp_id text,
dev text,
foreign key( chir_id, comp_id, atom_id ) references ligand_expo.chem_comp_chir( id, comp_id, atom_id ));

-- chem_comp_plane

create table ligand_expo.chem_comp_plane (
comp_id text,
id text,
number_atoms_all integer,
number_atoms_nh integer,
unique( comp_id, id ),
foreign key( comp_id ) references ligand_expo.chem_comp( id ));

-- chem_comp_plane_atom

create table ligand_expo.chem_comp_plane_atom (
atom_id text,
comp_id text,
dist_esd text,
plane_id text,
foreign key( comp_id, atom_id ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( plane_id, comp_id ) references ligand_expo.chem_comp_plane( id, comp_id ));

-- chem_comp_tor

create table ligand_expo.chem_comp_tor (
atom_id_1 text,
atom_id_2 text,
atom_id_3 text,
atom_id_4 text,
comp_id text,
id text,
unique( comp_id, id ),
foreign key( comp_id, atom_id_1 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_2 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_3 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_4 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- chem_comp_tor_value

create table ligand_expo.chem_comp_tor_value (
angle text,
angle_esd text,
comp_id text,
dist text,
dist_esd text,
tor_id text,
foreign key( tor_id, comp_id ) references ligand_expo.chem_comp_tor( id, comp_id ));

-- pdbx_chem_comp_atom_edit

create table ligand_expo.pdbx_chem_comp_atom_edit (
atom_id text,
comp_id text,
edit_atom_id text,
edit_atom_value text,
edit_op text,
ordinal integer,
foreign key( comp_id, atom_id ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- pdbx_chem_comp_atom_feature

create table ligand_expo.pdbx_chem_comp_atom_feature (
atom_id text,
comp_id text,
feature_type text,
foreign key( comp_id, atom_id ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- pdbx_chem_comp_audit

create table ligand_expo.pdbx_chem_comp_audit (
action_type text,
annotator text,
comp_id text,
date date,
details text,
processing_site text,
foreign key( comp_id ) references ligand_expo.chem_comp( id ));

-- pdbx_chem_comp_bond_edit

create table ligand_expo.pdbx_chem_comp_bond_edit (
atom_id_1 text,
atom_id_2 text,
comp_id text,
edit_bond_value text,
edit_op text,
ordinal integer,
foreign key( comp_id, atom_id_1 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ),
foreign key( comp_id, atom_id_2 ) references ligand_expo.chem_comp_atom( comp_id, atom_id ));

-- pdbx_chem_comp_descriptor

create table ligand_expo.pdbx_chem_comp_descriptor (
comp_id text,
descriptor text,
ordinal integer,
program text,
program_version text,
type text,
foreign key( comp_id ) references ligand_expo.chem_comp( id ));

-- pdbx_chem_comp_feature

create table ligand_expo.pdbx_chem_comp_feature (
comp_id text,
source text,
support text,
type text,
value text,
foreign key( comp_id ) references ligand_expo.chem_comp( id ));

-- pdbx_chem_comp_identifier

create table ligand_expo.pdbx_chem_comp_identifier (
comp_id text,
identifier text,
ordinal integer,
program text,
program_version text,
type text,
foreign key( comp_id ) references ligand_expo.chem_comp( id ));

-- pdbx_chem_comp_import

create table ligand_expo.pdbx_chem_comp_import (
comp_id text,
foreign key( comp_id ) references ligand_expo.chem_comp( id ));
