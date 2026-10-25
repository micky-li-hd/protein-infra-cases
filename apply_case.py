"""Apply one case to a clean checkout of the exact upstream commit."""
import argparse
from pathlib import Path
import subprocess

CASES = {
    'proteinmpnn-training': '8907e6671bfbfc92303b5f79c4b5e6ce47cdef57',
    'proteinmpnn-inference': '8907e6671bfbfc92303b5f79c4b5e6ce47cdef57',
    'rfdiffusion-inference': '86507b6538f51fce57b5a72477165f03999ed7ae',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=CASES)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    checkout = args.checkout.resolve(strict=True)

    def git(*parts):
        return subprocess.check_output(['git', '-C', str(checkout), *parts], text=True).strip()

    if git('rev-parse', 'HEAD') != CASES[args.case]:
        parser.error('Checkout does not match the pinned upstream commit.')
    if git('status', '--porcelain', '--untracked-files=normal'):
        parser.error('Use a clean, separate checkout; existing files will not be overwritten.')
    patch = Path(__file__).resolve().parent / (args.case + '.patch')
    git('apply', '--check', str(patch))
    if args.check_only:
        print('Patch applies. No files changed.')
    else:
        git('apply', str(patch))
        print('Applied', args.case, 'to', checkout)
        print('This applies source changes only; it does not verify runtime compatibility or speedup.')


if __name__ == '__main__':
    main()
