#   Copyright 2024 hidenorly
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import os
import sys
import select

def read_files(file_paths):
    lines = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            lines.extend(f.read().splitlines())
    return lines

def code_section_extractor(lines):
    results = []
    start_pos = None
    for i in range(0, len(lines)):
        line = lines[i].strip()
        if start_pos==None and (line.startswith("```") or line.startswith("++ b/")):
            start_pos = i
        elif start_pos!=None and line.startswith("```"):
            results.append( lines[start_pos+1:i] )
            start_pos = None
    if not results:
        results = [lines]
    return results

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='code section extractor')
    parser.add_argument('args', nargs='*', help='files')
    args = parser.parse_args()

    lines = []
    if len(args.args) > 0:
        lines = read_files(args.args)
    else:
        while True:
            readable,_,_ = select.select([sys.stdin], [], [], 0.5)
            if readable:
                input_data = sys.stdin.read()
                if not input_data:
                    break
                lines.extend( input_data.splitlines() )

    code_sections = code_section_extractor(lines)
    for section in code_sections:
        for line in section:
            print(line)

