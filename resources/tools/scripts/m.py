# Copyright (c) 2024 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys
from time import sleep

from mistralai import Mistral
from prompt_toolkit import prompt as input

api_key = os.environ["MISTRAL_API_KEY"]
model = "codestral-mamba-latest"
model = "mistral-large-latest"

#logging.basicConfig(level=logging.DEBUG)

client = Mistral(api_key=api_key)

#mod_list = client.models.list().data
#for mod in mod_list:
#    print(f"{mod.id}")
#    if mod.id == model:
#        print(f"{mod!r}")
#sys.exit(1)

def load_messages():
    with open("m.msg.py", "r") as fin:
        exec(fin.read(), globals())
    for message in messages:
        message["content"] = message["content"].strip()
    return messages

def save_messages(messages):
    with open("m.msg.py", "w") as fout:
        fout.write("messages = [\n")
        for message in messages:
            role = message["role"]
            content = message["content"]
            fout.write(f"    {{\n")
            fout.write(f"        'role': '{role}',\n")
            fout.write(f"        'content': '''\n{content}\n''',\n")
            fout.write(f"    }},\n")
        fout.write("]\n")

def main():
    messages = load_messages()

    while True:
        sleep(1)
        stream_response = client.chat.stream(
            model=model,
            messages=messages,
            temperature=0.0,
            safe_prompt=False,
            max_tokens=5000,
        )

        assistant_response = ""
        for chunk in stream_response:
            content = chunk.data.choices[0].delta.content
            if content:
                assistant_response += content
                print(content, end="", flush=True)

        print(f"\n\n{chunk.data.choices[0].finish_reason!r}")
        print(f"{chunk.data.usage!r}")

        messages.append({"role": "assistant", "content": assistant_response.strip()})
        save_messages(messages)

        user_input = input("\nYou: ")
        print("\n")
        messages.append({"role": "user", "content": user_input.strip()})
        save_messages(messages)

if __name__ == "__main__":
    main()
