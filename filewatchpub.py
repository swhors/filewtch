from file_dog_watch import run as run_dogwatch
from file_walk_watch import run as run_walkwatch
from parse_arg import parse_args


runner = {'dog':run_dogwatch, 'walk':run_walkwatch}

if __name__ == "__main__":
    mode, args = parse_args()

    if mode not in runner:
        print(f'Illegal mode: walk or dog')
    else:
        runner[mode](*args)
 
