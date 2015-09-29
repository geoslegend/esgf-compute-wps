from modules import configuration
import cdms2
from modules.utilities import  *

class Collection:
    def __init__( self, name, collection_spec ):
        self.dapfiles = {}
        self.locfile = None
        self.name = name
        self.server_type = collection_spec.get('type', 'file')
        self.base_url = collection_spec['url']
        self.initialize( collection_spec.get( 'open', [] ) )

    def initialize( self, open_list ):
        for var_id in open_list:
            self.getFile( var_id )

    def constructURL(self, var_id ):
        if self.server_type in [ 'dods', ]:
            return "%s/%s.ncml" % ( self.base_url, var_id )

    def getFile( self, var_id ):
        if self.server_type == 'file:':
            if self.locfile is None:
                self.locfile = self.loadFile()
            return self.locfile
        else:
            file = self.dapfiles.get( var_id, None )
            if file is None:
                file = self.loadFile( var_id )
                if file is not None: self.dapfiles[ var_id ] = file
            return file

    def loadFile(self, var_id=None ):
        if self.server_type == 'file':
            if self.base_url[:7]=="file://":
                f=cdms2.open(str(self.base_url[6:]))
            else:
                f=cdms2.open(str(self.base_url))
        else:
            url = self.constructURL( var_id )
            f=cdms2.open(str(url))
        return f

class CollectionManager:
    CollectionManagers = {}

    @classmethod
    def getInstance(cls,name):
        return cls.CollectionManagers.setdefault( name, CollectionManager(name) )

    def __init__( self, name ):
        self.collections = {}

    def getFile( self, collection_name, var_id ):
        collection = self.getCollection( collection_name )
        return collection.getFile( var_id )

    def addCollection(self, collection_name, collection_rec ):
        self.collections[ collection_name ] = Collection( collection_name, collection_rec )

    def getCollection(self, collection_name  ):
        try:
            return self.collections.get( collection_name )
        except KeyError:
            raise Exception( "Error, attempt to access undefined collection: %s " % collection_name )

collectionManager = CollectionManager.getInstance( configuration.CDAS_APPLICATION )

collections = configuration.CDAS_COLLECTIONS
for collection_spec in collections:
    collectionManager.addCollection( collection_spec[0], collection_spec[1] )

def cache_load_test():
    from modules.configuration import CDAS_PERSISTENCE_DIRECTORY
    import os, numpy
    cache_dir = os.path.expanduser( CDAS_PERSISTENCE_DIRECTORY )
    cached_files = [ os.path.join(cache_dir,f) for f in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir,f)) ]

    max_load_time = 0.0
    max_file = None
    for cached_file in cached_files:
        t0 = time.time()
        data = numpy.fromfile( cached_file, dtype=numpy.float32 )
        t1 = time.time()
        load_time = t1-t0
        print "Loaded file %s in %.3f" % ( cached_file, load_time )
        if load_time > max_load_time:
            max_load_time = load_time
            max_file = cached_file

    print "--- "*20
    print "MAX Load time: file %s in %.3f" % ( max_file, max_load_time )

if __name__ == "__main__":
#    from testing import getVariable
#    CacheLevel = 10000.0
#    TestVariable = getVariable( 0, CacheLevel )
#    data = TestVariable.data

    import os, numpy, numpy.ma as ma
    cached_file = os.path.expanduser( '~/.cdas/testing/MERRA_mon_atmos_hur' )
    data = numpy.fromfile( cached_file, dtype=numpy.float32 ).reshape( (432, 144, 288) )
    FillVal = 1.00000002e+20
    mdata = ma.masked_greater( data, 0.90000002e+20 )
    t0 = time.time()
    a = ma.average(data,0)
    t1 = time.time()
    print "Result computed in %.2f, shape = %s, sample=%s" % ( (t1-t0), str(a.shape), a.flatten()[0:10])






