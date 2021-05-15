======================
xmp_pp3_crossconverter
======================

Transfer metadata between Digikam and RawTherapee easily.


Usage
=====

- ``python <path_to_script>`` will do XMP --> PP3 (you can also specify ``--metadata_source "XMP"``, which is the default)
- ``python <path_to_script> --metadata_source "PP3"`` will do PP3 --> XMP
- ``python <path_to_script> --main_path "your/absolute/path"`` will specify a different directory than ``./``
- ``python <path_to_script> --verbose 1`` will start the verbose print

``--metadata_source``, ``--main_path``, and ``--verbose`` can of course be combined.
