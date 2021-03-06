#!/usr/bin/env python
#
# L. Brodeau, 2017

#
# Compute curl, aka relative vorticity from 2D vector on a lat-lon spherical
# grid a la ECMWF
#

import sys
import numpy as nmp
from netCDF4 import Dataset
import string

import barakuda_tool as bt

cv_wmod='wspd10m'

if len(sys.argv) != 4:
    print 'Usage: '+sys.argv[0]+' <FILE_VEC_V.nc> <name_Vx> <name_Vy>'
    sys.exit(0)

cf_Vx = sys.argv[1]
cv_Vx = sys.argv[2]
cv_Vy = sys.argv[3]


cf_Vy   = string.replace(cf_Vx, cv_Vx, cv_Vy)
cf_wmod = string.replace(cf_Vx, cv_Vx, cv_wmod)


print " cf_Vx = ", cf_Vx
print " cf_Vy = ", cf_Vy
print " cf_wmod = ", cf_wmod
print "\n"

rmult = 1.

if cv_Vx == 'EWSS':
    rmult = 1000.
    CUNIT_WMOD= '???'
    
if cv_Vx == 'U10M':
    rmult = 1.
    CUNIT_WMOD= 's^-1'



#  U
#  ~
bt.chck4f(cf_Vy)

f_Vy_in = Dataset(cf_Vy)

# Extracting the longitude and 1D array:
vlon     = f_Vy_in.variables['lon'][:]
clnm_lon = f_Vy_in.variables['lon'].long_name ; cunt_lon = f_Vy_in.variables['lon'].units
csnm_lon = f_Vy_in.variables['lon'].standard_name
print 'LONGITUDE: ', clnm_lon, cunt_lon, csnm_lon

# Extracting the longitude 1D array:
vlat     = f_Vy_in.variables['lat'][:]
clnm_lat = f_Vy_in.variables['lat'].long_name ; cunt_lat = f_Vy_in.variables['lat'].units
csnm_lat = f_Vy_in.variables['lat'].standard_name
print 'LATGITUDE: ', clnm_lat, cunt_lat, csnm_lat

# Extracting time 1D array:
vtime     = f_Vy_in.variables['time'][:] ; cunt_time = f_Vy_in.variables['time'].units
print 'TIME: ', cunt_time, '\n'

# Extracting a variable, ex: "t" the 3D+T field of temperature:
xty0    = f_Vy_in.variables[cv_Vy][0,:,:]
cunt_Vy = f_Vy_in.variables[cv_Vy].units
code_Vy = f_Vy_in.variables[cv_Vy].code
ctab_Vy = f_Vy_in.variables[cv_Vy].table
print cv_Vy+': ', cunt_Vy, code_Vy, ctab_Vy, '\n'




# V
# ~~~
bt.chck4f(cf_Vx)
f_Vx_in = Dataset(cf_Vx)
xtx0    = f_Vx_in.variables[cv_Vx][0,:,:]
cunt_Vx = f_Vx_in.variables[cv_Vx].units
code_Vx = f_Vx_in.variables[cv_Vx].code
ctab_Vx = f_Vx_in.variables[cv_Vx].table
print cv_Vx+': ', cunt_Vx, code_Vx, ctab_Vx, '\n'




# Checking dimensions
# ~~~~~~~~~~~~~~~~~~~
dim_Vy = xty0.shape ; dim_Vx = xtx0.shape
if dim_Vy != dim_Vx:
    print 'Shape problem!!!'; print dim_Vy , dim_Vx

print '\n'
Nt = len(vtime)
(nj, ni) = dim_Vy
print 'ni, nj, Nt = ', ni, nj, Nt



# Building Curl
# ~~~~~~~~~~~

xwmod = nmp.zeros(( nj, ni ))


# Creating output file
# ~~~~~~~~~~~~~~~~~~~~
f_out = Dataset(cf_wmod, 'w', format='NETCDF3_CLASSIC')

# Dimensions:
f_out.createDimension('lon', ni)
f_out.createDimension('lat', nj)
f_out.createDimension('time', None)

# Variables
id_lon = f_out.createVariable('lon','f4',('lon',))
id_lat = f_out.createVariable('lat','f4',('lat',))
id_tim = f_out.createVariable('time','f4',('time',))
id_wmod  = f_out.createVariable(cv_wmod,'f4',('time','lat','lon',))

# Attributes
id_tim.units = cunt_time

id_lat.long_name     = clnm_lat
id_lat.units         = cunt_lat
id_lat.standard_name = csnm_lat

id_lon.long_name     = clnm_lon
id_lon.units         = cunt_lon
id_lon.standard_name = csnm_lon

id_tim.units         = cunt_time

id_wmod.long_name = 'Curl of vector '+cv_Vx+' and '+cv_Vy
id_wmod.units = CUNIT_WMOD
id_wmod.code  = '???'
id_wmod.table = '128'

f_out.About = 'Created by Barakuda using '+cv_Vx+' and '+cv_Vy+'.'

# Filling variables:
id_lat[:] = vlat[:]
id_lon[:] = vlon[:]


for jt in range(Nt):
    
    print ' *** jt = ', jt

    xty = rmult*f_Vy_in.variables[cv_Vy][jt,:,:]
    xtx = rmult*f_Vx_in.variables[cv_Vx][jt,:,:]

    xwmod[:,:]      = nmp.sqrt(xtx*xtx + xty*xty)

    id_tim[jt]      = vtime[jt]
    id_wmod[jt,:,:] = xwmod[:,:] 

f_out.close()

f_Vx_in.close()
f_Vy_in.close()


print 'Bye!'

