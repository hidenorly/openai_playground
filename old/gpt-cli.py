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
import json
import select
from openai import AzureOpenAI

def files_reader(files):
    result = ""

    for path in files:
        if os.path.exists( path ):
          with open(path, 'r', encoding='UTF-8') as f:
            result += f.read()

    return result


def read_prompt_json(path):
    system_prompt = ""
    user_prompt = ""

    if path and os.path.isfile(path):
        with open(path, 'r', encoding='UTF-8') as f:
          result = json.load(f)
          if "system_prompt" in result:
            system_prompt = result["system_prompt"]
          if "user_prompt" in result:
            user_prompt = result["user_prompt"]

    return system_prompt, user_prompt

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Code review specified file with OpenAI LLM')
    parser.add_argument('args', nargs='*', help='files')
    parser.add_argument('-k', '--apikey', action='store', default=os.getenv("AZURE_OPENAI_API_KEY"), help='specify your API key or set it in AZURE_OPENAI_API_KEY env')
    parser.add_argument('-e', '--endpoint', action='store', default=os.getenv("AZURE_OPENAI_ENDPOINT"), help='specify your end point or set it in AZURE_OPENAI_ENDPOINT env')
    parser.add_argument('-d', '--deployment', action='store', default=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), help='specify deployment name or set it in AZURE_OPENAI_DEPLOYMENT_NAME env')
    parser.add_argument('-s', '--systemprompt', action='store', default=None, help='specify system prompt if necessary')
    parser.add_argument('-u', '--prompt', action='store', default=None, help='specify prompt')
    parser.add_argument('-p', '--promptfile', action='store', default=None, help='specify prompt.json')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='enable verbose')
    args = parser.parse_args()

    additional_prompt = ""
    if len(args.args) > 0:
        additional_prompt = files_reader(args.args)
    else:
        if select.select([sys.stdin], [], [], 0.0)[0]:
            additional_prompt = sys.stdin.read()

    system_prompt, user_prompt = read_prompt_json(args.promptfile)

    if args.systemprompt is not None:
        system_prompt = args.systemprompt

    if args.prompt is not None:
        user_prompt = str(args.prompt)

    user_prompt = user_prompt + "\n" +additional_prompt

    client = AzureOpenAI(
      api_key = args.apikey,  
      api_version = "2024-02-01",
      azure_endpoint = args.endpoint
    )

    _messages = []
    if system_prompt:
        _messages.append( {"role": "system", "content": system_prompt} )
    if user_prompt:
        _messages.append( {"role": "user", "content": user_prompt} )

    response = client.chat.completions.create(
        model= args.deployment, #"gpt-35-turbo-instruct", # model = "deployment_name".
        messages = _messages
    )

    print(response.choices[0].message.content)

    if response and args.verbose:
        print("")
        response = dict(response)
        if "id" in response:
            print(f'id: {response["id"]}')
        if "model" in response:
            print(f'model: {response["model"]}')
        if "usage" in response:
            usage = dict(response["usage"])
            if "prompt_tokens" in usage:
                print(f'prompt_tokens: {usage["prompt_tokens"]}')
            if "completion_tokens" in usage:
                print(f'completion_tokens: {usage["completion_tokens"]}')
            if "total_tokens" in usage:
                print(f'total_tokens: {usage["total_tokens"]}')
