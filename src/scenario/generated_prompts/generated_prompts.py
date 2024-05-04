import os
import datetime
from glob import glob
from pathlib import Path
from threading import Thread
from textwrap import dedent
from pyrit.common import default_values
from pyrit.memory import DuckDBMemory
from pyrit.memory.memory_interface import MemoryInterface
from pyrit.models import PromptTemplate
from pyrit.orchestrator import EndTokenRedTeamingOrchestrator
from pyrit.prompt_target import AzureOpenAIChatTarget, AzureMLChatTarget

default_values.load_default_env()

DATABASE_NAME = os.environ.get("DATABASE_NAME")
MAX_TURN = int(os.environ.get("MAX_CONVERSATION_TURN"))


def perform_red_teaming(
    prompt: str,
    red_teaming_llm: AzureOpenAIChatTarget | AzureMLChatTarget,
    memory: MemoryInterface = None,
):
    attack_strategy = dedent(prompt)

    target_llm = AzureOpenAIChatTarget(
        deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        endpoint=os.environ.get("AZURE_OPENAI_CHAT_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_CHAT_KEY"),
    )

    start = datetime.datetime.now()

    try:
        with EndTokenRedTeamingOrchestrator(
            attack_strategy=attack_strategy,
            red_teaming_chat=red_teaming_llm,
            prompt_target=target_llm,
            initial_red_teaming_prompt="Begin conversation",
            end_token="<|pwned|>",
            memory=memory,
            verbose=True,
        ) as red_teaming_orchestrator:
            red_teaming_orchestrator.apply_attack_strategy_until_completion(max_turns=MAX_TURN)
    except Exception as e:
        print(f"Error: {e}")

    end = datetime.datetime.now()
    print(f"Time taken: {end - start}")


def get_red_teaming_llms():
    return [
        AzureOpenAIChatTarget(
            deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            endpoint=os.environ.get("AZURE_OPENAI_CHAT_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_CHAT_KEY"),
        ),
        # AzureMLChatTarget(
        #     endpoint_uri=os.environ.get("AZURE_ML_MANAGED_ENDPOINT"),
        #     api_key=os.environ.get("AZURE_ML_KEY"),
        #     chat_message_normalizer=GenericSystemSquash(),
        # ),
    ]


files = glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*.yaml"))

duckdb_memory = DuckDBMemory(db_path=f"results/{DATABASE_NAME}.db")

for file in files:
    prompt = PromptTemplate.from_yaml_file(Path(file))
    for red_teaming_llm in get_red_teaming_llms():
        print(f"Performing red teaming for: {prompt.name}")
        Thread(
            target=perform_red_teaming,
            args=(
                prompt.template,
                red_teaming_llm,
                duckdb_memory,
            ),
        ).start()
