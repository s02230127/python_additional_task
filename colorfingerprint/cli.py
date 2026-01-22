import argparse, sys, subprocess
from .utils import *

def build_parser():
    p = argparse.ArgumentParser(prog="clrfp", description="Colorful SSH-fingerprint")
    p.add_argument('-f', '--file', default=sys.stdin, help='file to read from (default: stdin)')
    p.add_argument('-i', '--input', default='key', choices=('key', 'fingerprint'), help='fingerprint or key (default: key), key and stdin NOT AVAIBLE')
    p.add_argument('-d', '--digest', default='sha256', choices=('md5', 'sha256'), help='hash algorithm(default: sha256); ignored when -i fingerprint')
    p.add_argument('-c', '--color', choices=('foreground',  'background'), default='background', 
                   help='Coloring mode: foreground text or background fill (default: background).')
    return p


def main():
    argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input == 'key' and args.file == sys.stdin:
        print( "\033[31mERROR:\033[0m key and stdin NOT AVAIBLE, use key with file or stdin with fingerprint")
        exit(1)

    if args.input == 'key':
        try:
            cp = subprocess.run(['ssh-keygen', '-l', '-f', str(args.file), '-E', args.digest], capture_output=True, text=True)
            data = cp.stdout.strip()
            if cp.stderr != '':
                raise ValueError

        except FileNotFoundError:
            print( "\033[31mERROR:\033[0m File not found")
            exit(1)

        except ValueError:
            print( "\033[31mERROR:\033[0m Key not found in file")
            exit(1)
    
    if args.input == 'fingerprint':
        if args.file is sys.stdin:
            data = sys.stdin.read().strip()
        else:
            with open(args.file, 'r') as f:
                data = f.read().strip()
    try:
        fingerprint = parse_input(data)
    except ValueError:
        print( "\033[31mERROR:\033[0m fingerprint not found")
        exit(1)
    field = field_fill(fingerprint, 17, 9, 17)
    print(field_color(field, data, fingerprint, args.color))
    

if __name__ == '__main__':
    main()