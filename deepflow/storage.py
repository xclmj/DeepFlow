import xarray as xr
import pandas as pd
import numpy as np


def to_deltas(dt):
    """
    Convert from delta-ts to time steps
    :param dt: range of delta ts
    :return: range of time steps
    """
    dts = [dt[0]]
    for i in range(1, len(dt)):
        dts.append(dts[i-1]+dt[i])
    return np.array(dts)


def create_dataset(prod_data, prod_data_forecast, material_props, material_grads, latent_vars, prior_latent_vars, grad_latent_vars, misfit_vals):
    """
    Storage scheme for xarray dataframe
    :param prod_data: Production data of current iteration
    :param prod_data_forecast: Used if production data and forecast have different length (experimental)
    :param material_props: Porosity and Permeability Grids
    :param material_grads: Derivatives of objective function with respect to porosity and permeability
    :param latent_vars: latent variable vector z
    :param prior_latent_vars: latent variable vector of previous time step
    :param grad_latent_vars: gradients on the latent vectors
    :param misfit_vals: objective function value
    :return: stores the xarray dataframe to disk
    """
    dt_1 = to_deltas([1, 1, 3, 5, 5, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15])
    dt_2 = 150+to_deltas(np.array([15]*10))
    dt_3 = 300+to_deltas([25]*6)
    dt_4 = 450+to_deltas([25]*6)

    dts_forecast = np.concatenate([dt_1, dt_2, dt_3, dt_4])

    control = pd.TimedeltaIndex(pd.to_timedelta(dts_forecast, unit='d'))
    control_forecast = pd.TimedeltaIndex(pd.to_timedelta(dts_forecast, unit='d'))

    t0 = pd.Timestamp('20190101')

    data = prod_data
    locs = ['Injector', 'Producer']
    states = ['pressure', 'oil-rate', 'water-rate', 'water-cut']
    times = control+t0
    state_variables = xr.DataArray(data, coords=[locs, states, times], dims=['well', 'state_variable', 'time'])

    data = prod_data_forecast
    locs = ['Injector', 'Producer']
    states = ['pressure', 'oil-rate', 'water-rate', 'water-cut']
    times_full = control_forecast+t0
    state_variables_forecast = xr.DataArray(data, coords=[locs, states, times_full], dims=['well', 'state_variable', 'time'])

    data = material_props
    properties = ['Porosity', 'Permeability']
    n_grid_block_indices = range(64)
    m_grid_block_indices = range(128)
    material_properties = xr.DataArray(data, coords=[properties, n_grid_block_indices, m_grid_block_indices], dims=['property', 'Nx', 'Ny'])

    data = material_grads
    properties = ['dJdp', 'dJdkx' , 'dJdky', 'dJdkz']
    n_grid_block_indices = range(64)
    m_grid_block_indices = range(128)
    material_derivatives = xr.DataArray(data, coords=[properties, n_grid_block_indices, m_grid_block_indices], dims=['derivative', 'Nx', 'Ny'])

    data = latent_vars
    properties = ['z']
    variable_indices = range(50)
    n_grid_block_indices = range(2)
    m_grid_block_indices = range(1)
    latent_variables = xr.DataArray(data, coords=[properties, variable_indices, n_grid_block_indices, m_grid_block_indices], dims=['latent_variable', 'z', 'nx', 'ny'])

    data = prior_latent_vars
    properties = ['z_prior']
    variable_indices = range(50)
    n_grid_block_indices = range(2)
    m_grid_block_indices = range(1)
    prior_latent_variables = xr.DataArray(data, coords=[properties, variable_indices, n_grid_block_indices, m_grid_block_indices], dims=['latent_variable', 'z', 'nx', 'ny'])
 

    data = grad_latent_vars
    properties = ['dJdz']
    variable_indices = range(50)
    n_grid_block_indices = range(2)
    m_grid_block_indices = range(1)
    grad_latent_variables = xr.DataArray(data, coords=[properties, variable_indices, n_grid_block_indices, m_grid_block_indices], dims=['latent_variable', 'z', 'nx', 'ny'])
    
    data = misfit_vals
    properties = ['dJ']
    misfit_indices = range(5)
    misfit_values = xr.DataArray(data, coords=[properties, misfit_indices], dims=['functional', 'i'])

    iteration_ds = xr.Dataset({'state_variables': state_variables, 'state_variables_full': state_variables_forecast,
                           'material_properties': material_properties,
                           'material_derivatives': material_derivatives, 
                           'latent_variables': latent_variables,
                           'prior_latent_variables':prior_latent_variables,
                           'latent_variable_derivatives': grad_latent_variables,
                           'misfit_value': misfit_values})
    return iteration_ds


def create_ref_dataset(prod_data, material_props):
    dt_1 = to_deltas([1, 1, 3, 5, 5, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15])
    dt_2 = 150+to_deltas(np.array([15]*10))
    dt_3 = 300+to_deltas([25]*6)
    dt_4 = 450+to_deltas([25]*6)
    dts = np.concatenate([dt_1, dt_2, dt_3, dt_4])

    control = pd.TimedeltaIndex(pd.to_timedelta(dts, unit='d'))

    t0 = pd.Timestamp('20190101')

    data = prod_data
    locs = ['Injector', 'Producer']
    states = ['pressure', 'oil-rate', 'water-rate', 'water-cut']
    times = control+t0
    state_variables = xr.DataArray(data, coords=[locs, states, times], dims=['well', 'state_variable', 'time'])

    data = material_props
    properties = ['Porosity', 'Permeability']
    n_grid_block_indices = range(64)
    m_grid_block_indices = range(128)
    material_properties = xr.DataArray(data, coords=[properties, n_grid_block_indices, m_grid_block_indices], dims=['property', 'Nx', 'Ny'])

    iteration_ds = xr.Dataset({'state_variables': state_variables, 'material_properties': material_properties})
    return iteration_ds