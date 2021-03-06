import traceback

import numpy.ma as ma
import numpy as np
import cdutil
import cdms2, sys
from modules.utilities import *
from kernels.cda import CDASKernel

def get_subset( input_data, subset_index, subset_index_array ):
    im_mask = subset_index_array <> subset_index
    if input_data.ndim > 1:
        im_mask = np.tile( im_mask, input_data.shape[1:] )
    return ma.masked_array( input_data, mask = im_mask )

class TimeseriesAnalytics( CDASKernel ):

    season_def_array = [ 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0]

    def compress( self, variable, precision=4 ):
        maxval = variable.max()
        minval = variable.min()
        scale = ( pow(10,precision) - 0.01 ) / ( maxval - minval )
        scaled_variable = ( variable - minval ) * scale
        return { 'range': [ minval, maxval ], 'data': scaled_variable.tolist( numpy.nan ) }

    def annual_cycle( self, input_variable ):
        t0 = time.time()
        time_vals = input_variable.getTime().asComponentTime()
        month_index_array = np.array( [  tv.month for tv in time_vals ] )
        squeezed_input = input_variable.squeeze()
        acycle = [ ma.average( get_subset( squeezed_input, month_index, month_index_array ) ) for month_index in range(1,13) ]
        t1 = time.time()
        wpsLog.debug( "Computed annual cycle, time = %.4f, result:\n %s" % ( (t1-t0), str(acycle) ) )
        return ma.array(acycle)

    def seasonal_cycle( self, input_variable ):
        t0 = time.time()
        time_vals = input_variable.getTime().asComponentTime()
        season_index_array = np.array( [  self.season_def_array[tv.month] for tv in time_vals ] )
        squeezed_input = input_variable.squeeze()
        acycle = [ ma.average( get_subset( squeezed_input, season_index, season_index_array ) ) for season_index in range(0,4) ]
        t1 = time.time()
        wpsLog.debug( "Computed seasonal cycle, time = %.4f, result:\n %s" % ( (t1-t0), str(acycle) ) )
        return ma.array(acycle)

    # def run( self, subsetted_variables, metadata_recs, operation ):
    #     try:
    #         start_time = time.time()
    #         ( result_data, time_axis ) = self.applyOperation( subsetted_variables, operation )
    #         end_time = time.time()
    #         result_obj = self.getResultObject( metadata_recs, time_axis, result_data )
    #         wpsLog.debug( "Computed operation %s on region %s: time = %.4f" % ( str(operation), str(result_obj["data.region"]), (end_time-start_time) ) )
    #     except Exception, err:
    #         wpsLog.debug( "Exception executing timeseries process:\n " + traceback.format_exc() )
    #     return result_obj

    def applyOperation( self, input_variables, operation ):
        result = None
        result_mdata = {}
        rshape = None
        t0 = time.time()
        input_variable = input_variables[0]
        try:
            self.setTimeBounds( input_variable )
            operator = None
            time_axis = None
            if operation is not None:
                method = operation.get('method','').lower()
                bounds = operation.get('bounds','').lower()
                op_start_time = time.clock() # time.time()
                if not bounds:
                    if method == 'departures':
                        result = ma.anomalies( input_variable ).squeeze()
                    elif method == 'climatology':
                        result = cdutil.averager( input_variable, axis='t', weights='equal' )
                    elif method == 'value':
                        result =  input_variable
                    else:
                        result = input_variable
                    time_axis = input_variable.getTime()
                elif bounds == 'np':
                    if   method == 'departures':
                        result = ma.anomalies( input_variable ).squeeze()
                    elif method == 'climatology':
                        result = ma.average( input_variable ).squeeze()
                    elif method == 'annualcycle':
                        result = self.annual_cycle( input_variable )
                    else:
                        result = input_variable
                    time_axis = input_variable.getTime()
                else:
                    if bounds == 'djf':
                        operator = cdutil.DJF
                    elif bounds == 'mam':
                        operator = cdutil.MAM
                    elif bounds == 'jja':
                        operator = cdutil.JJA
                    elif bounds == 'son':
                        operator = cdutil.SON
                    elif bounds == 'year':
                        operator = cdutil.YEAR
                    elif bounds == 'annualcycle':
                        operator = cdutil.ANNUALCYCLE
                    elif bounds == 'seasonalcycle':
                        operator = cdutil.SEASONALCYCLE
                    if operator <> None:
                        if   method == 'departures':
                            result = operator.departures( input_variable ).squeeze()
                        elif method == 'climatology':
                            if bounds == 'annualcycle':
                                result = self.annual_cycle( input_variable )
#                                result = operator.climatology( input_variable ).squeeze()
                                time_axis = cdms2.createAxis( range( len(result) ) )
                                time_axis.units = "months"
                            elif bounds == 'seasonalcycle':
                                result = operator.climatology( input_variable ).squeeze()
                                time_axis = cdms2.createAxis( range( len(result) ) )
                                time_axis.units = "seasons"
                        else:
                            result = operator( input_variable ).squeeze()
                    if time_axis is None:
                        time_axis = result.getTime()
                op_end_time = time.clock() # time.time()
                # if math.isnan( result[0] ):
                #     pp = pprint.PrettyPrinter(indent=4)
                #     print "\n ---------- NaN in Result, Input: ---------- "
                #     print str( input_variable.data )
            else:
                result = input_variable
                time_axis = input_variable.getTime()

            if isinstance( result, float ):
                result_data = [ result ]
                rshape = [ 1 ]
            elif result is not None:
                if result.__class__.__name__ == 'TransientVariable':
                    result = ma.masked_equal( result.squeeze().getValue(), input_variable.getMissing() )
                result_data = result.tolist( numpy.nan )
                rshape = result.shape
            else:
                result_data = None
                time_axis = input_variable.getTime()
                rshape = "None"
        except Exception, err:
            wpsLog.debug( "Exception applying Operation '%s':\n %s" % ( str(operation), traceback.format_exc() ) )
            return ( None, None )

        if time_axis is not None:
            units = time_axis.units.split()
            if( len(units) == 3 ) and ( units[1] == 'since' ):
                newunits = "%s since 1970-1-1" % units[0]
                time_axis.toRelativeTime(newunits)
        rv = input_variable if result is None else result_data
        t1 = time.time()
        wpsLog.debug( " $$$ Applied Operation: %s to variable shape %s in time %.4f, result shape = %s" % ( str( operation ), str(input_variable.shape), (t1-t0), rshape  ) )
        result_mdata['time'] = time_axis
        return ( rv, result_mdata )


if __name__ == "__main__":
    from kernels.manager import kernelMgr
    from request.manager import TaskRequest

    wpsLog.addHandler( logging.StreamHandler(sys.stdout) ) #logging.FileHandler( os.path.abspath( os.path.join(os.path.dirname(__file__), '..', 'logs', 'wps.log') ) ) )
    wpsLog.setLevel(logging.DEBUG)

    run_args =  { 'region': '{"longitude": -137.09327695888, "latitude": 35.487604770915, "level": 85000 }',   # ,
                  'data': '{"collection": "MERRA/mon/atmos", "id": "hur"}',
#                  'operation': '[  {"kernel": "time", "method": "departures", "bounds":"np" } ] '
                  'operation': '[  {"kernel": "time", "method": "climatology",  "bounds":"annualcycle"} ] '
 #                 'operation': '[  {"kernel": "time", "method": "annualcycle",  "bounds":"np"} ] '
                }

    kernelMgr.run( TaskRequest( request=run_args ) )


