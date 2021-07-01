"""
*ImageCalibrants: Calibration Standards*
----------------------------------------

GSASII powder calibrants in dictionary ``ImageCalibrants.Calibrants``
containing substances commonly used for powder calibrations for image data.

Each entry in ``ImageCalibrants`` consists of::

  'key':([Bravais num,],[space group,],[(a,b,c,alpha,beta,gamma),],no. lines skipped,(dmin,pixLimit,cutOff),(absent list))

 * See below for Bravais num assignments.
 * The space group may be an empty string.
 * The absent list is optional; it gives indices of lines that have no intensity despite being allowed - see the Si example below; counting begins at zero

As an example::

  'LaB6  SRM660a':([2,],['',][(4.1569162,4.1569162,4.1569162,90,90,90),],0,(1.0,10,10.)),

For calibrants that are mixtures, the "Bravais num" and "(a,b,...)" values are repeated, as in this case::

  'LaB6 & CeO2':([2,0],['',''] [(4.1569,4.1569,4.1569,90,90,90),(5.4117,5.4117,5.4117,90,90,90)], 0, (1.0,2,1.)),

Note that Si has reflections (the 4th, 11th,...) that are not extinct by
symmetry but still have zero intensity. These are supplied in the final list::

  'Si':([0,],['F d 3 m'],[(5.4311946,5.4311946,5.4311946,90,90,90),],0,(1.,10,10.),(3,10,13,20,23,26,33,35,40,43)),

Note, the Bravais numbers are:
            * 0 F cubic
            * 1 I cubic
            * 2 P cubic
            * 3 R hexagonal (trigonal not rhombohedral)
            * 4 P hexagonal
            * 5 I tetragonal
            * 6 P tetragonal
            * 7 F orthorhombic
            * 8 I orthorhombic
            * 9 C orthorhombic
            * 10 P orthorhombic
            * 11 C monoclinic
            * 12 P monoclinic
            * 13 P triclinic

User-Defined Calibrants
=======================
To expand this list with locally needed additions, do not modify this
``ImageCalibrants.py`` file,
because you may lose these changes during a software update. Instead
duplicate the format of this file in a file named ``UserCalibrants.py``
and there define the material(s) you want::

  Calibrants={
    'LaB6 skip 2 lines':([2,],['',],[(4.1569162,4.1569162,4.1569162,90,90,90),],2,(1.0,10,10),()),
  }

New key values will be added to the list of options.
If a key is duplicated, the information in  ``UserCalibrants.py`` will
override the entry in this (the ``ImageCalibrants.py`` file).

"""

Calibrants={
    '--- TPS19A  LaB6  SRM660c ---': ([2,],[''],[(4.15683,4.15683,4.15683,90,90,90),],0,(1.0,10,10.)),
}
