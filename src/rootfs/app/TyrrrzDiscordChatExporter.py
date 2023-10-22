from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import exporter
import util
from pydantic import BaseModel, ConfigDict, Field

# This is the format that TyrrrzDiscordChatExporter uses
DATETIME_FORMAT = '%m/%d/%Y %H:%M'
# Default docker image and version
DOCKER_IMAGE = 'tyrrrz/discordchatexporter'
DOCKER_VERSION = 'stable'

class TyrrrDiscordChatExporter(BaseModel):

	docker: util.DockerImage = util.DockerImage(image=DOCKER_IMAGE, version=DOCKER_VERSION)
	export: 'Export'

	class _Command(BaseModel):
		model_config = ConfigDict(use_enum_values=True)
		def to_command_line_string(self) -> str:
			command_line = f"{self.__class__.__name__.lower()} "
			for attr, value in self.model_dump(by_alias=True).items():
				if value is None:
					continue
				elif isinstance(value, bool):
					command_line += f"--{attr}" if value else ""
				elif isinstance(value, list):
					command_line += f"--{attr} {' '.join(value)}"
				elif isinstance(value, datetime):
					command_line += f"--{attr} '{value.strftime(DATETIME_FORMAT)}'"
				elif isinstance(value, Enum):
					command_line += f"--{attr} {value.value}"
				else:
					command_line += f"--{attr} {value}"
				command_line += " "
			return command_line.strip()

	class Export(_Command):

		channel: Union[List[str], str]
		token: str

		after: Optional[datetime] = None
		before: Optional[datetime] = None
		filter: Optional[str] = None
		format: Optional['Format'] = None
		fuck_russia: Optional[bool] = Field(alias='fuck-russia', default=False)
		locale: Optional[str] = None
		markdown: Optional[bool] = None
		media: Optional[bool] = None
		media_dir: Optional[str] = Field(alias='media-dir', default=None)
		output: str = '/out/'
		parallel: Optional[int] = None
		partition: Optional[str] = None
		reuse_media: Optional[bool] = Field(alias='reuse-media', default=None)
		utc: Optional[bool] = None

		class Format(Enum):
			PLAINTEXT = 'PlainText'
			HTMLDARK = 'HtmlDark'
			HTMLLIGHT = 'HtmlLight'
			CSV = 'Csv'
			JSON = 'Json'

class Tokenizer(exporter.Tokenizer):
	class Tokens(exporter.Tokenizer.Tokens):
		pass

	def tokenize(self, path: Path) -> Tokens:
		"""
		channel example: "Are We Excited! - Text - planning-things [xxxxxxxxxxxxxxxxxx].txt
		thread example: "Are We Excited! - planning-things - Maud [xxxxxxxxxxxxxxxxxx].txt
		"""

		# Split file along known delimiter
		split_file = path.name.split(' - ')

		# Populate tokens from split string
		tokens = Tokenizer.Tokens(
			server = split_file[0],
			channel = split_file[1],
			thread = split_file[2].split(' [')[0]
		)

		# Fix case where channel is 'Text' and thread is the actual channel
		if tokens.channel == 'Text':
			tokens.channel = tokens.thread
			tokens.thread = None

		# Return tokens from parsed model using constructor-passed tokens as overrides
		return Tokenizer.Tokens.merged(tokens, self.tokens)
