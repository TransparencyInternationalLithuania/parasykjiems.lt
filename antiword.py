"""A procedural wrapper for the antiword command-line application.
"""

import subprocess
import tempfile


def antiword_file(filename):
    '''Returns plain-text version of Word file.
    '''

    aw = subprocess.Popen(['antiword', '-w', '0', filename],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          # Force UTF-8 locale.
                          env={'LC_ALL': 'lt_LT.utf8'})

    out, err = aw.communicate()

    if aw.returncode == 0:
        return out.decode('utf-8')
    else:
        raise Exception('Failed to run antiword: {}'
                        .format(err))


def antiword_string(word_document_data):
    '''Returns plain-text version of Word document given as a string.
    '''

    with tempfile.NamedTemporaryFile() as doc_file:
        doc_file.write(word_document_data)
        doc_file.flush()
        return antiword_file(doc_file.name)
