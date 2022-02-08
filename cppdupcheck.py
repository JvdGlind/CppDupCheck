#!/usr/bin/env python3

import argparse
import hashlib
import sys


from pathlib import Path

database = {}
codeBlockSize = 6


def addToDatabase(codeBlockHash, filePath, line):
    if type(codeBlockHash) != str:
        raise Exception()

    if codeBlockHash not in database:
        database[codeBlockHash] = []

    database[codeBlockHash].append({"path": filePath, "line": line})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Check if a directory contains duplicate code, found in the files listed in the inputlist.')
    parser.add_argument('-d', '--directory', help='path to the directory containing files', required=True)

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.is_dir():
        print("Invalid directory")
        sys.exit(-1)

    for file_path in directory.glob("*.cpp"):
        with open(file_path) as input_file:

            try:
                lines = [x.replace(' ', '') for x in input_file.readlines()]
            except UnicodeDecodeError:
                print(f"Failed to read {file_path}", file=sys.stderr)
                continue

            if len(lines) < codeBlockSize:
                continue

            for index in range(0, len(lines)-codeBlockSize):
                if lines[index] == '\n':
                    continue

                hash_object = hashlib.sha256(bytes(''.join(lines[index:index+codeBlockSize-1]), 'utf-8'))

                addToDatabase(hash_object.hexdigest(), file_path, index)

    for sha_hash in database:
        if len(database[sha_hash]) > 1:
            print(database[sha_hash])
