#!/usr/bin/env python3

import argparse
import hashlib
import json
import sys

from itertools import chain

from pathlib import Path

database = {}
codeBlockSize = 6


def findEndOfHeaderComment(lines):
    if '/*' not in lines[0]:
        return 0

    index = 1

    while index < len(lines):
        if '*/' in lines[index]:
            return index + 1

        index += 1

    raise Exception("No end of copyright found")


def addToDatabase(codeBlockHash, filePath, line):
    if type(codeBlockHash) != str:
        raise Exception()

    if codeBlockHash not in database:
        database[codeBlockHash] = []

    database[codeBlockHash].append({"path": str(filePath), "line": line})


def getAllFilesAsGenerator(directory):
    return chain(directory.glob("**/*.h"),
                 directory.glob("**/*.hpp"),
                 directory.glob("**/*.c"),
                 directory.glob("**/*.cpp"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Check if a directory contains duplicate code, found in the files listed in the inputlist.')
    parser.add_argument('-d', '--directory', help='path to the directory containing files', required=True)
    parser.add_argument('-o', '--output', help='file to write the output to')

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.is_dir():
        print("Invalid directory")
        sys.exit(-1)

    for file_path in getAllFilesAsGenerator(directory):
        with open(file_path) as input_file:
            try:
                lines = [x.replace(' ', '') for x in input_file.readlines()]
            except UnicodeDecodeError:
                print(f"Failed to read {file_path}", file=sys.stderr)
                continue

            if len(lines) < codeBlockSize:
                continue

            code_start_index = findEndOfHeaderComment(lines)

            for index in range(code_start_index, len(lines)-codeBlockSize):
                if lines[index] == '\n':
                    continue

                hash_object = hashlib.sha256(bytes(''.join(lines[index:index+codeBlockSize]), 'utf-8'))

                addToDatabase(hash_object.hexdigest(), file_path, index)

    violations = [database[x] for x in database if len(database[x]) > 1]

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write(json.dumps(violations, indent=4))
    else:
        for violation in violations:
            print(f"Duplicate code found in {len(violation)} files:")
            for file_meta in violation:
                print(f"\t {file_meta['path']} from line {file_meta['line']}")
