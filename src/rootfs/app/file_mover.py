import shutil
from pathlib import Path
from typing import List

import tokenizer
from pydantic import BaseModel


class _MoveOperation():
	src: Path
	dst: Path

	def __init__(self, src: Path, base_dir: Path, tokenizer: tokenizer.Tokenizer):
		self.src = src
		self.dst = base_dir.joinpath(Path(tokenizer.apply(path=src)))

class Mover(BaseModel):
	tokenizer: tokenizer.Tokenizer

	def move(
		self,
		destination_dir: Path,
		files: List[Path],
		overwrite: bool = True
	) -> None:
		moves = [_MoveOperation(src = file, base_dir = destination_dir, tokenizer = self.tokenizer) for file in files]

		# Check all files ahead of time to avoid partial moves
		for move in moves:
			if move.dst.exists() and not overwrite:
				raise FileExistsError(f"Destination file already exists: {move.dst.as_posix()}")

		# Move files
		for move in moves:
			if not move.dst.parent.exists():
				move.dst.parent.mkdir(parents=True)
			shutil.copy(move.src, move.dst)
			move.src.unlink(False)
