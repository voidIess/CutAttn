#!/usr/bin/env python
import argparse
import os

from experiments.tmux_launcher import Options

experiments = {
    2: Options(
        name="resnet_atn_02_continue_from_10",
        netG="resnet_atn",
        continue_train="",
    ),
    3: Options(
        name="resnet_atn_03_from_start_trans_at_16",
        netG="resnet_atn",
    ),
    4: Options(
        name="resnet_atn_04_start",
        netG="resnet_atn",
    ),
    5: Options(
        name="resnet_atn_05_from_5_trans_at_14",
        netG="resnet_atn",
        continue_train="",
        no_random_mask="",
    ),
    6: Options(
        name="resnet_atn_06_start_adain",
        netG="resnet_adain",
        no_random_mask="",
    ),
    7: Options(
        name="resnet_atn_07_from_05_adain",
        netG="resnet_adain",
        no_random_mask="",
        continue_train="",
    ),
    8: Options(
        name="resnet_atn_08_start_spectral_norm",
        netG="resnet_atn",
        netD="basic_spectral_norm",
    ),
    9: Options(
        name="resnet_atn_09_from_05_multiple_atn",
        netG="resnet_atn",
        continue_train="",
    ),
    10: Options(
        name="resnet_atn_10_from_05_spectral_norm",
        netG="resnet_atn",
        netD="basic_spectral_norm",
        continue_train="",
        ada_norm_layers="12",
    ),
    11: Options(
        name="resnet_atn_11_from_02_spectral_norm",
        netG="resnet_atn",
        netD="basic_spectral_norm",
        continue_train="",
        ada_norm_layers="12",
    ),
    12: Options(
        name="resnet_atn_12_start_multiple_atn_spectral_norm",
        netG="resnet_atn",
        netD="basic_spectral_norm",
        ada_norm_layers="12,13",
    ),
    13: Options(
        name="resnet_atn_13_from_02_adain",
        netG="resnet_adain",
        netD="basic",
        ada_norm_layers="12",
        continue_train="",
    ),
    14: Options(
        name="baseline_14_start_spectral_norm",
        netG="resnet_9blocks",
        netD="basic_spectral_norm",
    ),
    15: Options(
        name="resnet_atn_15_start_multiple_adain",
        netG="resnet_adain",
        netD="basic",
        ada_norm_layers="12,13,14",
    ),
    16: Options(
        name="resnet_atn_16_from_02_multiple_atn_spectral_norm",
        netG="resnet_atn",
        netD="basic_spectral_norm",
        ada_norm_layers="12,13",
        continue_train="",
        pretrained_name="baseline_14_start_spectral_norm",
        epoch=2,
    ),
}

experiments = {k: opt.set(dataroot="dataset") for k, opt in experiments.items()}

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='subcommand')

parser_train = subparsers.add_parser('train')
parser_train.add_argument('experiment_id', type=int)

parser_test = subparsers.add_parser('test')
parser_test.add_argument('experiment_id', type=int)
parser_test.add_argument('epoch', default='latest')
parser_test.add_argument("--num_test", type=int, default=50)

parser_list = subparsers.add_parser('list')

parser_eval = subparsers.add_parser('eval')
parser_eval.add_argument('experiment_id', type=int)
parser_eval.add_argument('epoch', default='latest')
parser_eval.add_argument('--batch_size', type=int, default=4)

parser.add_argument("--dry", action='store_true')

args = parser.parse_args()
for k, v in sorted(vars(args).items()):
    print(f"{k}: {v}")
if args.subcommand == "train":
    command = "python train.py " + str(experiments[args.experiment_id].set(n_epochs=15, n_epochs_decay=0))
    print(command)
    if not args.dry:
        os.system(command)
elif args.subcommand == "test":
    command = "python test.py " + str(experiments[args.experiment_id].set(epoch=args.epoch, num_test=args.num_test).remove('continue_train'))
    print(command)
    if not args.dry:
        os.system(command)
elif args.subcommand == "eval":
    print("Calculating metrics...")
    import eval_simple
    eval_simple.eval(experiments[args.experiment_id].kvs['name'], args)
elif args.subcommand == "list":
    for k, v in experiments.items():
        print(f"{k}: {v.kvs['name']}")
else:
    print("Please provide a command")
    parser.print_help()