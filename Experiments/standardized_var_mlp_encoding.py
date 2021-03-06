import torch
import numpy as np
import pandas as pd
import argparse
import os
from itertools import product
import pickle
import shutil
import sys

# Data modules
from Data.generate_synthetic import standardized_var_model
from Data.data_processing import format_ts_data, normalize

# Model modules
sys.path.append('../Model')
from mlp import ParallelMLPEncoding
from experiment_line import run_experiment

# Parse command line arguments
parser = argparse.ArgumentParser()

parser.add_argument('--lam', type = float, default = 0.1, help = 'lambda for weight decay')
parser.add_argument('--seed', type = int, default = 12345, help = 'seed')
parser.add_argument('--hidden', type = int, default = 10, help = 'hidden units')
parser.add_argument('--network_lag', type = int, default = 5, help = 'lag considered by MLP')
parser.add_argument('--penalty', type = str, default = 'hierarchical', help = 'penalty type')

parser.add_argument('--nepoch', type = int, default = 1000, help = 'number of training epochs')
parser.add_argument('--lr', type = float, default = 0.001, help = 'learning rate')
parser.add_argument('--weight_decay', type = float, default = 0.01, help = 'weight decay on outgoing weights')

parser.add_argument('--data_seed', type = int, default = -1, help = 'seed for data generation')
parser.add_argument('--sparsity', type = float, default = 0.3, help = 'sparsity of time series')
parser.add_argument('--p', type = int, default = 10, help = 'dimensionality of time series')
parser.add_argument('--T', type = int, default = 500, help = 'length of time series')
parser.add_argument('--lag', type = int, default = 1, help = 'lag in VAR model')
parser.add_argument('--sd', type = float, default = 2.0, help = 'standard deviation of noise')

parser.add_argument('--loss_check', type = int, default = 10, help = 'interval for checking loss')

args = parser.parse_args()

# Prepare filename
experiment_base = 'Standardized VAR MLP Encoding'
results_dir = 'Results/' + experiment_base

experiment_name = results_dir + '/expt'
experiment_name += '_nepoch=%d_lr=%e_wd=%e' % (args.nepoch, args.lr, args.weight_decay)
experiment_name += '_lam=%e_seed=%d_hidden=%d_networklag=%d_penalty=%s' % (args.lam, args.seed, args.hidden, args.network_lag, args.penalty)
experiment_name += '_spars=%e_p=%d_T=%d_lag=%d_dseed=%d_sd=%e.out' % (args.sparsity, args.p, args.T, args.lag, args.data_seed, args.sd)

# Create directory, if necessary
if not os.path.exists(results_dir):
     os.makedirs(results_dir)

# Verify that experiment doesn't exist
if os.path.isfile(experiment_name):
	print('Skipping experiment')
	sys.exit(0)

# Prepare data
if args.data_seed == -1:
	X, _, GC = standardized_var_model(args.sparsity, args.p, 5, args.sd, args.T, args.lag)
else:
	X, _, GC = standardized_var_model(args.sparsity, args.p, 5, args.sd, args.T, args.lag, seed = args.data_seed)
X = normalize(X)
X_train, Y_train, _, _ = format_ts_data(X, args.network_lag, validation = 0.0)

# Get model
if args.seed != 0:
	torch.manual_seed(args.seed)
model = ParallelMLPEncoding(Y_train.shape[1], Y_train.shape[1], args.network_lag, [args.hidden], args.lr, 'line', args.lam, args.penalty, nonlinearity = 'sigmoid', weight_decay = args.weight_decay)

# Run experiment
train_loss, train_objective, weights, pred = run_experiment(model, X_train, Y_train, args.nepoch, predictions = True, loss_check = args.loss_check, verbose = True)

# Format results
experiment_params = {
	'nepoch': args.nepoch,
	'lr': args.lr,
	'lam': args.lam,
	'seed': args.seed,
	'hidden': args.hidden,
	'network_lag': args.network_lag,
	'weight_decay': args.weight_decay,
	'penalty': args.penalty
}

data_params = {
	'sparsity': args.sparsity,
	'p': args.p,
	'T': args.T,
	'lag': args.lag,
	'data_seed': args.data_seed,
	'sd': args.sd,
	'GC_true': GC
}

best_results = {
	'train_objective': train_objective,
	'GC_est': [np.linalg.norm(np.reshape(w, newshape = (args.hidden * args.network_lag, args.p), order = 'F'), axis = 0) for w in weights],
	'weights': weights
}

results_dict = {
	'experiment_params': experiment_params,
	'data_params': data_params,
	'best_results': best_results
}

# Save results
with open(experiment_name, 'wb') as f:
	pickle.dump(results_dict, f)
