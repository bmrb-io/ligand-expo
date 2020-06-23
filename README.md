# ligand-expo
Import PDB ligand expo into BMRB processing pipeline

There's two parts:
  * import chem. comps from mmCIF files into NMR-STAR database, dump the "public" version of the database for use on BMRB 
    website (public API & pages).
  * Simple WSGI front-end for searching and for generating NMR-STAR chem. comp and entity saveframes for insertion in BMRB 
    entries (internal processing by BMRB annotators).

PDB supports "compound" chem comps that are comprized of other chem comps. BMRB does not.

DB loader supports the notion of "local mods", so it checks for dates: "initial" vs. "last updated". For this to work
any local update must touch the "last updated" field.

### Files

  * `PDBX.sql` - DDL script for mmCIF version of teh database. It's hand-written and needs to be adjusted for
    any updates to PDB Exchange dictionary (chem comp section is very stable and hasn't really changed in forever)

### Require

  * `psycopg2`
  * `SAS`
  * `werkzeug` for the WSGI bit
