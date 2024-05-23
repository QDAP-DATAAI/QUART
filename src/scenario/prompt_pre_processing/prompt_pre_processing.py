import http.client
import json
import os
import re
from dataclasses import dataclass, field
from glob import glob
from pathlib import Path
from pyrit.common import default_values
from pyrit.memory import DuckDBMemory
from pyrit.models import PromptTemplate, PromptRequestPiece
from pyrit.prompt_target import AzureOpenAIChatTarget
from pyrit.score import SelfAskGptClassifier, ContentClassifiers


@dataclass
class PreProcessingPromptTemplate(PromptTemplate):
    pre_process_parameters: list[str] = field(default_factory=list)
    pre_process_template: str = ""

    def apply_pre_process_parameters(self, **kwargs) -> str:
        """Builds a new prompts from the pre processing template.
        Args:
            **kwargs: the key value for the pre processing template inputs

        Returns:
            A new prompt following the pre processing template
        """
        final_prompt = self.pre_process_template
        for key, value in kwargs.items():
            if key not in self.pre_process_parameters:
                raise ValueError(
                    f'Invalid parameters passed. [expected="{self.pre_process_parameters}", actual="{kwargs}"]'
                )
            # Matches field names within brackets {{ }}
            #  {{   key    }}
            #  ^^^^^^^^^^^^^^
            regex = "{}{}{}".format("\{\{ *", key, " *\}\}")  # noqa: W605
            matches = re.findall(pattern=regex, string=final_prompt)
            if not matches:
                raise ValueError(
                    f"No parameters matched, they might be missing in the pre processing template. "
                    f'[expected="{self.pre_process_parameters}", actual="{kwargs}"]'
                )
            final_prompt = re.sub(pattern=regex, string=final_prompt, repl=value)
        return final_prompt


class HttpChatTarget:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def send_messages(self, method: str, path: str, payload: dict, headers: dict) -> json:
        connection = http.client.HTTPSConnection(self.base_url)
        payload_bytes = json.dumps(payload).encode()
        connection.request(method, path, payload_bytes, headers)
        response = connection.getresponse() 
        return json.loads(response.read())


# 0. load prompt templates from yaml files
# 1. Send prompt to target chatbot
# 2. Run ethics classifier
# 3. Pre-process input'
# 4. Send pre-processed prompt to target chatbot and internal chatbot for comparison
# 5. Store results in memory

default_values.load_default_env()

DATABASE_NAME = os.environ.get("DATABASE_NAME")
MAX_TURN = int(os.environ.get("MAX_CONVERSATION_TURN"))

files = glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*.yaml"))

duckdb_memory = DuckDBMemory(db_path=f"results/{DATABASE_NAME}.db")

for file in files:
    prompt_template = PreProcessingPromptTemplate.from_yaml_file(Path(file))
    prompt = prompt_template.template
    target_chatbot = HttpChatTarget(base_url="api-dev.ai.qld.gov.au")
    responseTarget = target_chatbot.send_messages(
        method="POST",
        path="/desbt/openai/deployments/gpt-4-turbo/chat/completions?api-version=2024-02-01",
        payload={"messages": [{"role": "user", "content": prompt}]},
        headers={"Content-type": "application/json", "api-key": "16ccdd70cf8b469f9f6033fc911a887a"},
    )
    print(f"[{os.path.basename(file)}] - Response is given as:", responseTarget)
    duckdb_memory.add_request_response_to_memory(
        request=PromptRequestPiece(
            role="user_request",
            original_prompt_text=prompt,
        ).to_prompt_request_response(),
    )
    duckdb_memory.add_request_response_to_memory(
        request=PromptRequestPiece(
            role="user_response",
            original_prompt_text=responseTarget['choices'][0]['message']['content'],
        ).to_prompt_request_response(),
    )
    chat_llm = AzureOpenAIChatTarget(
        deployment_name=os.environ.get("AZURE_OPENAI_COMPLETION_DEPLOYMENT"),
        endpoint=os.environ.get("AZURE_OPENAI_COMPLETION_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_COMPLETION_KEY"),
        memory=duckdb_memory,
    )
    ethics_classifier = SelfAskGptClassifier(
        content_classifier=ContentClassifiers.REFUSAL_CLASSIFIER, chat_target=chat_llm
    )
    scored_response = ethics_classifier.score_text(text=prompt)
    print(f"[{os.path.basename(file)}] - Scored response is given as:", scored_response.score_value)

    prompt_to_pre_process = prompt_template.apply_pre_process_parameters(input=prompt)
    request = PromptRequestPiece(
        role="user",
        original_prompt_text=prompt_to_pre_process,
    ).to_prompt_request_response()
    responseChat = chat_llm.send_prompt(prompt_request=request)
    print(f"[{os.path.basename(file)}] - Pre processed prompt is given as:", responseChat)

    responseTarget = target_chatbot.send_messages(
        method="POST",
        path="/desbt/openai/deployments/gpt-4-turbo/chat/completions?api-version=2024-02-01",
        payload={"messages": [{"role": "user", "content": prompt_to_pre_process}]},
        headers={"Content-type": "application/json", "api-key": "16ccdd70cf8b469f9f6033fc911a887a"},
    )
    print(f"[{os.path.basename(file)}] - Pre processed response is given as:", responseTarget)
    duckdb_memory.add_request_response_to_memory(
        request=PromptRequestPiece(
            role="pre-proc-req",
            original_prompt_text=prompt_to_pre_process,
        ).to_prompt_request_response(),
    )
    duckdb_memory.add_request_response_to_memory(
        request=PromptRequestPiece(
            role="pre-proc-resp-chat",
            original_prompt_text=responseChat.request_pieces[0].original_prompt_text,
        ).to_prompt_request_response(),
    )
    duckdb_memory.add_request_response_to_memory(
        request=PromptRequestPiece(
            role="pre-proc-resp-target",
            original_prompt_text=responseTarget['choices'][0]['message']['content'],
        ).to_prompt_request_response(),
    )
