--
-- pre-generate entity saveframes
--  there is no good primary key
--

insert into chem_comp."Entity" (
    "Sf_category",
    "Sf_framecode",
    "Entry_ID",
    "BMRB_code",
    "Name",
    "Type",
    "Number_of_nonpolymer_components",
    "Nonpolymer_comp_ID",
    "Nonpolymer_comp_label",
    "Paramagnetic",
    "Formula_weight")
select 
    'entity',
    'entity_'||"ID",
    'NEED_ACC_NO',
    "BMRB_code",
    case when "Name" is null then 'entity_'||"ID" else "Name" end,
    case when upper("Name")='WATER' then 'water' else 'non-polymer' end,
    1,
    "ID",
    'chem_comp_'||"ID",
    "Paramagnetic",
    "Formula_weight"
from chem_comp."Chem_comp";

-- these aren't very useful but it's all we got
--
--
insert into chem_comp."Entity_common_name" (
    "Name",
    "Type",
    "Sf_ID",
    "Entry_ID")
select 
    c."Name",
    'BMRB',
    e."Sf_ID",
    'NEED_ACC_NO'
from chem_comp."Chem_comp" c join chem_comp."Entity" e
on e."Nonpolymer_comp_ID"=c."ID";

--
--
--
insert into chem_comp."Entity_systematic_name" (
    "Name",
    "Naming_system",
    "Sf_ID",
    "Entry_ID")
select 
    c."Name",
    'BMRB',
    e."Sf_ID",
    'NEED_ACC_NO'
from chem_comp."Chem_comp" c join chem_comp."Entity" e
on e."Nonpolymer_comp_ID"=c."ID";

--
--
--
insert into chem_comp."Entity_systematic_name" (
    "Name",
    "Naming_system",
    "Sf_ID",
    "Entry_ID")
select 
    coalesce(c."Three_letter_code",c."ID"),
    'Three letter code',
    e."Sf_ID",
    'NEED_ACC_NO'
from chem_comp."Chem_comp" c join chem_comp."Entity" e
on e."Nonpolymer_comp_ID"=c."ID";

--
--
--
insert into chem_comp."Entity_comp_index" (
    "ID",
    "Auth_seq_ID",
    "Entity_ID",
    "Comp_ID",
    "Comp_label",
    "Sf_ID",
    "Entry_ID")
select
    1,
    1,
    e."ID",
    c."ID",
    'chem_comp_'||c."ID",
    e."Sf_ID",
    'NEED_ACC_NO'
from chem_comp."Chem_comp" c join chem_comp."Entity" e
on e."Nonpolymer_comp_ID"=c."ID";

-- non-polymer entities don't have entity_poly
--
-- chem_comp."Entity_poly_seq"

-- entity_atom_list is redundant for monomer entities like these
-- and we don't know how to make it for polymer ones (unless they're all standard residues)
-- it doesn't exist in ~97% of BMRB entries
-- chem_comp."Entity_atom_list"

-- entity_bond is intended for unusual bonds only in 3.1 schema. whatever that means
-- chem_comp."Entity_bond"

-- eof
--
