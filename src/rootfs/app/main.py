#!/usr/bin/python3 -B

import argparse
import os
import socket
from datetime import datetime
from pathlib import Path

import file_mover
import TyrrrzDiscordChatExporter
import util
import yaml
from config import Config
from config import Tokenizer as ConfigTokenizer
from docker.errors import ContainerError
from docker.models.containers import Container


def main():
	# Parse arguments
	argparser = argparse.ArgumentParser(
		prog='ttrpg-discord-export'
	)
	argparser.add_argument("--config", "-c", type=str, help="Path(s) to config file(s)", required=True, nargs='+')
	argparser.add_argument("--start", "-s", type=str, help="Start date/time")
	argparser.add_argument("--end", "-e", type=str, help="End date/time")
	argparser.add_argument("--debug", "-d", action='store_true', help="Enable debug mode")
	args = argparser.parse_args()

	# Load config
	config = Config.read(args.config)

	# Parse dates
	if args.start:
		config.start_date = args.start
	if args.end:
		config.end_date = args.end
	config.tyrrrz_discordchatexporter.export.after = datetime.strptime(config.start_date, config.date_format)
	config.tyrrrz_discordchatexporter.export.before = datetime.strptime(config.end_date, config.date_format)

	# Directory management
	EXPORT_DIR = Path('/out')
	EXPORT_DIR.mkdir(parents=True, exist_ok=True)
	WORKING_DIR = Path('/working')
	WORKING_DIR.mkdir(parents=True, exist_ok=True)

	# Dump the config file
	tokenizer = ConfigTokenizer(
		format=config.config_dump.format,
		tokens=ConfigTokenizer.Tokens(**(
			ConfigTokenizer.Tokens(
				start_date=config.start_date,
				end_date=config.end_date,
				run_date=datetime.now().strftime(config.date_format)
			).model_dump(exclude_unset=True)
			| config.config_dump.tokens.model_dump(exclude_unset=True)
			| config.config_dump.tokens.model_extra if config.config_dump.tokens.model_extra is not None else {}
		))
	)
	config_dump_path = Path(EXPORT_DIR, tokenizer.apply())
	config_dump_path.parent.mkdir(parents=True, exist_ok=True)
	with open(config_dump_path, 'w') as file:
		yaml.safe_dump(config.model_dump(by_alias=True, exclude_unset=True, exclude={"tyrrrz_discordchatexporter": {"export": {"token": True}}}), file)

	# Create the exports tokenizer
	tokenizer = TyrrrzDiscordChatExporter.Tokenizer(
		format=config.export.format,
		tokens=TyrrrzDiscordChatExporter.Tokenizer.Tokens(**(
			TyrrrzDiscordChatExporter.Tokenizer.Tokens(
				start_date=config.start_date,
				end_date=config.end_date
			).model_dump(exclude_unset=True)
			| config.export.tokens.model_dump(exclude_unset=True)
			| config.export.tokens.model_extra if config.export.tokens.model_extra is not None else {}
		))
	)

	# Create the file mover
	mover = file_mover.Mover(tokenizer=tokenizer, )

	# Run the exporter container
	export_container_name = f"t-d-e-{datetime.now().strftime('%Y%m%d%H%M')}"
	data_exported = False
	try:
		docker_client = util.docker_client()

		# Download channels
		docker_client.containers.run(
			image=config.tyrrrz_discordchatexporter.docker.image_version,
			name=export_container_name,
			command=config.tyrrrz_discordchatexporter.export.to_command_line_string(),
			detach=False,
			environment={ 'TZ': config.tz },
			remove=False,
			stderr=True,
			stdout=True
		)

		# Get the exported files
		exporter_container: Container = docker_client.containers.get(export_container_name)
		this_container: Container = docker_client.containers.get(socket.gethostname())
		export_data, stat = exporter_container.get_archive(config.tyrrrz_discordchatexporter.export.output)
		this_container.put_archive(WORKING_DIR, export_data)

		data_exported = True

	except ContainerError:
		print("Nothing exported")
		if config.debug:
			raise

	finally:
		try:
			docker_client.containers.get(export_container_name).remove()
		except:
			pass

	if not data_exported:
		return

	# Move the exported files
	files_dir = Path(WORKING_DIR.as_posix(), os.path.basename(config.tyrrrz_discordchatexporter.export.output.rstrip('/')))
	files = [Path(files_dir, f) for f in os.listdir(files_dir)]
	if files is not None:
		mover.move(
			destination_dir=EXPORT_DIR,
			files=files
		)

if __name__ == '__main__':
	main()
