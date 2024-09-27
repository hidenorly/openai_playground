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
from GptHelper import GptClientFactory, IGpt

class SimpleGptClient:
    def __init__(self, client=None, promptfile=None):
        self.client = client
        self.system_prompt = ""
        self.user_prompt = ""
        if promptfile:
            self.system_prompt, self.user_prompt = IGpt.read_prompt_json(promptfile)

    def _query(self, system_prompt, user_prompt):
        content = None
        response = None

        if self.client and user_prompt:
            content, response = self.client.query(system_prompt, user_prompt)
            return content, response

        return None, None

    def query(self, additional_prompt=None):
        content = None
        response = None

        system_prompt = self.system_prompt
        user_prompt = self.user_prompt
        if additional_prompt:
        	user_prompt += additional_prompt

        print(user_prompt)

        retry_count = 0
        while retry_count<3:
            # 1st level
            content, response = self._query(system_prompt, user_prompt)
            retry_count += 1
            if content:
                break
            else:
                print(f"ERROR!!!: LLM didn't expected anser. Retry:{retry_count}")
                print(content)

        return content, response

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='multi gpt client')
    parser.add_argument('args', nargs='*', help='files')

    parser.add_argument('-c', '--useclaude', action='store_true', default=False, help='specify if you want to use calude3')
    parser.add_argument('-g', '--gpt', action='store', default="openai", help='specify openai or calude3 or openaicompatible')

    parser.add_argument('-k', '--apikey', action='store', default=None, help='specify your API key or set it in AZURE_OPENAI_API_KEY env')
    parser.add_argument('-y', '--secretkey', action='store', default=os.getenv("AWS_SECRET_ACCESS_KEY"), help='specify your secret key or set it in AWS_SECRET_ACCESS_KEY env (for claude3)')
    parser.add_argument('-e', '--endpoint', action='store', default=None, help='specify your end point or set it in AZURE_OPENAI_ENDPOINT env')
    parser.add_argument('-d', '--deployment', action='store', default=None, help='specify deployment name or set it in AZURE_OPENAI_DEPLOYMENT_NAME env or model(s with ,)')
    parser.add_argument('-p', '--promptfile', action='store', default=None, help='specify prompt.json')

    parser.add_argument('-s', '--systemprompt', action='store', default=None, help='specify system prompt if necessary')
    parser.add_argument('-u', '--prompt', action='store', default=None, help='specify prompt')
    parser.add_argument('-H', '--header', action='append', default=[], help='Specify headers for http e.g. header_key:value (multiple --header are ok)')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='enable verbose')

    args = parser.parse_args()

    client = GptClientFactory.new_client(args)
    gpt_client = SimpleGptClient(client, args.promptfile)

    additional_prompt = ""
    if len(args.args) > 0:
        additional_prompt = IGpt.files_reader(args.args)
    else:
        if select.select([sys.stdin], [], [], 0.0)[0]:
            additional_prompt = sys.stdin.read()

    if args.systemprompt is not None:
    	gpt_client.system_prompt = str(args.systemprompt)

    if args.prompt is not None:
        gpt_client.user_prompt = str(args.prompt)


    contents, responses = gpt_client.query(additional_prompt)
    if not isinstance(contents, list):
        contents = [contents]
    for content in contents:
        print(content)

    if responses and args.verbose:
        if not isinstance(responses, list):
            responses = [responses]
        for response in responses:
            print("")
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


