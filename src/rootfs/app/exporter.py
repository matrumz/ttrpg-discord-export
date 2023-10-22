from abc import ABC
from typing import Optional

import tokenizer
from pydantic import BaseModel


class Config(BaseModel):
	format: str
	tokens: tokenizer.Tokens = tokenizer.Tokens()

class Tokenizer(tokenizer.Tokenizer, ABC):
	class Tokens(tokenizer.Tokens):
		start_date: Optional[str] = None
		end_date: Optional[str] = None
		server: Optional[str] = None
		channel: Optional[str] = None
		thread: Optional[str] = None
