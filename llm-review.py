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
from openai import AzureOpenAI

def files_reader(files):
    result = ""

    for path in files:
        if os.path.exists( path ):
          with open(path, 'r', encoding='UTF-8') as f:
            result += f.read()
            f.close()

    return result

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Code review specified file with OpenAI LLM')
    parser.add_argument('args', nargs='*', help='files')
    parser.add_argument('-k', '--apikey', action='store', default=os.getenv("AZURE_OPENAI_API_KEY"), help='specify your API key or set it in AZURE_OPENAI_API_KEY env')
    parser.add_argument('-e', '--endpoint', action='store', default=os.getenv("AZURE_OPENAI_ENDPOINT"), help='specify your end point or set it in AZURE_OPENAI_ENDPOINT env')
    parser.add_argument('-d', '--deployment', action='store', default=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), help='specify deployment name or set it in AZURE_OPENAI_DEPLOYMENT_NAME env')
    args = parser.parse_args()

    codes = ""
    if len(args.args)>0:
        codes = files_reader(args.args)
    else:
        codes = sys.stdin.read()

    client = AzureOpenAI(
      api_key = args.apikey,  
      api_version = "2024-02-01",
      azure_endpoint = args.endpoint
    )
    response = client.chat.completions.create(
        model= args.deployment, #"gpt-35-turbo-instruct", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "You're the world class best programmer and you're doing pair programming. You're requeted to code-review. You need pointed out what's problem, the potential risk and the future expansion. And you need to explain how to solve with expected examples. Example code is expected as diff output manner as -:original code +:modified code"},
            {"role": "user", "content": "Please review the following code and please explain the problem and please show the better code about the problematic part.\n"+codes}
        ]
    )

    #print(response)
    #print(response.model_dump_json(indent=2))
    print(response.choices[0].message.content)