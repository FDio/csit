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

from google import genai
from google.genai import types

#logging.basicConfig(level=logging.DEBUG)

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
        message["text"] = message["text"].strip()
    return messages

def save_messages(messages):
    with open("g.msg.py", "w") as fout:
        fout.write(f"{license_block}\n\n")
        fout.write("messages = [\n")
        for message in messages:
            role = message["role"]
            content = message["text"]
            fout.write(f"    {{\n")
            fout.write(f"        'role': '{role}',\n")
            fout.write(f"        'text': '''\n{content}\n''',\n")
            fout.write(f"    }},\n")
        fout.write("]\n")

def main():
    api_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    #for m in client.models.list():
    #    for action in m.supported_actions:
    #        if action == "generateContent":
    #            print(m.name)
    #raise RuntimeError("Done.")

    # model_name = "gemini-2.5-pro-preview-05-06"
    # "Gemini 2.5 Pro Preview doesn't have a free quota tier."
    model_name = "gemini-2.5-flash-preview-05-20"
    model_name = "gemini-2.5-flash-preview-04-17-thinking"
    print(f"{model_name=}")
    sleep(1)

    messages = load_messages()
    with open("draft-ietf-bmwg-mlrsearch-11.md", "r") as fin:
        draft_content = fin.read()
    if messages[0]["role"] != "system":
        raise RuntimeError("System prompt neeed.")
    subst_messages = deepcopy(messages)
    subst_system = subst_messages[0]["text"]
    subst_system = subst_system.replace("${draft}", draft_content)
    subst_messages[0]["text"] = subst_system

    config = types.GenerateContentConfig(
        system_instruction=subst_messages[0]["text"],
        max_output_tokens=10000,
        temperature=0.0,
    )
    history = [
        types.Content(
            role=message["role"],
            parts=[types.Part.from_text(text=message["text"])]
        )
        for message in subst_messages[1:-1]
    ]
    request = subst_messages[-1]["text"]
    chat = client.chats.create(
        model=model_name,
        config=config,
        history=history,
    )
    #print(f"{chat=!r}")
    #print(f"{chat._config=!r}")

    while True:
        stream_response = chat.send_message_stream(message=request)

        assistant_response = ""
        for chunk in stream_response:
            text = chunk.text
            if not text:
                if not chunk.finish_reason:
                    raise RuntimeError(f"{chunk!r}")
                break
            assistant_response += text
            print(text, end="", flush=True)
        print(f"\n\n{chunk!r}\n")

        messages.append({"role": "model", "text": assistant_response.strip()})
        save_messages(messages)

        user_input = input("\nYou: ")
        print("\n")
        messages.append({"role": "user", "text": user_input.strip()})
        save_messages(messages)
        request = messages[-1]["text"]
        sleep(1)

if __name__ == "__main__":
    main()
