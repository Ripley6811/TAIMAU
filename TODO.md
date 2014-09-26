***Do Soon:***
- Add functions for editing/adding branches.
- Option to output entire list of companies and products to Excel for reference.
- Lock PO price after invoice attached
- Allow move of remaining non-invoiced shipments to new PO in case of price change. In all PO view mode.
    - When closing PO and non-invoiced manifests are present, ask if remainder need to move to new PO.
    - Change PO close prompt to show only after total PO qty shipped **and** invoiced.
- Add editable (autosaved) note under branch buttons. Large obvious letters for keeping PO/Manifest instructions.
- Deleting 'parent' link in Branch might break something. Look to see where it is used.

***Requested:***
- RT should match manifest order (and PO order). Check this.
- Added destinations list to CoGroups and make selectable in manifest (and PO optional).
- Add destinations option/buttons to manifest.
- Add vehicle radiobuttons

***Extra:***
- Command line method for updating database from outputed Excel of companies and products.
- Add discount option widgets if it might be used.
- ReportLab's open-source PDF toolkit shows the ming character. Do more testing and switch from FPDF.
- Clean up/refactor and document code.
- Learn to output matplotlib plot as PDF and transfer that image to another PDF. Use 'pdfrw' package. Another option is to integrate R somehow for generating reports.
