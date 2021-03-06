from itertools import product
import numpy as np
import time

dstamp = time.strftime('%Y%m%d')
tstamp = time.strftime('%H%M%S')

jobname = 'lorentz_mlp_encoding_%s_%s' % (dstamp, tstamp)
jobfile = 'Batches/%s.job' % jobname

lam_grid = np.append(np.geomspace(1.0, 0.01, num = 50), 0)
seed_grid = [0]
hidden_grid = [10]
network_lag_grid = [5]

nepoch_grid = [30000]
lr_grid = [0.01]
wd_grid = [0.01]

FC_grid = [10, 40]
sd_grid = [2.0]
dt_grid = [0.05]
p_grid = [10, 20, 30]
T_grid = [500, 750, 1000]
data_seed_grid = [0, 1, 2, 3, 4]

BASECMD = 'python lorentz_mlp_encoding.py'

param_grid = product(lam_grid, seed_grid, hidden_grid, network_lag_grid,
	nepoch_grid, lr_grid, wd_grid,
	FC_grid, sd_grid, dt_grid, p_grid, T_grid, data_seed_grid)

with open(jobfile, 'w') as f:
	for param in param_grid:
		lam, seed, hidden, network_lag, nepoch, lr, wd, FC, sd, dt, p, T, data_seed = param

		argstr = BASECMD

		argstr += ' --lam=%e' % lam
		argstr += ' --seed=%d' % seed
		argstr += ' --hidden=%d' % hidden
		argstr += ' --network_lag=%d' % network_lag

		argstr += ' --nepoch=%d' % nepoch
		argstr += ' --lr=%e' % lr
		argstr += ' --weight_decay=%e' % wd

		argstr += ' --FC=%e' % FC
		argstr += ' --sd=%e' % sd
		argstr += ' --dt=%e' % dt
		argstr += ' --p=%d' % p
		argstr += ' --T=%d' % T
		argstr += ' --data_seed=%d' % data_seed

		f.write(argstr + '\n')