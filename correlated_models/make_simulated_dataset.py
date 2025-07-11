import numpy as np
import matplotlib .pyplot as plt

x_mod = np.arange(0,100,1)
x_obs = np.random.normal(x_mod, 0.2)


P = 14.35
K = 10.
Tc = 2.453

zero = 25.
half_range = 25.
c1 = 5



z_mod = np.random.uniform(zero-half_range, zero+half_range, size=len(x_mod))

sin_mod = - K * np.sin((x_obs-Tc)/P * 2*np.pi)
cor_mod = np.random.normal(c1*(z_mod-zero), 5)
y_mod = sin_mod + cor_mod
y_obs = np.random.normal(y_mod, np.sqrt(2.))

m_size = 2
plt.scatter(x_obs, sin_mod, s=m_size, label='sin')

plt.scatter(x_obs, y_mod, s=m_size, label='y_mod')
plt.scatter(x_obs, y_obs, s=m_size, label='y_obs')
plt.legend()
plt.show()

plt.scatter(z_mod, cor_mod, s=m_size, label='cor')
plt.scatter(z_mod, y_obs, s=m_size, label='cor')
plt.show()

fileout_dat = open('dataset_dat.dat', 'w')
fileout_anc = open('dataset_anc.dat', 'w')

fileout_dat.write('# time flux flux_err jitter offset subset \n')
fileout_anc.write('# time flux flux_err jitter offset subset \n')

for b, v, a in zip (x_obs, y_obs, z_mod):
    fileout_dat.write('{0:12f} {1:12f} 1.00 0  0 -1 \n'.format(b,v))
    fileout_anc.write('{0:12f} {1:12f} 1.00 0  0 -1 \n'.format(b,a))
fileout_dat.close()
fileout_anc.close()
