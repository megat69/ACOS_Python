import bcrypt
from dotenv import load_dotenv
import os
import json

def gen_hash(method:str="env", **kwargs):
	"""
	Generates a hash key.
	:param method: "env" (stores in a .env file) or "json" (stores in a .json file)
	:param kwargs: "file" is a the json file to save in,
	"key" param is the key to save the hash in.
	"""
	if method.lower() == "env":
		env_file = open(".env", "w", encoding="utf-8")
		env_file.write("HASH="+bcrypt.gensalt().decode())
		env_file.close()
	elif method.lower() == "json":
		json_file = open(kwargs["file"], "r")
		json_content = json.load(json_file)
		json_file.close()
		json_content[kwargs["key"]] = bcrypt.gensalt().decode()
		json_file = open(kwargs["file"], "w")
		json.dump(json_content, json_file, indent = 4)
		json_file.close()
	else:
		return bcrypt.gensalt().decode()


def get_hash(method:str="env", *args, **kwargs):
	if method.lower() == "env":
		load_dotenv()
		return os.getenv("HASH")
	elif method.lower() == "json":
		json_file = open(kwargs["file"], "r")
		json_content = json.load(json_file)
		json_file.close()
		return json_content[kwargs["key"]]
	elif method.lower() == "given":
		return args[0]

def cipher_password(password:(str, bytes), method:str="env", *args, **kwargs):
	if isinstance(password, str):
		password = password.encode()
	return bcrypt.hashpw(password, get_hash(method, *args, **kwargs).encode())

def get_password(file:str, key:str):
	json_file = open(file, "r")
	json_content = json.load(json_file)
	json_file.close()
	return json_content[key].encode()

def check_password(password:(str, bytes), method:str="env", **kwargs):
	if isinstance(password, str):
		password = password.encode()
	return bcrypt.checkpw(password, get_password(**kwargs))

def compare_passwords(password:(str, bytes), ciphered_password:(str, bytes)):
	if isinstance(password, str):
		password = password.encode()
	if isinstance(ciphered_password, str):
		ciphered_password = ciphered_password.encode()
	return bcrypt.checkpw(password, ciphered_password)
