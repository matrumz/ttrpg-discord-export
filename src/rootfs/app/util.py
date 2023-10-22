import docker
from pydantic import BaseModel


class DockerImage(BaseModel):
	image: str
	version: str
	@property
	def image_version(self) -> str:
		return f"{self.image}:{self.version}"

def static_vars(**kwargs):
	"""
	Used to create static variables in a function.
	ex:
		@static_vars(counter=0)
		def foo():
			foo.counter += 1
			print("Counter is %d" % foo.counter)
	"""
	def decorator(func):
		for k in kwargs:
			setattr(func, k, kwargs[k])
		return func
	return decorator

@static_vars(client = None)
def docker_client() -> docker.DockerClient:
	if docker_client.client == None:
		docker_client.client = docker.from_env()
	return docker_client.client
