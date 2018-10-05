from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np

class IOFLAGS:
    IO_TYPE    = 'h5'
    BATCH_SIZE = 1
    INPUT_FILE = ''
    DATA_DIM   = ''
class io_base(object):

    def __init__(self,flags):
        self._batch_size = flags.BATCH_SIZE
   
    def batch_size(self,size=None):
        if size is None: return self._batch_size
        self._batch_size = int(size)

    def num_entries(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def next(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

class io_h5(io_base):

    def __init__(self,flags):
        super(io_h5,self).__init__(flags=flags)
        self._flags = flags
        self._data  = None
        self._label = None
        self._num_entries = None

    def num_entries(self):
        return self._num_entries

    def initialize(self):
        import h5py as h5
        self._data  = None
        self._label = None
        files = self._flags.INPUT_FILE.split(',')
        for f in files:
            print(f)
            f = h5.File(f,'r')
            if self._data is None:
                self._data  = np.array(f['raw' ]).astype(np.float32)
                self._label = np.array(f['onehot']).astype(np.float32)
            else:
                self._data  = np.concatenate(self._data, np.array(f['raw' ]))
                self._label = np.concatenate(self._label,np.array(f['onehot']))
        self._num_entries = len(self._data)

    def next(self):
        idx = np.arange(self.num_entries())
        np.random.shuffle(idx)
        idx = idx[0:self.batch_size()]
        return self._data[idx, ...], self._label[idx, ...], idx
    #def next(self):
    #    import numpy as np
    #    return (np.zeros(shape=[self._flags.BATCH_SIZE,32*32*32],dtype=np.float32),
    #            np.zeros(shape=[self._flags.BATCH_SIZE,32*32*32],dtype=np.float32),
    #            np.arange(0,self._flags.BATCH_SIZE,1))

    def dim_data(self):
        dim = None
        exec('dim = list(%s)' % self._flags.DATA_DIM)
        dim.insert(0,self._flags.BATCH_SIZE)
        return dim
    
    def finalize(self):
        pass

def io_factory(flags):
    if flags.IO_TYPE == 'h5':
        return io_h5(flags)
    raise NotImplementedError
