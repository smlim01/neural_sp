#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Evaluate the trained hierarchical model (Switchboard corpus)."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os.path import join, abspath
import sys
import argparse

sys.path.append(abspath('../../../'))
from models.load_model import load
from examples.swbd.data.load_dataset_hierarchical import Dataset
from examples.swbd.metrics.cer import do_eval_cer
from examples.swbd.metrics.wer import do_eval_wer
from utils.config import load_config

parser = argparse.ArgumentParser()
parser.add_argument('--model_path', type=str,
                    help='path to the model to evaluate')
parser.add_argument('--epoch', type=int, default=-1,
                    help='the epoch to restore')
parser.add_argument('--beam_width', type=int, default=1,
                    help='beam_width (int, optional): beam width for beam search.' +
                    ' 1 disables beam search, which mean greedy decoding.')
parser.add_argument('--eval_batch_size', type=int, default=1,
                    help='the size of mini-batch in evaluation')
parser.add_argument('--max_decode_len', type=int, default=100,
                    help='the length of output sequences to stop prediction when EOS token have not been emitted')
parser.add_argument('--max_decode_len_sub', type=int, default=300,
                    help='the length of output sequences to stop prediction when EOS token have not been emitted')


def main():

    args = parser.parse_args()

    # Load a config file (.yml)
    params = load_config(join(args.model_path, 'config.yml'), is_eval=True)

    # Load dataset
    vocab_file_path = '../metrics/vocab_files/' + \
        params['label_type'] + '_' + params['data_size'] + '.txt'
    vocab_file_path_sub = '../metrics/vocab_files/' + \
        params['label_type_sub'] + '_' + params['data_size'] + '.txt'
    eval2000_swbd_data = Dataset(
        backend=params['backend'],
        input_channel=params['input_channel'],
        use_delta=params['use_delta'],
        use_double_delta=params['use_double_delta'],
        data_type='eval2000_swbd', data_size=params['data_size'],
        label_type=params['label_type'], label_type_sub=params['label_type_sub'],
        vocab_file_path=vocab_file_path,
        vocab_file_path_sub=vocab_file_path_sub,
        batch_size=args.eval_batch_size, splice=params['splice'],
        num_stack=params['num_stack'], num_skip=params['num_skip'],
        sort_utt=False, save_format=params['save_format'])
    eval2000_ch_data = Dataset(
        backend=params['backend'],
        input_channel=params['input_channel'],
        use_delta=params['use_delta'],
        use_double_delta=params['use_double_delta'],
        data_type='eval2000_ch',  data_size=params['data_size'],
        label_type=params['label_type'], label_type_sub=params['label_type_sub'],
        vocab_file_path=vocab_file_path,
        vocab_file_path_sub=vocab_file_path_sub,
        batch_size=args.eval_batch_size, splice=params['splice'],
        num_stack=params['num_stack'], num_skip=params['num_skip'],
        sort_utt=False, save_format=params['save_format'])
    params['num_classes'] = eval2000_swbd_data.num_classes
    params['num_classes_sub'] = eval2000_swbd_data.num_classes_sub

    # Load model
    model = load(model_type=params['model_type'],
                 params=params,
                 backend=params['backend'])

    # Restore the saved parameters
    model.load_checkpoint(save_path=args.model_path, epoch=args.epoch)

    # GPU setting
    model.set_cuda(deterministic=False, benchmark=True)

    wer_eval2000_swbd = do_eval_wer(
        model=model,
        dataset=eval2000_swbd_data,
        beam_width=args.beam_width,
        max_decode_len=args.max_decode_len,
        eval_batch_size=args.eval_batch_size,
        progressbar=True)
    print('  WER (SWB, main): %f %%' % (wer_eval2000_swbd * 100))
    wer_eval2000_ch = do_eval_wer(
        model=model,
        dataset=eval2000_ch_data,
        beam_width=args.beam_width,
        max_decode_len=args.max_decode_len,
        eval_batch_size=args.eval_batch_size,
        progressbar=True)
    print('  WER (CHE, main): %f %%' % (wer_eval2000_ch * 100))
    print('  WER (mean, main): %f %%' %
          ((wer_eval2000_swbd + wer_eval2000_ch) * 100 / 2))

    cer_eval2000_swbd, _ = do_eval_cer(
        model=model,
        dataset=eval2000_swbd_data,
        beam_width=args.beam_width,
        max_decode_len=args.max_decode_len_sub,
        eval_batch_size=args.eval_batch_size,
        progressbar=True)
    print('  CER (SWB, sub): %f %%' % (cer_eval2000_swbd * 100))
    cer_eval2000_ch, _ = do_eval_cer(
        model=model,
        dataset=eval2000_ch_data,
        beam_width=args.beam_width,
        max_decode_len=args.max_decode_len_sub,
        eval_batch_size=args.eval_batch_size,
        progressbar=True)
    print('  CER (CHE, sub): %f %%' % (cer_eval2000_ch * 100))
    print('  CER (mean, sub): %f %%' %
          ((cer_eval2000_swbd + cer_eval2000_ch) * 100 / 2))


if __name__ == '__main__':
    main()
