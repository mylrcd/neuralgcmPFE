# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import importlib.resources
import pickle

from absl.testing import absltest
from dinosaur import horizontal_interpolation
from dinosaur import pytree_utils
from dinosaur import spherical_harmonic
import jax
import neuralgcm
from neuralgcm import api
import numpy as np
import xarray


def horizontal_regrid(
    regridder: horizontal_interpolation.Regridder, dataset: xarray.Dataset
) -> xarray.Dataset:
  """Horizontally regrid an xarray Dataset."""
  # TODO(shoyer): consider moving to public API
  regridded = xarray.apply_ufunc(
      regridder,
      dataset,
      input_core_dims=[['longitude', 'latitude']],
      output_core_dims=[['longitude', 'latitude']],
      exclude_dims={'longitude', 'latitude'},
      vectorize=True,  # loops over level, for lower memory usage
  )
  regridded.coords['longitude'] = np.rad2deg(regridder.target_grid.longitudes)
  regridded.coords['latitude'] = np.rad2deg(regridder.target_grid.latitudes)
  return regridded


class APITest(absltest.TestCase):

  def test_stochastic_model_basics(self):
    timesteps = 3
    dt = np.timedelta64(1, 'h')

    # load model
    package = importlib.resources.files(neuralgcm)
    file = package.joinpath('data/tl63_stochastic_mini.pkl')
    ckpt = pickle.loads(file.read_bytes())
    model = api.PressureLevelModel.from_checkpoint(ckpt)

    # load data
    with package.joinpath('data/era5_tl31_19590102T00.nc').open('rb') as f:
      ds_tl31 = xarray.load_dataset(f).expand_dims('time')
    regridder = horizontal_interpolation.ConservativeRegridder(
        spherical_harmonic.Grid.TL31(), model.data_coords.horizontal
    )
    ds_in = horizontal_regrid(regridder, ds_tl31)
    data, forcings = model.data_from_xarray(ds_in)
    data_in, forcings_in = pytree_utils.slice_along_axis(
        (data, forcings), axis=0, idx=0
    )

    # run model
    encoded = model.encode(data_in, forcings_in, rng_key=jax.random.key(0))
    _, data_out = model.unroll(
        encoded, forcings, steps=timesteps, timedelta=dt, start_with_input=True
    )

    # convert to xarray
    t0 = ds_tl31.time.values[0]
    times = np.arange(t0, t0 + timesteps * dt, dt)
    ds_out = model.data_to_xarray(data_out, times=times)

    # validate
    actual = ds_out.head(time=1)
    expected = ds_in.drop_vars(['sea_surface_temperature', 'sea_ice_cover'])

    # check matching variable shapes
    xarray.testing.assert_allclose(actual, expected, atol=1e6)

    # check that round-tripping the initial condition is approximately correct
    typical_relative_error = abs(actual - expected).median() / expected.std()
    tolerance = xarray.Dataset({
        "u_component_of_wind": 0.04,
        "v_component_of_wind": 0.08,
        "temperature": 0.02,
        "geopotential": 0.0005,
        "specific_humidity": 0.003,
        "specific_cloud_liquid_water_content": 0.12,
        "specific_cloud_ice_water_content": 0.15,
    })
    self.assertTrue(
        (typical_relative_error < tolerance).to_array().values.all(),
        msg=f"typical relative error is too large:\n{typical_relative_error}",
    )

    # TODO(shoyer): test decode()
    # TODO(shoyer): verify RNG key works correctly
    # TODO(shoyer): verify RNG key is optional for deterministic models


if __name__ == '__main__':
  absltest.main()