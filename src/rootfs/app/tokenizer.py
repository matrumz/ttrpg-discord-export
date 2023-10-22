from abc import abstractmethod
from functools import reduce
from typing import Callable, Dict, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

# # Generics
# T = TypeVar['T']

# Serializer = Callable[[T], str]
# Deserializer = Callable[[str], T]

Serializer = Callable[[any], str]
Deserializer = Callable[[str], any]

class Tokens(BaseModel):
	model_config = ConfigDict(extra='allow')

	@classmethod
	def merged(cls, *tokens: 'Tokens'):
		tokens_dicts = [token.model_dump(exclude_unset=True) for token in tokens if token is not None]
		merged_dict = reduce(lambda a, b: a | b, tokens_dicts, {})
		return cls(**merged_dict)

class Tokenizer(BaseModel):
	# Serialization
	format: str
	# serializers: Dict[type[T], Serializer[T]] = {}
	# serializers: Dict[any, Serializer] = {}
	tokens: Tokens = Tokens()

	# Deserialization
	# deserializer: Dict[type[T], Deserializer[T]] = {}
	# deserializer: Dict[any, Deserializer] = {}

	@abstractmethod
	def tokenize(self, **kwargs) -> Tokens:
		pass

	def apply(self, **kwargs) -> str:
		# TODO use serializer
		tokens = self.tokenize(**kwargs)
		return eval(f'f"{self.format}"', tokens.model_dump() | tokens.model_extra)
