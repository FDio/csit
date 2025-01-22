# Copyright (c) 2025 Cisco and/or its affiliates.
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

from copy import deepcopy
import logging
import os
import sys
from time import sleep

import google.generativeai as genai

#logging.basicConfig(level=logging.DEBUG)

model_name = "gemini-1.5-pro"

license_block = '''
# Copyright (c) 2025 Cisco and/or its affiliates.
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
'''.strip()

def load_messages():
    with open("g.msg.py", "r") as fin:
        exec(fin.read(), globals())
    for message in messages:
        message["parts"] = message["parts"].strip()
    return messages

def save_messages(messages):
    with open("g.msg.py", "w") as fout:
        fout.write(f"{license_block}\n\n")
        fout.write("messages = [\n")
        for message in messages:
            role = message["role"]
            content = message["parts"]
            fout.write(f"    {{\n")
            fout.write(f"        'role': '{role}',\n")
            fout.write(f"        'parts': '''\n{content}\n''',\n")
            fout.write(f"    }},\n")
        fout.write("]\n")

def main():
    messages = load_messages()
    with open("draft-ietf-bmwg-mlrsearch-09.md", "r") as fin:
        draft_content = fin.read()
    if messages[0]["role"] != "system":
        raise RuntimeError("System prompt neeed.")
    subst_messages = deepcopy(messages)
    subst_system = subst_messages[0]["parts"]
    subst_system = subst_system.replace("${draft}", draft_content)
    subst_messages[0]["parts"] = subst_system

    sleep(1)
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    model_info = genai.get_model(f"models/{model_name}")
    print(f"{model_info.input_token_limit=}")
    print(f"{model_info.output_token_limit=}")
    print()

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=subst_messages[0]["parts"],
    )
    chat = model.start_chat(history=subst_messages[1:-1])
    request = subst_messages[-1]["parts"]

    while True:
        stream_response = chat.send_message(
            request,
            stream=True,
            generation_config = genai.GenerationConfig(
                max_output_tokens=1000,
                temperature=0.0,
            )
        )

        assistant_response = ""
        for chunk in stream_response:
            text = chunk.text
            if not text:
                raise RuntimeError("Empty chunk?")
            assistant_response += text
            print(text, end="", flush=True)

        print(f"\n\n{stream_response.usage_metadata!r}")

        messages.append({"role": "model", "parts": assistant_response.strip()})
        save_messages(messages)

        user_input = input("\nYou: ")
        print("\n")
        messages.append({"role": "user", "parts": user_input.strip()})
        save_messages(messages)
        request = messages[-1]["parts"]
        sleep(1)

if __name__ == "__main__":
    main()
