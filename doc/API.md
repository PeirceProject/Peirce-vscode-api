* Peirce Server API

- populate
  - args: path to C++ file 
  - return: 
    - list of code coordinates in JSON

- check
  - args: C++ file, list of annotations
  - return: list of interpretations, one per code coordinate;

- 

* What is the right API?
  - initialize : C++ file -> builds empty interpretation
  - annotate : C++ file element (code coord, interpretation) -> updated interpretation in Peirce
  - delete annotation
  - get errors
  - ...

* Extension itself

* Peirce server -- concept of operation? interactive, we need a box that is Peirce
  - initialize
  - load saved annotations
  - add/remove annotation
  - get unannotated objects
  - get annotated objects
  - ... 