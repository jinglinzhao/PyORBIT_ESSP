import numpy as np


from astropy.time import Time
def bjd_utc_to_tdb(utc):
    utc_astropy = Time(utc, scale='utc', format='jd')
    return utc_astropy.tdb.to_value('jd')

S1_dataset = np.genfromtxt('TOI1807_data_season01.dat')
S2_dataset = np.genfromtxt('TOI1807_data_season02.dat')


fileout_rv   = open('TOI1807_RV_s01_PyORBIT.dat', 'w')
fileout_bis  = open('TOI1807_BIS_s01_PyORBIT.dat', 'w')
fileout_logrhk = open('TOI1807_logRHK_s01_PyORBIT.dat', 'w')


fileout_rv.write('# epoch value error jitter offset \n')
fileout_bis.write('# epoch value error jitter offset \n')
fileout_logrhk.write('# epoch value error jitter offset \n')


for bjd, rv, rv_e, logrhk, logrhk_e, bis in zip(
    S1_dataset[:,0], #bjd_tdb
    S1_dataset[:,1]*1000., S1_dataset[:,2]*1000., #rv
    S1_dataset[:,3], S1_dataset[:,4], #logrhk
    S1_dataset[:,5]*1000.  #bis
    ):

    fileout_rv.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, rv, rv_e))
    fileout_bis.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, bis, rv_e*np.sqrt(2)))
    fileout_logrhk.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, logrhk, logrhk_e))


fileout_rv.close()
fileout_bis.close()
fileout_logrhk.close()



fileout_rv   = open('TOI1807_RV_s02_PyORBIT.dat', 'w')
fileout_bis  = open('TOI1807_BIS_s02_PyORBIT.dat', 'w')
fileout_logrhk = open('TOI1807_logRHK_s02_PyORBIT.dat', 'w')


fileout_rv.write('# epoch value error jitter offset \n')
fileout_bis.write('# epoch value error jitter offset \n')
fileout_logrhk.write('# epoch value error jitter offset \n')


for bjd, rv, rv_e, logrhk, logrhk_e, bis in zip(
    S2_dataset[:,0], #bjd_tdb
    S2_dataset[:,1]*1000., S2_dataset[:,2]*1000., #rv
    S2_dataset[:,3], S2_dataset[:,4], #logrhk
    S2_dataset[:,5]*1000.  #bis
    ):

    fileout_rv.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, rv, rv_e))
    fileout_bis.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, bis, rv_e*np.sqrt(2)))
    fileout_logrhk.write('{0:12f} {1:9f} {2:9f} 0 0 \n'.format(bjd, logrhk, logrhk_e))


fileout_rv.close()
fileout_bis.close()
fileout_logrhk.close()
