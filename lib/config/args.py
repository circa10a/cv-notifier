'''
Create and parse arguments
'''
import argparse


def args():
    '''
    Create argument parser and parse
    '''
    parser = argparse.ArgumentParser(prog='cv-notifier', usage='main.py [options]', description='recognizes objects using YOLOv8 and calls configurable webhooks')
    parser.add_argument('--config', type=str, help='Path to configuration file', default='config.yaml',)
    return parser.parse_args()
