***Do Soon:***
- Add functions for editing branches.
- New frame that consolidates the PO, manifest, invoice, and payment.
- Option to output entire list of companies to Excel for reference.
- Save editing in excel to database with password and notes on double-checking, and backup.
- Lock PO price after invoice attached!
- Allow editing of manifest amount. Lock when invoiced (thus verified).
- Allow move of remaining non-invoiced shipments to new PO in case of price change. In all PO view mode.
    - When closing PO and non-invoiced manifests are present, ask if remainder need to move to new PO.
    - Change PO close prompt to show only after total PO qty shipped **and** invoiced.
- Add editable (autosaved) note under branch buttons. Large obvious letters for keeping PO/Manifest instructions.
- Deleting 'parent' link in Branch might break something. Look to see where it is used.
- Undo 'paid' command in case of mistake
- All caps for all license, invoice #, check #, PO # fields.
- PO creation should only show the supplies or products and not both.
- BUG: Deleting PO will sometimes say it is already deleted or not present.
- Remove create button on PO management frame. Deactivate PO management button if there are no active PO's.

***Requested:***
- RT should match manifest order (and PO order). Check this.
- Add destinations list to CoGroups and make selectable in manifest (and PO optional).
- Add destinations option/buttons to manifest.
- Add vehicle radiobuttons
- Help directions. List of questions and focuses program on the related page and gives instructions.
- Show total kg/L etc. when typing number of barrels/bags in PO creation frame.

***Extra:***
- Command line method for updating database from outputed Excel of companies and products.
- Add discount option widgets if it might be used.
- Use ReportLab for QC report instead of FPDF.
- Clean up/refactor and document code.
- Learn to output matplotlib plot as PDF and transfer that image to another PDF. Use 'pdfrw' package. Another option is to integrate R somehow for generating reports.
- Add popup balloon messages all over for more info. Turn off and on in options.
- Fix translations to be more obvious about function.
- Show deactivated products in gray at bottom of PO creation frame.
