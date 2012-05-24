import subprocess
import os

GHOSTSCRIPT = 'gs'
MOGRIFY = 'mogrify'

def _run_program(program, *args):
    args = [program] + list(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError('"{}" failed: {}'.format(args.join(' '), stdout))
    else:
        return stdout

def to_png(pdf, png, resolution=96, oversampling=4):
    assert(os.path.exists(pdf))
    _run_program(
        GHOSTSCRIPT,
        '-q',
        '-dSAFER',
        '-dBATCH',
        '-dNOPAUSE',
        '-sDEVICE=pngalpha',
        '-r{}'.format(resolution * oversampling),
        '-dTextAlphaBits=4',
        '-dGraphicsAlphaBits=4',
        '-sOutputFile={}'.format(png),
        pdf,
    )
    assert(os.path.exists(png))
    if oversampling != 1:
        _run_program(
            MOGRIFY,
            '-resize', '{:.0%}'.format(1.0 / oversampling),       
            png
        )
    

import sys
pdf, png = sys.argv[1:]
to_png(pdf, png)
