import argparse

def str2tuple(tp=int):

    def convert(s):
        return tuple(tp(i) for i in s.split(','))
    return convert

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=0, help='random seed')
    parser.add_argument('--dataset', type=str, choices=['idda', 'femnist', 'gta5'], required=True, help='dataset name')
    parser.add_argument('--niid', action='store_true', default=False,  help='Run the experiment with the non-IID partition (IID by default). Only on FEMNIST dataset.')
    parser.add_argument('--model', type=str, choices=['deeplabv3_mobilenetv2', 'resnet18', 'cnn'], help='model name')
    parser.add_argument('--num_rounds', type=int, help='number of rounds')
    parser.add_argument('--num_epochs', type=int, help='number of local epochs')
    parser.add_argument('--clients_per_round', type=int, help='number of clients trained per round')
    parser.add_argument('--hnm', action='store_true', default=False, help='Use hard negative mining reduction or not')
    parser.add_argument('--lr', type=float, default=0.05, help='learning rate')
    parser.add_argument('--bs', type=int, default=4, help='batch size')
    parser.add_argument('--wd', type=float, default=0, help='weight decay')
    parser.add_argument('--m', type=float, default=0.9, help='momentum')
    parser.add_argument('--print_train_interval', type=int, default=10, help='client print train interval')
    parser.add_argument('--print_test_interval', type=int, default=10, help='client print test interval')
    parser.add_argument('--eval_interval', type=int, default=10, help='eval interval')
    parser.add_argument('--test_interval', type=int, default=10, help='test interval')
    # New Argument:
    parser.add_argument('--centr', action='store_true', default=False, help='Only one client will be used if set True')
    parser.add_argument('--opt', type=str, choices=['SGD', 'adam'], default = 'SGD', help='Optimizer choice')
    parser.add_argument('--sched', type=str, choices=['lin', 'step'], default = None, help='Scheduler choice')
    parser.add_argument('--n_images_per_style', type=int, default=1000, help='number of images to extract style (avg is performed)')
    parser.add_argument('--fda_L', type=float, default=0.01, help='to control size of amplitude window')
    parser.add_argument('--fda_b', type=int, default=None, help='if != None it is used instead of fda_L:' 'b == 0 --> 1x1, b == 1 --> 3x3, b == 2 --> 5x5, ...')
    parser.add_argument('--fda_size', type=str2tuple(int), default='1024,512', help='size (W,H) to which resize images before style transfer')
    return parser
