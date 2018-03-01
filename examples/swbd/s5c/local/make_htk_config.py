#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Make configuration file for HTK toolkit (Switchboard corpus)."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os.path import join, basename
import sys
import argparse
import subprocess

sys.path.append('../../../')
from utils.feature_extraction.htk import save_config

parser = argparse.ArgumentParser()
parser.add_argument('--data_save_path', type=str, help='path to save data')
parser.add_argument('--htk_save_path', type=str, help='path to save HTK files')
parser.add_argument('--config_save_path', type=str,
                    help='path to save the configuration file')

parser.add_argument('--channels', type=int,
                    help='the number of frequency channels')
parser.add_argument('--window', type=float, default=0.025,
                    help='window width to extract features')
parser.add_argument('--slide', type=float, default=0.01,
                    help='extract features per slide')
parser.add_argument('--energy', type=int, help='if 1, add the energy feature')
parser.add_argument('--delta', type=int, help='if 1, add the energy feature')
parser.add_argument('--deltadelta', type=int,
                    help='if 1, double delta features are also extracted')


def main():

    args = parser.parse_args()

    # HTK settings
    save_config(audio_file_type='wav',
                feature_type='fbank',
                channels=args.channels,
                config_save_path=args.config_save_path,
                sampling_rate=8000,
                window=args.window,
                slide=args.slide,
                energy=bool(args.energy),
                delta=bool(args.delta),
                deltadelta=bool(args.deltadelta))

    for data_type in ['train', 'dev', 'eval2000']:
        wav_paths = []
        with open(join(args.data_save_path, data_type, 'wav.scp')) as f:
            for line in f:
                line = line.strip()
                wav_path = line.split(' ')[7]
                wav_paths.append(wav_path)

                # Split per channel
                # result_A = subprocess.call(
                #     ['$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe', '-f', 'wav', '-p', '-c', '1',
                #      join(args.data_save_path, 'wav', data_type, basename(wav_path).split('.')[0] + '-A.wav')])
                # result_B = subprocess.call(
                #     ['$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe', '-f', 'wav', '-p', '-c', '2',
                #      join(args.data_save_path, 'wav', data_type, basename(wav_path).split('.')[0] + '-B.wav')])
                #
                # if result_A != 0 or result_B != 0:
                #     raise ValueError

        with open(join(args.data_save_path, data_type, 'wav2htk.scp'), 'w') as f:
            for wav_path in wav_paths:
                f.write(wav_path + '  ' + join(args.data_save_path, 'htk', data_type,
                                               basename(wav_path).replace('.wav', '.htk')) + '\n')


if __name__ == '__main__':
    main()
