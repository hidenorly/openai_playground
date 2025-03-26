#   Copyright 2024, 2025 hidenorly
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
import requests
import select
import base64
import mimetypes
import io
from PIL import Image

class OpenAICompatibleLLM:
    def __init__(self, api_key, endpoint, is_streaming):
        self.api_key = api_key
        self.endpoint = endpoint
        self.is_streaming = is_streaming

    def _create_header_and_payload(self, messages, model=None):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        payload = {
            "messages": messages,
        }
        if model:
            payload["model"] = model
        return headers, payload

    def create_chat_completion(self, messages, model=None):
        headers, payload  = self._create_header_and_payload(messages, model)

        if "/api/chat" in self.endpoint or self.is_streaming:
            # streaming mode (ollama mode)
            payload["stream"] = True
            
            r = requests.post(self.endpoint, headers=headers, json=payload, stream=True)
            r.raise_for_status()
            output = ""
            for line in r.iter_lines():
                body = json.loads(line)
                if "error" in body:
                    raise Exception(body["error"])
                if body.get("done") is False:
                    message = body.get("message", "")
                    content = message.get("content", "")
                    output += content

                if body.get("done", False):
                    message = body
                    message["content"] = output
                    return output, message

        else:
            # non-streaming mode
            response = requests.post(self.endpoint, headers=headers, json=payload)
            if response.status_code == 200:
                response_json = response.json()
                main_message = response_json['choices'][0]['message']['content']
                return main_message, response_json
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")

        return None, None

def files_reader(files):
    result = ""
    for path in files:
        if os.path.exists(path):
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


def get_file_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("text/") or mime_type in ["application/json", "application/csv", "application/xml"]:
            return "text"
    return "file"

def get_base64_and_ext_body_or_shrinked_image(file_path, max_size):
    result = None
    ext = os.path.splitext(file_path)[-1][1:].upper() # ext

    image = None
    buf = None

    try:
        image = Image.open(file_path)
    except:
        pass

    if image:
        w1, h1 = image.size
        if max(w1, h1) > max_size:
            if w1 > h1:
                w2 = max_size
                h2 = int(h1 * (max_size / w1))
            else:
                w2 = int(w1 * (max_size / h1))
                h2 = max_size
            image = image.resize((w2, h2), resample=Image.LANCZOS)
        buf = io.BytesIO()
        image.save(buf, format=ext)
        result = base64.b64encode(buf.getvalue()).decode("utf-8")
    else:
        with open(file_path, "rb") as file:
            result = base64.b64encode(file.read()).decode("utf-8")

    return result, ext


def get_message_for_attachments(user_prompt, file_paths, max_size=320):
    result = {
        "role": "user"
    }
    body_images = []
    body_files = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            file_type = get_file_type(file_path)
            base64_data, ext = get_base64_and_ext_body_or_shrinked_image(file_path, max_size)
            if file_type == "image":
                body_images.append(base64_data)
            else:
                body_files.append(base64_data)

#        result = {
#            "role": "user",
#            "content": {
#                "type": file_type,
#                "data": base64_data,
#                "name": os.path.basename(file_path),
#                "format": ext.lower()
#            }

    if user_prompt:
        result["content"] = user_prompt
    if body_images:
        result["images"] = body_images
    if body_files:
        pass
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='General LLM client for OpenAI compatible web API')
    parser.add_argument('args', nargs='*', help='files')
    parser.add_argument('-k', '--apikey', action='store', default=os.getenv("LLM_API_KEY"), help='specify your API key or set it in LLM_API_KEY env')
    parser.add_argument('-e', '--endpoint', action='store', default=os.getenv("LLM_ENDPOINT"), help='specify your end point (e.g. http://localhost:8080/v1/chat/completions ) or set it in LLM_ENDPOINT env')
    parser.add_argument('-d', '--deployment', action='store', default=os.getenv("LLM_DEPLOYMENT_NAME"), help='optional. specify deployment name(model) or set it in LLM_DEPLOYMENT_NAME env')
    parser.add_argument('-s', '--systemprompt', action='store', default=None, help='specify system prompt if necessary')
    parser.add_argument('-u', '--prompt', action='store', default=None, help='specify prompt')
    parser.add_argument('-p', '--promptfile', action='store', default=None, help='specify prompt.json')
    parser.add_argument('-o', '--stream', action='store_true', default=False, help='specify if streaming mode is necessary (e.g. ollam)')
    parser.add_argument('-a', '--attach', action='append', default=[], help='Attachment files such as hoge.jpg')
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

    user_prompt = user_prompt + "\n" + additional_prompt

    service = OpenAICompatibleLLM(api_key=args.apikey, endpoint=args.endpoint, is_streaming=args.stream)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if args.attach:
        attachments = []
        for an_attach in args.attach:
            an_attach = os.path.expanduser(an_attach)
            if os.path.exists(an_attach):
                attachments.append(an_attach)
        if attachments:
            messages.append(get_message_for_attachments(user_prompt, attachments))
    elif user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    try:
        response_content, response = service.create_chat_completion(messages=messages, model=args.deployment)
        print(response_content)
        if response and args.verbose:
            print("")
            if "id" in response:
                print(f'id: {response["id"]}')
            if "model" in response:
                print(f'model: {response["model"]}')
            if "usage" in response:
                usage = response["usage"]
                if "prompt_tokens" in usage:
                    print(f'prompt_tokens: {usage["prompt_tokens"]}')
                if "completion_tokens" in usage:
                    print(f'completion_tokens: {usage["completion_tokens"]}')
                if "total_tokens" in usage:
                    print(f'total_tokens: {usage["total_tokens"]}')
    except Exception as e:
        print(e)
