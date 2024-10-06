#!/usr/bin/env python3
import argparse
import random
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Python implementation of GNU shuf.")
    parser.add_argument('-e', '--echo', nargs='*', help='Treat each argument as an input line.')
    parser.add_argument('-i', '--input-range', help='Treat each number in the range LO-HI as an input line.')
    parser.add_argument('-n', '--head-count', type=int, help='Output at most COUNT lines.')
    parser.add_argument('-r', '--repeat', action='store_true', help='Repeat output values.')
    return parser.parse_args()

def process_input_range(range_arg):
    lo, hi = map(int, range_arg.split('-'))
    return list(map(str, range(lo, hi+1)))

def main():
    args = parse_args()

    # Handle input source
    if args.echo is not None:
        lines = args.echo
    elif args.input_range is not None:
        lines = process_input_range(args.input_range)
    else:
        lines = [line.strip() for line in sys.stdin]

    # Output handling with --repeat and --head-count
    count = 0
    while True:
        if args.repeat:
            # Randomly select from input lines for each output
            line = random.choice(lines)
        else:
            # Shuffle lines once if not repeating
            if count == 0:
                random.shuffle(lines)
            # Break out of the loop if all lines are processed
            if count >= len(lines):
                break
            line = lines[count]
        
        print(line)
        count += 1
        
        # Check head count limit
        if args.head_count is not None and count >= args.head_count:
            break

if __name__ == "__main__":
    main()
