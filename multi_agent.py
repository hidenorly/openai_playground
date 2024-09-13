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

from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_version="2023-05-15",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_completion(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

class Agent:
    def __init__(self, role, description):
        self.role = role
        self.description = description
        self.memory = []

    def act(self, task):
        messages = [
            {"role": "system", "content": f"You are a {self.role}. {self.description}"},
            {"role": "user", "content": task}
        ] + self.memory
        response = get_completion(messages)
        self.memory.append({"role": "assistant", "content": response})
        return response

def orchestrator(goal, agents):
    overall_memory = []
    
    while True:
        messages = [
            {"role": "system", "content": "You are an orchestrator. Your job is to coordinate multiple AI agents to achieve a goal."},
            {"role": "user", "content": f"Goal: {goal}\n\nAvailable agents: {', '.join([agent.role for agent in agents])}\n\nDecide the next step and which agent should perform it. If the goal is achieved, respond with 'GOAL ACHIEVED'."}
        ] + overall_memory

        decision = get_completion(messages)
        
        if "GOAL ACHIEVED" in decision:
            print("Goal achieved!")
            break

        for agent in agents:
            if agent.role.lower() in decision.lower():
                result = agent.act(decision)
                overall_memory.append({"role": "assistant", "content": f"{agent.role}: {result}"})
                print(f"{agent.role}: {result}")
                break

if __name__=="__main__":
    researcher = Agent("Researcher", "You research and provide factual information.")
    writer = Agent("Writer", "You write creative and engaging content.")
    critic = Agent("Critic", "You provide constructive criticism and suggestions for improvement.")

    agents = [researcher, writer, critic]

    goal = "Write a short blog post about the benefits of AI in healthcare"
    orchestrator(goal, agents)