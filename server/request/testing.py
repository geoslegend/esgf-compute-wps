import unittest, sys, logging, json
from request.manager import taskManager
from modules.utilities import wpsLog
verbose = False

if verbose:
    wpsLog.addHandler( logging.StreamHandler(sys.stdout) )
    wpsLog.setLevel(logging.DEBUG)

class KernelTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test01_average(self):
        wpsLog.debug( " Running test01_average ")
        test_result = [-0.6465788864083037, -0.7916658211967762, -0.8998650285346974, -0.8043334996794719, -0.6292299838201451, -0.6465719687693373, -0.17121787652244863, -0.4230452245556677, -0.5003512719821789, -0.5228934256650012, -0.8243848620174903 ]
        request_parms = {'version': ['1.0.0'], 'service': ['WPS'], 'embedded': ['true'], 'async': ['false'], 'rawDataOutput': ['result'], 'identifier': ['cdas'], 'request': ['Execute'] }
        request_parms['datainputs'] = ['[domain=[{"id":"d0","level":{"start":0,"end":1,"system":"indices"}}];variable={"dset":"MERRA/mon/atmos/ua","id":"v0:ua","domain":"d0"};operation=["CWT.average(v0,axis:xy)"];]']
        response_json = taskManager.processRequest( request_parms )
        response = json.loads(response_json)
        response_data = response['data']
        self.assertEqual( test_result, response_data[0:len(test_result)] )

    def test02_average(self):
        test_result = [-0.6465788864083037, -0.7916658211967762, -0.8998650285346974, -0.8043334996794719, -0.6292299838201451, -0.6465719687693373, -0.17121787652244863, -0.4230452245556677, -0.5003512719821789, -0.5228934256650012, -0.8243848620174903 ]
        request_parms = {'version': ['1.0.0'], 'service': ['WPS'], 'embedded': ['true'], 'async': ['false'], 'rawDataOutput': ['result'], 'identifier': ['cdas'], 'request': ['Execute'] }
        request_parms['datainputs'] = ['[domain=[{"id":"d0","level":{"start":0,"end":1,"system":"indices"}}];variable={"dset":"MERRA/mon/atmos/ua","id":"v0:ua","domain":"d0"};operation=["CWT.average(v0,axis:xy)"];]']
        response_json = taskManager.processRequest( request_parms )
        response = json.loads(response_json)
        response_data = response['data']
        self.assertEqual( test_result, response_data[0:len(test_result)] )

    def xtest03_ensemble_average(self):
        test_result = [ 287.3746163535607, 287.32201028468666, 288.0899054125938, 288.8933610641959, 289.69324597969796, 290.6019424186093, 290.5856389458788, 290.3434735042316, 290.11871301777, 289.1724024490968 ]
        request_parms = {'version': ['1.0.0'], 'service': ['WPS'], 'embedded': ['true'], 'async': ['false'], 'rawDataOutput': ['result'], 'identifier': ['cdas'], 'request': ['Execute'] }
        request_parms['datainputs'] = ['[domain=[{"id":"d0","level":{"start":0,"end":1,"system":"indices"}}];variable=[{"dset":"MERRA/mon/atmos/ta","id":"v0:ta","domain":"d0"},{"dset":"CFSR/mon/atmos","id":"v0:ta","domain":"d0"}];operation=["CWT.average(*,axis:exy)"];]']
        response_json = taskManager.processRequest( request_parms )
        response = json.loads(response_json)
        response_data = response['data']
        self.assertEqual( test_result, response_data[0:len(test_result)] )

    def xtest04_ensemble_average(self):
        test_result = [ 287.3746163535607, 287.32201028468666, 288.0899054125938, 288.8933610641959, 289.69324597969796, 290.6019424186093, 290.5856389458788, 290.3434735042316, 290.11871301777, 289.1724024490968 ]
        request_parms = {'version': ['1.0.0'], 'service': ['WPS'], 'embedded': ['true'], 'async': ['false'], 'rawDataOutput': ['result'], 'identifier': ['cdas'], 'request': ['Execute'] }
        request_parms['datainputs'] = ['[domain=[{"id":"d0","level":{"start":0,"end":1,"system":"indices"}}];variable=[{"dset":"MERRA/mon/atmos/ta","id":"v0:ta","domain":"d0"},{"dset":"CFSR/mon/atmos","id":"v0:ta","domain":"d0"}];operation=["CWT.average(*,axis:exy)"];]']
        response_json = taskManager.processRequest( request_parms )
        response = json.loads(response_json)
        response_data = response['data']
        self.assertEqual( test_result, response_data[0:len(test_result)] )

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( KernelTests )
    test_runner.run( suite )

