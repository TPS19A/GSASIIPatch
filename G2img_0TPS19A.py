# -*- coding: utf-8 -*-
########### SVN repository information ###################
# $Date: 2020-02-05 19:00:20 +0800 (Wed, 05 Feb 2020) $
# $Author: vondreele $
# $Revision: 4288 $
# $URL: https://subversion.xray.aps.anl.gov/pyGSAS/trunk/imports/G2img_1TIF.py $
# $Id: G2img_1TIF.py 4288 2020-02-05 11:00:20Z vondreele $
########### SVN repository information ###################
'''
*Module G2img_1TIF: Tagged-image File images*
--------------------------------------------------

Routine to read an image in Tagged-image file (TIF) format as well as a variety
of slightly incorrect pseudo-TIF formats used at instruments around the world.
Note that the name ``G2img_1TIF`` is used so that this file will
sort to the top of the image formats and thus show up first in the menu.
(It is the most common, alas).

'''

from __future__ import division, print_function
import struct as st
import GSASIIobj as G2obj
import GSASIIpath
import GSASIIfiles as G2fil
import numpy as np
import time
DEBUG = False
GSASIIpath.SetVersionNumber("$Revision: 4288 $")
class TIF_ReaderClass(G2obj.ImportImage):
    '''Reads TIF files using a routine (:func:`GetTifData`) that looks
    for files that can be identified from known instruments and will
    correct for slightly incorrect TIF usage. If that routine fails,
    it will be read with a standard TIF reader, which can handle compression
    and other things less commonly used at beamlines.
    '''
    def __init__(self):
        super(self.__class__,self).__init__( # fancy way to self-reference
            extensionlist=('.tif','.tiff'),
            strictExtension=False,
            formatName = 'TPS19A TIF image',
            longFormatName = 'Various .tif and pseudo-TIF formats'
            )
        self.scriptable = True

    def ContentsValidator(self, filename):
        '''Does the header match the required TIF header?
        '''
        fp = open(filename,'rb')
        tag = fp.read(2)
        if 'bytes' in str(type(tag)):
            tag = tag.decode('latin-1')
        if tag == 'II' and int(st.unpack('<h',fp.read(2))[0]) == 42: #little endian
            pass
        elif tag == 'MM' and int(st.unpack('>h',fp.read(2))[0]) == 42: #big endian
            pass
        else:
            return False # header not found; not valid TIF
            fp.close()
        fp.close()
        return True

    def Reader(self,filename, ParentFrame=None, **unused):
        '''Read the TIF file using :func:`GetTifData`. If that fails,
        use :func:`scipy.misc.imread` and give the user a chance to
        edit the likely wrong default image parameters.
        '''
        self.Comments,self.Data,self.Npix,self.Image = GetTifData(filename)
        if self.Npix == 0:
            G2fil.G2Print("GetTifData failed to read "+str(filename)+" Trying PIL")
#            import scipy.misc
#            self.Image = scipy.misc.imread(filename,flatten=True)
            import PIL.Image as PI
            self.Image = PI.open(filename,mode='r')

            # for scipy 1.2 & later  scipy.misc.imread will be removed
            # with note to use imageio.imread instead
            # (N.B. scipy.misc.imread uses PIL/pillow perhaps better to just use pillow)
            self.Npix = self.Image.size
            if ParentFrame:
                self.SciPy = True
                self.Comments = ['no metadata']
                self.Data = {'wavelength': 0.1, 'pixelSize': [200., 200.], 'distance': 100.0}
                self.Data['size'] = list(self.Image.shape)
                self.Data['center'] = [int(i/2) for i in self.Image.shape]
        if self.Npix == 0:
            return False
        self.LoadImage(ParentFrame,filename)
        return True

def GetTifData(filename):
    '''Read an image in a pseudo-tif format,
    as produced by a wide variety of software, almost always
    incorrectly in some way.
    '''
    import struct as st
    import array as ar
    import ReadMarCCDFrame as rmf
    image = None
    File = open(filename,'rb')
    dataType = 5
    center = [None,None]
    wavelength = None
    distance = None
    polarization = None
    samplechangerpos = None
    try:
        Meta = open(filename+'.metadata','Ur')
        head = Meta.readlines()
        for line in head:
            line = line.strip()
            try:
                if '=' not in line: continue
                keyword = line.split('=')[0].strip()
                if 'dataType' == keyword:
                    dataType = int(line.split('=')[1])
                elif 'wavelength' == keyword.lower():
                    wavelength = float(line.split('=')[1])
                elif 'distance' == keyword.lower():
                    distance = float(line.split('=')[1])
                elif 'polarization' == keyword.lower():
                    polarization = float(line.split('=')[1])
                elif 'samplechangercoordinate' == keyword.lower():
                    samplechangerpos = float(line.split('=')[1])
            except:
                G2fil.G2Print('error reading metadata: '+line)
        Meta.close()
    except IOError:
        G2fil.G2Print ('no metadata file found - will try to read file anyway')
        head = ['no metadata file found',]

    tag = File.read(2)
    if 'bytes' in str(type(tag)):
        tag = tag.decode('latin-1')
    byteOrd = '<'
    if tag == 'II' and int(st.unpack('<h',File.read(2))[0]) == 42:     #little endian
        IFD = int(st.unpack(byteOrd+'i',File.read(4))[0])
    elif tag == 'MM' and int(st.unpack('>h',File.read(2))[0]) == 42:   #big endian
        byteOrd = '>'
        IFD = int(st.unpack(byteOrd+'i',File.read(4))[0])
    else:
#        print (tag)
        lines = ['not a detector tiff file',]
        return lines,0,0,0
    File.seek(IFD)                                                  #get number of directory entries
    NED = int(st.unpack(byteOrd+'h',File.read(2))[0])+1
    IFD = {}
    nSlice = 1
    if DEBUG: print('byteorder:',byteOrd)
    for ied in range(NED):
        Tag,Type = st.unpack(byteOrd+'Hh',File.read(4))
        nVal = st.unpack(byteOrd+'i',File.read(4))[0]
        if DEBUG: print ('Try:',Tag,Type,nVal)
        if Type == 1:
            Value = st.unpack(byteOrd+nVal*'b',File.read(nVal))
        elif Type == 2:
            Value = st.unpack(byteOrd+'i',File.read(4))
        elif Type == 3:
            Value = st.unpack(byteOrd+nVal*'h',File.read(nVal*2))
            st.unpack(byteOrd+nVal*'h',File.read(nVal*2))
        elif Type == 4:
            if Tag in [273,279]:
                nSlice = nVal
                nVal = 1
            Value = st.unpack(byteOrd+nVal*'i',File.read(nVal*4))
        elif Type == 5:
            Value = st.unpack(byteOrd+nVal*'i',File.read(nVal*4))
        elif Type == 11:
            Value = st.unpack(byteOrd+nVal*'f',File.read(nVal*4))
        IFD[Tag] = [Type,nVal,Value]
        if DEBUG: print (Tag,IFD[Tag])

    head.append('[Tiff Tags]')
    for _,v in IFD.items():
        if v[0] == 2: # type 2=ASCII
            File.seek(v[2][0]) # Offset: a location with respect to the beginning of the TIFF file.
            line = File.read(v[1]-1).decode("utf-8") # the last byte must be NUL (binary zero).
            line = line.replace(':',"=",1)
            head.append(line)
            if '=' not in line: continue
            keyword = line.split('=')[0].strip()
            if 'dataType' == keyword:
                dataType = int(line.split('=')[1])
            elif 'wavelength' == keyword.lower():
                wavelength = float(line.split('=')[1])
            elif 'distance' == keyword.lower():
                distance = float(line.split('=')[1])
            elif 'polarization' == keyword.lower():
                polarization = float(line.split('=')[1])
            elif 'samplechangercoordinate' == keyword.lower():
                samplechangerpos = float(line.split('=')[1])
# sample04211605_000003.tif
    sizexy = [IFD[256][2][0],IFD[257][2][0]]
    [nx,ny] = sizexy
    Npix = nx*ny
    time0 = time.time()
    if sizexy == [4096,4096]:
        if IFD[273][2][0] == 8:
            tifType = 'XRD1611'
            pixy = [100.,100.]
            File.seek(8)
            G2fil.G2Print ('Read PE 4Kx4K tiff file: '+filename)
            if IFD[258][2][0] == 16:
                image = np.array(np.frombuffer(File.read(2*Npix),dtype=np.uint16),dtype=np.int32)
            else:
                image = np.array(np.frombuffer(File.read(4*Npix),dtype=np.int32))

    if image is None:
        lines = ['not a known detector tiff file',]
        return lines,0,0,0

    if sizexy[1]*sizexy[0] != image.size: # test is resize is allowed
        lines = ['not a known detector tiff file',]
        return lines,0,0,0
    if GSASIIpath.GetConfigValue('debug'):
        G2fil.G2Print ('image read time: %.3f'%(time.time()-time0))
    image = np.reshape(image,(sizexy[1],sizexy[0]))
    center = (not center[0]) and [pixy[0]*sizexy[0]/2000,pixy[1]*sizexy[1]/2000] or center
    wavelength = (not wavelength) and 0.10 or wavelength
    distance = (not distance) and 100.0 or distance
    polarization = (not polarization) and 0.99 or polarization
    samplechangerpos = (not samplechangerpos) and 0.0 or samplechangerpos
    data = {'pixelSize':pixy,'wavelength':wavelength,'distance':distance,'center':center,'size':sizexy,
            'setdist':distance,'PolaVal':[polarization,False],'samplechangerpos':samplechangerpos}
    File.close()
    return head,data,Npix,image
