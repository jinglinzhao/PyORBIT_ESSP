import numpy as np


from astropy.time import Time
def bjd_utc_to_tdb(utc):
    utc_astropy = Time(utc, scale='utc', format='jd')
    return utc_astropy.tdb.to_value('jd')

HS_dataset = np.genfromtxt('K2-141_HARPS_archive.dat')
HN_dataset = np.genfromtxt('K2-141_HARPN_DRS-235.rdb', skip_header=2)


fileout_rv   = open('K2-141_RV_PyORBIT.dat', 'w')
fileout_bis  = open('K2-141_BIS_PyORBIT.dat', 'w')
fileout_fwhm = open('K2-141_FWHM_PyORBIT.dat', 'w')
fileout_sind = open('K2-141_Sindex_PyORBIT.dat', 'w')


fileout_rv.write('# epoch value error jitter offset \n')
fileout_bis.write('# epoch value error jitter offset \n')
fileout_fwhm.write('# epoch value error jitter offset \n')
fileout_sind.write('# epoch value error jitter offset \n')


for bjd, rv, rv_e, bis, bis_e, fwhm, fwhm_e, sindex, sindex_e in zip(
    HN_dataset[:,0], #bjd_tdb
    HN_dataset[:,1], HN_dataset[:,2], #rv
    HN_dataset[:,5], HN_dataset[:,6], #bis
    HN_dataset[:,3], HN_dataset[:,4], #fwhm
    HN_dataset[:,9], HN_dataset[:,10], #bsindex
    ):

    fileout_rv.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, rv, rv_e))
    fileout_bis.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, bis, bis_e))
    fileout_fwhm.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, fwhm, fwhm_e))
    fileout_sind.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, sindex, sindex_e))

#bjd rv rv_error bis fwhm  sindex sindex_err texp snr
bjd_tdb = bjd_utc_to_tdb(2450000.0+HS_dataset[:, 0])
all_err = HS_dataset[:, 2]*2*1000.


for bjd, rv, rv_e, bis, bis_e, fwhm, fwhm_e, sindex, sindex_e in zip(
    bjd_tdb-2400000, #bjd_tdb
    HS_dataset[:,1]*1000., HS_dataset[:,2]*1000., #rv
    HS_dataset[:,3]*1000., all_err, #bis
    HS_dataset[:,4]*1000., all_err, #fwhm
    HS_dataset[:,5], HS_dataset[:,6], #bsindex
    ):

    fileout_rv.write('{0:12f} {1:9f} {2:9f} 1 1 \n'.format(bjd, rv, rv_e))
    fileout_bis.write('{0:12f} {1:9f} {2:9f} 1 1 \n'.format(bjd, bis, bis_e))
    fileout_fwhm.write('{0:12f} {1:9f} {2:9f} 1 1 \n'.format(bjd, fwhm, fwhm_e))
    fileout_sind.write('{0:12f} {1:9f} {2:9f} 1 1 \n'.format(bjd, sindex, sindex_e))


fileout_rv.close()
fileout_bis.close()
fileout_fwhm.close()
fileout_sind.close()