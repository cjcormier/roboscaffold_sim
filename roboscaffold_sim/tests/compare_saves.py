import argparse

from roboscaffold_sim.simulators.load_save import compare_saves

parser = argparse.ArgumentParser(description='Basic simulation player.')
parser.add_argument('file_1', type=str, help='First file')
parser.add_argument('file_2', type=str, help='Second file')

if __name__ == '__main__':
    args = parser.parse_args()
    print(compare_saves(args.file_1, args.file_2))