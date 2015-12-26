Readme
=====

OpenClinica CRF conversion tool.

---

This tool is written in python and converts a CRF (Case Report Form) from the OpenClinica format into an HTML version of it.

Before using it you need to convert the CRF into CSV using Excel.

The tool uses the jquery.dform plugin to auto-generate the form.

Not all properties of each element are implemented and a lot of work is still needed to complete the conversion.

This script is probably a good starting point to tweak your parser.


Possible Extensions
=====

* Complete all form elements (e.g. adding all labels, both right and left)
* Include HIDE/SHOW elements (i.e. dynamically showing elements according to predefined conditions)
* Using http://openpyxl.readthedocs.org/ to read directly from the XLSX file