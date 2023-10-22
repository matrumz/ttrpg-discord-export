from os import environ
from pathlib import Path
from typing import Any, Dict, List, Optional

import exporter
import tokenizer
import TyrrrzDiscordChatExporter
import yaml
from deepmerge import always_merger as merger
from pydantic import BaseModel, Field


class Config(BaseModel):
	class _Dump(BaseModel):
		format: str = Field(default='config.yaml')
		# tokens: Dict[str, Any] = Field(default={})
		tokens: tokenizer.Tokens = tokenizer.Tokens()

	date_format: str = Field(alias='date-format')
	end_date: Optional[str] = Field(alias='end-date', default=None)
	start_date: Optional[str] = Field(alias='start-date', default=None)
	tz: str = Field(default=environ.get('TZ', 'America/New_York'))
	export: exporter.Config
	config_dump: _Dump = Field(alias='config-dump')

	tyrrrz_discordchatexporter: TyrrrzDiscordChatExporter.TyrrrDiscordChatExporter = Field(alias='tyrrrz/discordchatexporter')

	@classmethod
	def read(cls, paths: List[Path]) -> 'Config':
		data: Dict[str, Any] = {}
		for path in paths:
			with open(path, 'r') as file:
				merger.merge(data, yaml.safe_load(file))
		return cls(**data)

class Tokenizer(tokenizer.Tokenizer):
	class Tokens(tokenizer.Tokens):
		start_date: Optional[str] = None
		end_date: Optional[str] = None
		run_date: Optional[str] = None

	def tokenize(self) -> Tokens:
		return self.tokens
