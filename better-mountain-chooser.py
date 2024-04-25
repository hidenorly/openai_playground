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

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Code review specified file with OpenAI LLM')
    parser.add_argument('-k', '--apikey', action='store', default=os.getenv("AZURE_OPENAI_API_KEY"), help='specify your API key or set it in AZURE_OPENAI_API_KEY env')
    parser.add_argument('-e', '--endpoint', action='store', default=os.getenv("AZURE_OPENAI_ENDPOINT"), help='specify your end point or set it in AZURE_OPENAI_ENDPOINT env')
    parser.add_argument('-d', '--deployment', action='store', default=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), help='specify deployment name or set it in AZURE_OPENAI_DEPLOYMENT_NAME env')
    args = parser.parse_args()

    info = sys.stdin.read()

    client = AzureOpenAI(
      api_key = args.apikey,  
      api_version = "2024-02-01",
      azure_endpoint = args.endpoint
    )
    response = client.chat.completions.create(
        model= args.deployment, #"gpt-35-turbo-instruct", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "You're the best experienced mountain tour guide. For customer's satisfaction, check the given info. you need to suggest the best mountains and the car park for the customer. considering points are shorter transport from the customer to the park, better review commented mountain in the given mountain records, smaller dangerousnes, better sceneic experience. You need to output several candidates of recommended mountains and explain what's the points of the recommendations. Output is in Japanese. Expect to output top 5 mountain candidates."},
            {"role": "user", "content": "Please suggest recommended mountains from given candidates and the related mountain records including impression.\n"+info}
        ]
    )

    #print(response)
    #print(response.model_dump_json(indent=2))
    print(response.choices[0].message.content)