import sys
from pathlib import Path
from typing import Optional

import yaml

self_exe = Path(sys.argv[0]).resolve()
self_dir = self_exe.parent


def is_debug() -> bool:
    """
    检查当前是否为调试模式
    :return: bool
    """
    # 编译后.py文件会与python解释器一起打包进依赖
    if any("dll" in str(p) for p in Path(__file__).parent.iterdir()):
        return False
    else:
        print(f"Debug environment detected: {self_dir}")
        print(f"{list(self_dir.iterdir())}")
        text = "Detected debug environment, setting log level to DEBUG"
        # 打印颜色设置为黄色
        print(f"\033[33m{text}\033[0m")
        return True


default_config = {
    "model_dir": "model/",
    "retriever_config": {
        "module_name": "retriever",
        "model_name": "zyw0605688/gte-large-zh:latest",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_type": "openai",
        "api_key": "null",
    },
    "mllm_chat_bot_config": {
        "module_name": "chat_bot",
        "model_name": "qwen2.5vl:7b",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_type": "openai",
        "api_key": "null",
    },
    "chat_bot_config": {
        "module_name": "chat_bot",
        "model_name": "qwen2.5:0.5b",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_type": "openai",
        "api_key": "null",
    },
}


class BotConfig:
    module_name: str
    model_name: str
    base_url: str
    api_type: str
    api_key: str

    def __init__(
        self,
        module_name: str,
        model_name: str,
        base_url: str,
        api_type: str,
        api_key: str,
    ):
        self.module_name = module_name
        self.model_name = model_name
        self.base_url = base_url
        self.api_type = api_type
        self.api_key = api_key
        self.base_url = base_url


class Config:
    model_dir: str
    retriever_config: BotConfig
    mllm_chat_bot_config: BotConfig
    chat_bot_config: BotConfig

    def __init__(
        self,
        config_path: Optional[str] = None,
        model_dir: Optional[str] = None,
        retriever_config: Optional[BotConfig] = None,
        mllm_chat_bot_config: Optional[BotConfig] = None,
        chat_bot_config: Optional[BotConfig] = None,
    ):
        if path := config_path:
            if not Path(path).exists() or not Path(path).suffix in [".yaml", ".yml"]:
                with open(
                    self_dir.joinpath("config.yaml").resolve().__str__(),
                    "w",
                    encoding="utf-8",
                ) as f:
                    yaml.dump(default_config, f, allow_unicode=True)

            with open(path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            self.model_dir = config_data.get("model_dir", default_config["model_dir"])
            self.retriever_config = BotConfig(
                **config_data.get(
                    "retriever_config", default_config["retriever_config"]
                )
            )
            self.mllm_chat_bot_config = BotConfig(
                **config_data.get(
                    "mllm_chat_bot_config", default_config["mllm_chat_bot_config"]
                )
            )
            self.chat_bot_config = BotConfig(
                **config_data.get("chat_bot_config", default_config["chat_bot_config"])
            )
        else:
            self.model_dir = model_dir or default_config["model_dir"]
            self.retriever_config = retriever_config or BotConfig(
                **default_config["retriever_config"]
            )
            self.mllm_chat_bot_config = mllm_chat_bot_config or BotConfig(
                **default_config["mllm_chat_bot_config"]
            )
            self.chat_bot_config = chat_bot_config or BotConfig(
                **default_config["chat_bot_config"]
            )


config = Config(config_path=self_dir.joinpath("config.yaml").resolve().__str__())
