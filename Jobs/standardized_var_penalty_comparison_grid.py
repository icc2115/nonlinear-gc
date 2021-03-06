from itertools import product
import numpy as np
import time

dstamp = time.strftime('%Y%m%d')
tstamp = time.strftime('%H%M%S')

jobname = 'standardized_var_penalty_comparison_%s_%s' % (dstamp, tstamp)
jobfile = 'Batches/%s.job' % jobname

lam_grid = np.append(np.geomspace(10.0, 0.001, num = 50), 0)
seed_grid = [0]
hidden_grid = [10]
network_lag_grid = [5, 10, 20]

nepoch_grid = [30000]
lr_grid = [0.01]
wd_grid = [0.01]
penalty_grid = ['group_lasso', 'hierarchical', 'stacked']

sparsity_grid = [0.3]
p_grid = [20]
T_grid = [750]
lag_grid = [2]
data_seed_grid = [0, 1, 2, 3, 4]

BASECMD = 'python standardized_var_mlp_encoding.py'

param_grid = product(penalty_grid,
	lam_grid, seed_grid, hidden_grid, network_lag_grid,
	nepoch_grid, lr_grid, wd_grid, 
	sparsity_grid, p_grid, T_grid, lag_grid, data_seed_grid)

with open(jobfile, 'w') as f:
	for param in param_grid:
		penalty, lam, seed, hidden, network_lag, nepoch, lr, wd, sparsity, p, T, lag, data_seed = param

		argstr = BASECMD

		argstr += ' --lam=%e' % lam
		argstr += ' --seed=%d' % seed
		argstr += ' --hidden=%d' % hidden
		argstr += ' --network_lag=%d' % network_lag

		argstr += ' --nepoch=%d' % nepoch
		argstr += ' --lr=%e' % lr
		argstr += ' --weight_decay=%e' % wd
		argstr += ' --penalty=%s' % penalty
		
		argstr += ' --sparsity=%e' % sparsity
		argstr += ' --p=%d' % p
		argstr += ' --T=%d' % T
		argstr += ' --lag=%d' % lag
		argstr += ' --data_seed=%d' % data_seed

		f.write(argstr + '\n')
