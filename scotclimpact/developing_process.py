import functools

import numpy  as np
import xarray as xr
import pandas as pd
from scipy.stats     import genextreme as genex
from scipy.stats     import multivariate_normal
from scipy.stats     import kstest
from scipy.stats     import norm
from scipy.stats     import lognorm
from datetime        import datetime

from .data import fetch_file

class Fitted_Obs_Sim():
    def __init__(self,
                 dsObs,
                 dsSim,
                 grid,
                 simParams      = ['c','loc1','scale1'],
                 preProcess     = True,
                 nVariates      = 1000,
                 storeInput     = False,
                 intensityUnits = u"\u00b0C",#'degrees_Celsius',
                 TScotVariates  = True):
        '''
        initialise with fitted parameter files from simulations and observations.
        When we have confirmed exactly how we want to do the de-biasing of simulations,
        these steps can be skipped by only providing the fully processed composite file.
        '''
        # align and transpose coordinates
        sameTranspose = lambda x: x.transpose('projection_x_coordinate','projection_y_coordinate',...)
        dsObs, dsSim, grid = xr.align(sameTranspose(dsObs), 
                                      sameTranspose(dsSim), 
                                      sameTranspose(grid), 
                                      join = 'inner', exclude = ['year', 'ensemble_member'])

        self.dsObs = dsObs.load(); self.dsSim = dsSim.load()
        
        self.TScotVariates  = TScotVariates
        self.intensityUnits = intensityUnits
        if storeInput: # if there is a need to keep full input files
            self.dsObsInput = self.dsObs.copy(deep = True)
            self.dsSimInput = self.dsSim.copy(deep = True)
        
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

        # block zero cross-covariance
        indexObsP = xr.where(np.isin(self.ds.params, simParams), 0, 1)
        indexSimP = xr.where(np.isin(self.ds.params, simParams), 1, 0)
        self.ds['iCovObsP']  = (['params_i','params_j'],
                                np.matmul(np.array([indexObsP]).T, [indexObsP]))
        self.ds['iCovSimP']  = (['params_i','params_j'],
                                np.matmul(np.array([indexSimP]).T, [indexSimP]))
        da = self.dsObs.bootstrap_covariance * self.ds.iCovObsP\
           + self.dsSim.bootstrap_covariance * self.ds.iCovSimP

        self.ds['bootstrap_covariance'] = da.compute()

        self.ds.coords['paramsGEV'] = ['c','loc','scale']
        
        self.fit            = self.ds.fit
        self.bootstrapMean  = self.ds.bootstrap_mean
        self.bootstrapCov   = self.ds.bootstrap_covariance
        self.fCovariateType = self.ds.covariateFunction
        
        self.dsObs = self.dsObs.stack(variate = ['year'])
        self.dsSim = self.dsSim.stack(variate = ['year','ensemble_member'])

        # a logarithmic scale function can be added here
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
                    linear_loc_log_scale= lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x, 
                                                                np.exp(p[3] + p[4]*x)]),
                    log_loc_scale       = lambda x,p: np.array([p[0], 
                                                                np.exp(p[1] + p[2]*x), 
                                                                np.exp(p[3] + p[4]*x)]),
                    quadratic_loc       = lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x + p[3]*x*x, 
                                                                p[4]]),
                    quadratic_loc_scale = lambda x,p: np.array([p[0], 
                                                                p[1] + p[2]*x + p[3]*x*x, 
                                                                p[4] + p[5]*x + p[6]*x*x]))
        self.fCovariate = displays[self.fCovariateType]

        ### pre-process bootstrap variates used to calculate confidence intervals
        self.nVariates  = nVariates
        self.bsVariates = None
        if preProcess: self.variate_bootstrap_dist(nVariates)

    def get_xy_indices(self, x, y):
        return np.argmin(np.abs(self.grid.projection_x_coordinate.values - x)),\
               np.argmin(np.abs(self.grid.projection_y_coordinate.values - y))

    def variate_bootstrap_dist(self, nVariates = 1000):
        '''
        produce random variates of the bootstrap parameters
        '''
        def f(mean, cov, nVariates): 
            if (not np.isfinite(mean).all()) or (not np.isfinite(cov).all()):
                return np.array([[np.nan]*mean.size]*nVariates)
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

    def get_temperature_anomaly_params(self, Tanomaly):
        '''
        convert a set global temperature anomaly into the covariate.
        Equation in report, uses fits to: 
        Scotland average temperature using HadUK-Grid,
        Scotland sensitivity using UKCP18 60km GCM and 12km RCP,
        global temperature anomaly using HadCRUT5 ensemble,
        '''
        m = [-0.264, 0.825, 0.998]#mu from normal fits
        s = [ 0.090, 0.094, 0.040]#sigma from normal fits
        mean = m[0] + m[1] * (Tanomaly - m[2])
        if type(self.bsVariates) == type(None):
            return mean
        elif self.TScotVariates == False:#if we don't want to unclude uncertainty in TScot
            return mean, np.array([mean]*self.nVariates)            
        else:
            std  = np.sqrt(s[0]**2 + (s[1]*(Tanomaly - m[2]))**2 + (m[1]*s[2])**2)
            return mean, norm.rvs(mean, std, self.nVariates)
    
    def set_temperature_anomaly(self, Tanomaly):
        m,v = self.get_temperature_anomaly_params(Tanomaly)
        self.set_covariate(m, bsCovariates = v)
       
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
            
    def apply_units(self, da, 
                    units = '',
                    attrs = dict()):
        da.attrs['units'] = units
        for k in attrs.keys():
            da.attrs[k] = attrs[k]
        return da
    
    def output_modes(self, x, grid, output, units = '', attrs = dict()):
        if output != 'dataarray':
            return x
        else:
            return self.apply_units(x*grid, units, attrs)

    def intensity_from_return_time(self, tauReturn, mode = 'fit', output = 'dataarray', quantiles = [0.025,0.975]):
        if (mode == 'variates') or (mode == 'quantiles'):
            fit = self.intensity_from_return_time(tauReturn, mode = 'fit')
            bss = self.intensity_from_return_time(tauReturn, mode = 'bs')
            if mode == 'quantiles':
                ds = xr.merge([fit, bss.quantile(quantiles, dim = 'variate')\
                         .rename(intensity = 'intensity_quantiles')])
            else:
                ds = xr.merge([fit, bss.rename(intensity = 'intensity_variates')])
            return self.apply_units(ds, units = self.intensityUnits)
        elif mode == 'fit':
                x    = self.fitGEV.ppf(1-1/tauReturn)
                grid = self.grid.mask.rename('intensity')
        elif mode == 'bs':
                x    = self.bsfitGEV.ppf(1-1/tauReturn)
                grid = self.bsGrid.mask.rename('intensity')
        return self.output_modes(x, grid, output, 
            units = self.intensityUnits,
            attrs = dict(
                description = 'intensity at %d year return time'%tauReturn),
                    ).to_dataset()

    def return_time_from_intensity(self, intensity, mode = 'fit', output = 'dataarray', quantiles = [0.025,0.975]):
        if (mode == 'variates') or (mode == 'quantiles'):
            fit = self.return_time_from_intensity(intensity, mode = 'fit')
            bss = self.return_time_from_intensity(intensity, mode = 'bs')
            if mode == 'quantiles':
                ds = xr.merge([fit, bss.quantile(quantiles, dim = 'variate')\
                         .rename(return_time = 'return_time_quantiles')])
            else:
                ds = xr.merge([fit, bss.rename(return_time = 'return_time_variates')])
            return self.apply_units(ds, units = 'years')
        elif mode == 'fit':
                x    = 1/self.fitGEV.sf(intensity)
                grid = self.grid.mask.rename('return_time')
        elif mode == 'bs':
                x    = 1/self.bsfitGEV.sf(intensity)
                grid = self.bsGrid.mask.rename('return_time')
        return self.output_modes(x, grid, output, 
            units = 'year',
            attrs = dict(
                description = 'return time of %0.1f %s'%(intensity,self.intensityUnits)),
                    ).to_dataset()
        
    def times_more_likely(self, intensity, cov0, cov1, 
                          bsCovs0 = None, bsCovs1 = None,
                          mode = 'quantiles',
                          quantiles = [0.025,0.975]):
        '''
        compare how many times more likely an event is at cov1 than at cov0
        '''
        self.set_covariate(cov0, bsCovs0)
        r0   = self.return_time_from_intensity(intensity, mode = 'fit', output = 'dataarray')
        bsR0 = self.return_time_from_intensity(intensity, mode =  'bs', output = 'dataarray')
        
        self.set_covariate(cov1, bsCovs1)
        r1   = self.return_time_from_intensity(intensity, mode = 'fit', output = 'dataarray')
        bsR1 = self.return_time_from_intensity(intensity, mode =  'bs', output = 'dataarray')

        if mode == 'quantiles':
            return self.apply_units(xr.merge([
                (r0/r1).rename(return_time = 'times_more_likely'),
                (bsR0/bsR1).rename(return_time='times_more_likely_quantiles')\
                                    .times_more_likely_quantiles.quantile(quantiles, dim = 'variate')]),
                    'times_more_frequent',
                            attrs = dict(
                    description = 'ratio of return times at cov%0.1f vs cov%0.1f of %0.1f %s'\
                                %(cov0, cov1, intensity, self.intensityUnits)))
        if mode == 'variates':
            return self.apply_units(xr.merge([
                (r0/r1).rename(return_time = 'times_more_likely'),
                         (bsR0/bsR1).rename(return_time='times_more_likely_variates')]),
                    'times_more_frequent',
                            attrs = dict(
                    description = 'ratio of return times at cov%0.1f vs cov%0.1f of %0.1f %s'\
                                %(cov0, cov1, intensity, self.intensityUnits)))
            
    def times_more_likely_T(self, intensity, T0, T1,
                          mode = 'quantiles',
                          quantiles = [0.025,0.975]):
        
        cov0, bsCovs0 = self.get_temperature_anomaly_params(T0)
        cov1, bsCovs1 = self.get_temperature_anomaly_params(T1)
        
        return self.times_more_likely(intensity, cov0, cov1, 
                          bsCovs0, bsCovs1,
                          mode = mode,
                          quantiles = quantiles)
    
    def change_in_intensity(self, return_time, cov0, cov1, 
                          bsCovs0 = None, bsCovs1 = None,
                          mode = 'quantiles',
                          quantiles = [0.025,0.975]):
        '''
        compare how many times more likely an event is at cov1 than at cov0
        '''
        self.set_covariate(cov0, bsCovs0)
        r0   = self.intensity_from_return_time(return_time, mode = 'fit', output = 'dataarray')
        bsR0 = self.intensity_from_return_time(return_time, mode =  'bs', output = 'dataarray')
        
        self.set_covariate(cov1, bsCovs1)
        r1   = self.intensity_from_return_time(return_time, mode = 'fit', output = 'dataarray')
        bsR1 = self.intensity_from_return_time(return_time, mode =  'bs', output = 'dataarray')

        if mode == 'quantiles':
            return self.apply_units(xr.merge([
                (r1-r0).rename(intensity = 'intensity_change'),
                (bsR1-bsR0).rename(intensity='intensity_change_quantiles')\
                                    .intensity_change_quantiles.quantile(quantiles, dim = 'variate')]),
                    self.intensityUnits,
                            attrs = dict(
                    description = 'change in intensity at cov%0.1f vs cov%0.1f at return time of %d years'\
                                %(cov0, cov1, return_time)))
        if mode == 'variates':
            return self.apply_units(xr.merge([
                (r1-r0).rename(intensity = 'intensity_change'),
                (bsR1-bsR0).rename(intensity='intensity_change_variates')]),
                    self.intensityUnits,
                            attrs = dict(
                    description = 'change in intensity at cov%0.1f vs cov%0.1f at return time of %d years'\
                                %(cov0, cov1, return_time)))

    def change_in_intensity_T(self, return_time, T0, T1,
                              mode = 'quantiles',
                              quantiles = [0.025,0.975]):
            
        cov0, bsCovs0 = self.get_temperature_anomaly_params(T0)
        cov1, bsCovs1 = self.get_temperature_anomaly_params(T1)
            
        return self.change_in_intensity(return_time, cov0, cov1, 
                              bsCovs0, bsCovs1,
                              mode = mode,
                              quantiles = quantiles)
    def get_variates_dist(self, calculation,
                 xIndex    = None,      yIndex = None,
                 intensity = None, return_time = None,
                 T0        = None,          T1 = None):
        '''
        can add raise statements here
        '''
        if calculation == 'intensity_from_return_time':
            dataset = self.intensity_from_return_time(return_time, mode = 'variates')
        elif calculation == 'return_time_from_intensity':
            dataset = self.return_time_from_intensity(intensity, mode = 'variates')
        elif calculation == 'change_in_intensity':
            dataset = self.change_in_intensity_T(return_time, T0 = T0, T1 = T1, mode = 'variates')
        elif calculation == 'times_more_likely':
            dataset = self.times_more_likely_T(intensity, T0 = T0, T1 = T1, mode = 'variates')
        
        if (type(xIndex) != type(None)) and (type(yIndex) != type(None)):
            dataset = dataset.isel(projection_x_coordinate = xIndex,
                                   projection_y_coordinate = yIndex)
        return dataset

    def get_CI_report(self, calculation, 
                 report    = 'central_CI',
                 quantiles = [0.025,0.975],
                 xIndex    = None,      yIndex = None,
                 intensity = None, return_time = None,
                 T0        = None,          T1 = None):
        '''
        can add raise statements here
        '''
        if report == 'calibrated_confidence':
            quantiles = [0.05,0.1,0.25,0.75,0.9,0.95]
        #-----------------------------------------------------------
        if calculation == 'intensity_from_return_time':
            mv = np.inf
            dataset = self.intensity_from_return_time(return_time, 
                                                      mode = 'quantiles', quantiles = quantiles)
            var     = 'intensity'
        #-----------------------------------------------------------            
        elif calculation == 'return_time_from_intensity':
            mv = 200
            dataset = self.return_time_from_intensity(intensity, 
                                                      mode = 'quantiles', quantiles = quantiles)
            var     = 'return_time'
        #-----------------------------------------------------------           
        elif calculation == 'change_in_intensity':
            mv = np.inf
            dataset = self.change_in_intensity_T(return_time, T0 = T0, T1 = T1, 
                                                      mode = 'quantiles', quantiles = quantiles)
            var     = 'intensity_change'
        #-----------------------------------------------------------            
        elif calculation == 'times_more_likely':
            mv = 50
            dataset = self.times_more_likely_T(intensity, T0 = T0, T1 = T1,
                                                      mode = 'quantiles', quantiles = quantiles)
            var     = 'times_more_likely'
        #-----------------------------------------------------------        
        if (type(xIndex) != type(None)) and (type(yIndex) != type(None)):
            dataset = dataset.isel(projection_x_coordinate = xIndex,
                                   projection_y_coordinate = yIndex)
            def two_sigfigs(num):
                return '%d'%float(f"{num:.{2}g}")
            def formatVal(q, mv, var): 
                if (q > mv) or (np.isnan(q)): 
                    q = 'more than ' + str(mv)
                elif (var == 'intensity')\
                  or (var == 'intensity_change')\
                  or (q < 10):                         
                    q = '%0.1f'%q
                else: 
                    q = two_sigfigs(q)
                return q

            qs = [dataset[var]]
            for qi in quantiles:
                qs.append(dataset[var+'_quantiles'].sel(quantile = qi).values)
            qs = [formatVal(q, mv, var) for q in qs]
            
            if report == 'central_CI':
                return '%s (%s — %s) %s'%(qs[0], qs[1], qs[2],
                                          dataset.attrs['units'].replace('_',' '))
            if report == 'calibrated_confidence':# calibrated language for 90%, 80%, 50% confidence intervals from IPCC AR4 guidance
                return\
                       'Central estimate:     %s %s\n'%(qs[0],dataset.attrs['units'].replace('_',' '))\
                      +'Very High confidence: %s to %s %s\n'%(qs[1],qs[6],
                                                dataset.attrs['units'].replace('_',' '))\
                      +'High confidence:      %s to %s %s\n'%(qs[2],qs[5],
                                                dataset.attrs['units'].replace('_',' '))\
                      +'Medium confidence:    %s to %s %s\n'%(qs[3],qs[4],
               
                                                              dataset.attrs['units'].replace('_',' '))
        return dataset

    def get_KS_test_p(self, data, distribution, nParams):
        def fit_and_p(variates,distribution,nParams):
            if not np.isfinite(variates).all():
                fit = np.nan*np.empty(nParams)
                p   = np.array([np.nan])
            else:
                fit = np.array(distribution.fit(variates))
                p   = np.array([kstest(variates, fit, alternative = 'less').pvalue])
            return fit, p
        fit, p = xr.apply_ufunc(
                    fit_and_p,
                    data,
                    distribution,
                    nParams,
                    input_core_dims = [['variate'],[],[]],
                    output_core_dims = [['fit'],[]],
                    exclude_dims = set(('variate',)),
                    vectorize = True)
        return xr.merge(
                [fit.to_dataset(name = 'dist_fit'), 
                   p.to_dataset(name = 'KS_test')])
        
    def test_dist(self, data, distribution = 'default', 
                  nParams = 3, threshold = 0.05, return_fit = False):
        if distribution == 'default': distribution = lognorm
        ks   = self.get_KS_p(data, distribution, nParams)
        test = xr.where(np.isnan(ks.KS_test), np.nan, 
                        xr.where(ks.KS_test<threshold, 1, 0))
        if return_fit: return test, ks
        else: return test

    def renormalise(self, data = 'obs', dataCovariate = 'obs', dataFit = 'obs'):
        if data == 'obs':
            data          = self.dsObs.tasmax
            dataCovariate = self.dsObs.covariate
            dataFit       = self.dsObs.fit
        elif data == 'sim':
            data          = self.dsSim.tasmax
            dataCovariate = self.dsSim.covariate
            dataFit       = self.dsSim.fit
        shape, loc, scale = self.fCovariate(
                    dataCovariate,
                    [dataFit.sel(params = p).broadcast_like(data)\
                     for p in self.ds.params])
        renorm = ((data - loc)/scale).to_dataset(name = 'renormalised_data')
        return renorm

    def ks_compare(self):
        '''
        identify if the input observations and simulations follow the same distribution
        '''
        renormObs = self.renormalise(data = 'obs')
        renormSim = self.renormalise(data = 'sim')
        return xr.apply_ufunc(
            lambda a,b: np.array( [kstest(a,b).pvalue]),
            renormObs,
            renormSim,
            input_core_dims = [['variate'],['variate']],
            output_core_dims = [[]],
            exclude_dims = set(('variate',)),
            vectorize = True)\
            .rename(renormalised_data = 'test')

    def calculate_overlap(self, n = 1e4, calculationMode = 'array'):
        '''
        calculate the overlap of the distributions of parameters in 
        observations and simulations
        '''
        x = self.dsObs
        xVar = x.bootstrap_covariance.where(x.params_i == x.params_j, 0)
        xMu  = x.fit
        y = self.dsSim
        yVar = y.bootstrap_covariance.where(y.params_i == y.params_j, 0)        
        yMu  = y.fit
        
        def overlap(m0, v0, m1, v1, n = 1000, nd = (5,)): 
            '''
            estimate shared area
            '''
            n = int(n)
            s0 = np.sqrt(v0.diagonal(axis1 = -2, axis2 = -1))
            s1 = np.sqrt(v1.diagonal(axis1 = -2, axis2 = -1))
        
            N0       = norm(m0, s0)
            N1       = norm(m1, s1)
            
            bounds   = [np.nan_to_num(np.min([m0-3*s0, m1-3*s1], axis = 0),0),
                        np.nan_to_num(np.max([m0+3*s0, m1+3*s1], axis = 0),0)]
        
            scale    = bounds[1]-bounds[0]
            tests    = np.random.uniform(bounds[0],bounds[1],(n,) + nd)
            overlap  = np.min([N0.pdf(tests), N1.pdf(tests)], axis = 0)
            return overlap.sum(axis = 0) * scale / n

        if calculationMode == 'array':#fast for small memory
            self.ds['overlap'] = (['projection_y_coordinate',
                                   'projection_x_coordinate',
                                   'params'],
                        overlap(xMu.values,xVar.values,
                                yMu.values,yVar.values,
                                nd = (self.ds.projection_y_coordinate.size, 
                                      self.ds.projection_x_coordinate.size, 
                                      self.ds.params.size), 
                                n = n))
        if calculationMode == 'cellwise':#less memory intensive
            self.ds['overlap'] = xr.apply_ufunc(
                        overlap,
                        xMu,xVar,
                        yMu,yVar,
                        n,
                        input_core_dims = [['params'],['params_i','params_j'],
                                           ['params'],['params_i','params_j'],[],],
                        output_core_dims = [['params']],
                        vectorize = True).compute()
        return self.ds.overlap

    def apply_metadata(self, da,
                       other    = dict(),
                       creator  = 'default',#this needs to be decided by adaptation team
                       user     = 'default',#let users credit themselves for their request
                      ):
        da.attrs[      'creator'] = creator
        da.attrs[       'source'] = 'Scottish Climate Scenario Decision-Making Web-Tool. This data product is built on other data from: UK Climate Projections (UKCP18), UK observations (HadUK-Grid), Global temperature anomalies (HadCRUT5), Regional boundaries from spatialdata.gov.scot.'
        da.attrs[         'user'] = user
        da.attrs['creation_date'] = datetime.today().strftime('%Y-%m-%d')
        da.attrs[  'institution'] = 'Researcher at The University of Edinburgh, using JASMIN'
        da.attrs[      'comment'] = 'This data product was produced via a Scottish Government funded ClimateXChange project in 2025/26. ClimateXChange is one of five centres of expertise funded by Scottish Government. The centres work at the interface between policy and research, and provide responsive work in areas of high policy importance: climate change (ClimateXChange), animal disease outbreaks (EPIC), plant health (Scotland’s Plant Health Centre), water (CREW) and knowledge exchange and impact (SEFARI Gateway). The centres of expertise work jointly to make sure policymakers have easy access to research, help prioritise scientific resources in line with society’s priorities and create new partnerships with research institutes and universities.'
        for k in other.keys(): da.attrs[k] = other[k]
        return da

    def download_data(self, da,
                      fileType = 'netCDF',
                      other    = dict(),
                      creator  = 'Climate Hazards Tool',
                      user     = 'Tool User',
                      ):
        self.apply_metadata(da, other, creator, user)
        if fileType == 'netCDF':
            da.to_netcdf('hazard_download.nc')
        if fileType == 'csv': 
            df = da.to_dataframe()
            df.attrs = da.attrs
            with open('hazard_download.csv', 'w', encoding='utf-8') as f:
                # Write metadata
                if df.attrs:
                    for key, value in df.attrs.items():
                        f.write(f'# {key}: {value}\n')
        # Write CSV
                df.to_csv(f, index=True)
    

        #df.attrs = da.attrs
        #compression_opts = dict(method='zip',archive_name='out.csv')  
        #df.to_csv('hazard_download.zip', index=False,
        #compression=compression_opts) 

    def list_dataset_info(self, ds, mode = 'full'):
        '''
        list dataset info for including with output.
        '''
        info = []
        if type(ds) == 'xarray.core.dataset.Dataset':
            info.append("=== GLOBAL ATTRIBUTES ===")
        else:
            info.append("=== ATTRIBUTES ===")
        for attr, value in ds.attrs.items():
            info.append(f"{attr}: {value}")
        info.append("\n" + "="*50 + "\n")

        if mode == 'full':
            if type(ds) == 'xarray.core.dataset.Dataset':
                info.append("=== VARIABLES ===")
                for var_name in ds.data_vars:
                    var = ds[var_name]
                    info.append(f"{var_name}:")
                    info.append(f"  Dimensions: {var.dims}")
                    info.append(f"  Shape: {var.shape}")
                    info.append(f"  Data type: {var.dtype}")
                    if var.attrs:
                        info.append("  Attributes:")
                        for attr, val in var.attrs.items():
                            info.append(f"    {attr}: {val}")
                    info.append('')
                info.append("="*50 + "\n")
            
            info.append("=== COORDINATES ===")
            for coord_name in ds.coords:
                coord = ds[coord_name]
                info.append(f"{coord_name}:")
                info.append(f"  Dimensions: {coord.dims}")
                info.append(f"  Shape: {coord.shape}")
                info.append(f"  Data type: {coord.dtype}")
                if coord.attrs:
                    info.append("  Attributes:")
                    for attr, val in coord.attrs.items():
                        info.append(f"    {attr}: {val}")
                info.append('')
        return info
        
@functools.lru_cache(maxsize=16)
def init_composite_fit(model_file, grid_size, simParams='c,loc1,scale0,scale1', nVariates=10000, preProcess=True, **kwargs):
    simParams = simParams.split(',')
    dsObs = xr.open_dataset(fetch_file('model_fits/obs/'+model_file%'HadUK'))
    dsSim = xr.open_dataset(fetch_file('model_fits/sim/'+model_file%'UKCP18'))
    grid = xr.open_dataset(fetch_file('grids/gridWide_g%i.nc'%grid_size))\
             .sel(projection_y_coordinate = slice(4e5,13e5),
                  projection_x_coordinate = slice(0,5e5))
    dsSim, dsObs, grid = xr.align(dsSim, dsObs, grid, join = 'outer', exclude = ['year', 'ensemble_member'], fill_value  = np.nan)

    return Fitted_Obs_Sim(dsObs, dsSim, grid, simParams = simParams, nVariates = nVariates, preProcess = preProcess, **kwargs)


def intensity_from_return_time(compositeFit, covariate, tauReturn):
    compositeFit.set_temperature_anomaly(covariate)
    return compositeFit.intensity_from_return_time(tauReturn).intensity

def return_time_from_intensity(compositeFit, covariate, intensity):
    compositeFit.set_temperature_anomaly(covariate)
    return compositeFit.return_time_from_intensity(intensity).return_time

def change_in_intensity(compositeFit, return_time, cov0, cov1):
    return compositeFit.change_in_intensity(return_time, cov0, cov1).intensity_change

def change_in_frequency(compositeFit, intensity, cov0, cov1):
    return compositeFit.times_more_likely(intensity, cov0, cov1).times_more_likely

def intensity_ci_report(compositeFit, cov, return_time, x_idx, y_idx):
    compositeFit.set_temperature_anomaly(cov)
    return compositeFit.get_CI_report(
        'intensity_from_return_time',
        report='calibrated_confidence',
        return_time=return_time,
        T0=cov,
        xIndex=x_idx,
        yIndex=y_idx,
    )

def return_time_ci_report(compositeFit, cov, intensity, x_idx, y_idx):
    compositeFit.set_temperature_anomaly(cov)
    return compositeFit.get_CI_report(
        'return_time_from_intensity',
        report='calibrated_confidence',
        intensity=intensity,
        xIndex=x_idx,
        yIndex=y_idx,
    )

def change_in_intensity_ci_report(compositeFit, return_time, cov0, cov1, x_idx, y_idx):
    return compositeFit.get_CI_report(
        'change_in_intensity',
        report='calibrated_confidence',
        return_time=return_time,
        T0=cov0,
        T1=cov1,
        xIndex=x_idx,
        yIndex=y_idx,
    )

def change_in_frequency_ci_report(compositeFit, intensity, cov0, cov1, x_idx, y_idx):
    return compositeFit.get_CI_report(
        'times_more_likely',
        report='calibrated_confidence',
        intensity=intensity,
        T0=cov0,
        T1=cov1,
        xIndex=x_idx,
        yIndex=y_idx,
    )

