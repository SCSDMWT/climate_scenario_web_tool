import functools
import numpy as np
from scipy.stats    import genextreme as genex
from scipy.stats    import multivariate_normal
import xarray as xr

from .cache import get_cache

#import matplotlib.pyplot as plt

class Fitted_Obs_Sim():
    def __init__(self,
                 dsObs,
                 dsSim,
                 grid,
                 simParams  = ['c','loc1','scale1'],
                 preProcess = True,
                 nVariates  = 1000):
        '''
        initialise with fitted parameter files from simulations and observations.
        When we have confirmed exactly how we want to do the de-biasing of simulations,
        these steps can be skipped by only providing the fully processed composite file.
        '''
        dsObs, dsSim, grid = xr.align(dsObs, dsSim, grid, join = 'inner')
        
        self.dsObs  = dsObs.broadcast_like(grid, 
                        exclude = ['year','params','params_i','params_j'])
        self.dsSim  = dsSim.broadcast_like(grid, 
                        exclude = ['year','ensemble_member','params','params_i','params_j'])

        self.gridDims = list(grid.dims)
        self.ds     = self.dsObs.copy(deep = True).load()
        self.grid   = grid.load()
        self.bsGrid = grid.copy(deep = True)
        self.bsGrid = self.bsGrid.expand_dims(variate = range(nVariates), axis = -1)

        for v in ['fit','bootstrap_mean']:
            da = self.ds[v]
            da = da.where(~np.isin(da.params, simParams),
                            self.dsSim[v])
            self.ds[v] = da.compute()
        
        da = self.ds.bootstrap_covariance
        for param in simParams:
            da = da.where(da.params_i != param,self.dsSim.bootstrap_covariance)
            da = da.where(da.params_j != param,self.dsSim.bootstrap_covariance)
        self.ds['bootstrap_covariance'] = da.compute()

        self.ds.coords['paramsGEV'] = ['c','loc','scale']
        
        self.fit            = self.ds.fit
        self.bootstrapMean  = self.ds.bootstrap_mean
        self.bootstrapCov   = self.ds.bootstrap_covariance
        self.fCovariateType = self.ds.covariateFunction
        
        displays = dict(
                    stationary          = lambda x,p: np.array([p[0], 
                                                                p[1], 
                                                                p[2]]),
                    linear_loc          = lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x, 
                                                                p[3]]),
                    linear_loc_scale    = lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x, 
                                                                p[3] + p[4]*x]),
                    quadratic_loc       = lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x + p[3]*x*x, 
                                                                p[4]]),
                    quadratic_loc_scale = lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x + p[3]*x*x, 
                                                                p[4] + p[5]*x + p[6]*x*x]))
        self.fCovariate = displays[self.fCovariateType]

        ### pre-process bootstrap variates

        self.bsVariates = None
        if preProcess: self.variate_bootstrap_dist(nVariates)

    def get_GEV_params(self, covariate, fit):
        # not used as this loops rather than using matrix operation
        return xr.apply_ufunc(
                        self.fCovariate,
                        covariate,
                        fit,
                        input_core_dims = [[],['params']],
                        output_core_dims = [['fit']],
                        exclude_dims = set(('params',)),
                        vectorize = True)

    def variate_bootstrap_dist(self, nVariates = 1000):
        '''
        produce random variates of the bootstrap parameters
        '''
        def f(mean, cov, nVariates): 
            if not np.isfinite(mean).all():
                return np.array([mean]*nVariates)
            else:
                return multivariate_normal(mean, cov).rvs(nVariates)
        self.bsVariates = xr.apply_ufunc(
                        f,
                        self.bootstrapMean,
                        self.bootstrapCov,
                        nVariates,
                        input_core_dims = [['params'],['params_i','params_j'],[]],
                        output_core_dims = [['variate','params']],
                        vectorize = True).compute()
        
    def set_covariate(self, covariate, bsCovariates = None):
        '''
        set the covariate, can accept an array of bootstrap covariates (same length as number of bootstrap variates)
        '''
        self.ds['fitGEV'] = (['paramsGEV']+self.gridDims, 
                     self.fCovariate(covariate, [self.fit.sel(params = p) for p in self.ds.params]))
        self.fitGEV = genex(c     = self.ds.fitGEV.sel(paramsGEV='c'),
                            loc   = self.ds.fitGEV.sel(paramsGEV='loc'),
                            scale = self.ds.fitGEV.sel(paramsGEV='scale'))
        if type(self.bsVariates) != type(None):
            if type(bsCovariates) == type(None):
                bsCovariates = covariate
            self.ds['bsfitGEV'] = (['paramsGEV']+self.gridDims+['variate'], 
                     self.fCovariate(bsCovariates, [self.bsVariates.sel(params = p) for p in self.ds.params]))
            self.bsfitGEV = genex(c     = self.ds.bsfitGEV.sel(paramsGEV='c'),
                              loc   = self.ds.bsfitGEV.sel(paramsGEV='loc'),
                              scale = self.ds.bsfitGEV.sel(paramsGEV='scale'))
        else:
            self.bsGEV = None

    def intensity_from_return_time(self, tauReturn, mode = 'fit', output = 'dataarray'):
        if mode == 'fit':
            grid = self.grid
            x = self.fitGEV.ppf(1-1/tauReturn)
        elif mode == 'bs':
            grid = self.bsGrid
            x = self.bsfitGEV.ppf(1-1/tauReturn)
        if output != 'dataarray':
            return x
        else:
            return x*grid.rename(mask='intensity')
        
    def return_time_from_intensity(self, intensity, mode = 'fit', output = 'dataarray'):
        if mode == 'fit':
            grid = self.grid
            x = 1/self.fitGEV.sf(intensity)
        elif mode == 'bs':
            grid = self.bsGrid
            x = 1/self.bsfitGEV.sf(intensity)
        if output != 'dataarray':
            return x
        else: 
            return x*grid.rename(mask='return_time')
        
    def intensity_from_return_time_quantiles(self, tauReturn, quantiles = [0.025,0.975]):
        '''
        call bootstrap version of intensity function and return quantiles
        '''
        x = self.intensity_from_return_time(tauReturn, mode = 'bs', output = 'dataarray')
        return x.intensity.quantile(quantiles, dim = 'variate')

    def return_time_from_intensity_quantiles(self, intensity, quantiles = [0.025,0.975]):
        '''
        call bootstrap version of return_time function and return quantiles
        '''
        x = self.return_time_from_intensity(intensity, mode = 'bs', output = 'dataarray')
        return x.return_time.quantile(quantiles, dim = 'variate')


@functools.lru_cache(maxsize=16)
def init_composite_fit(file, simParams='c,loc1,scale1', nVariates=10000, preProcess=True):
    simParams = simParams.split(',')
    dsObs = xr.open_dataset('HadUK_%s.nc'%file)
    dsSim = xr.open_dataset('%s.nc'%file)
    grid = xr.open_dataset('gridWide_g12.nc')\
             .sel(projection_y_coordinate = slice(4e5,13e5),
                  projection_x_coordinate = slice(0,5e5))
    
    result = Fitted_Obs_Sim(dsObs, dsSim, grid, simParams = simParams, nVariates = nVariates, preProcess = preProcess)
    return result



def intensity_from_return_time(compositeFit, covariate, tauReturn):
    bsCovariates = multivariate_normal(2, 1).rvs(10000) # model accepts lots of variates of covariate
    compositeFit.set_covariate(covariate=covariate, bsCovariates=bsCovariates)
    return compositeFit.intensity_from_return_time(tauReturn).intensity

def return_time_from_intensity(compositeFit, covariate, intensity):
    bsCovariates = multivariate_normal(2, 1).rvs(10000) # model accepts lots of variates of covariate
    compositeFit.set_covariate(covariate=covariate, bsCovariates=bsCovariates)
    return compositeFit.return_time_from_intensity(intensity).return_time
