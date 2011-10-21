"""A procedural wrapper for the antiword command-line application.
"""

import subprocess
import tempfile


def antiword_file(filename):
    '''Returns plain-text version of Word file.
    '''
    return (subprocess .check_output(['antiword', '-w', '0', filename])
            .decode('utf-8'))


def antiword_string(word_document_data):
    '''Returns plain-text version of Word document given as a string.
    '''

    with tempfile.NamedTemporaryFile() as doc_file:
        doc_file.write(word_document_data)
        doc_file.flush()
        return antiword_file(doc_file.name)
