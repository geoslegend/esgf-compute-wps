from engines.manager import ComputeEngine

class MultiprocEngine( ComputeEngine ):

    def getCommunicator( self ):
        from engines.multiprocEngine.communicator import MultiprocCommunicator
        return  MultiprocCommunicator()


    @staticmethod
    def getWorkerIntracom():
        pass
