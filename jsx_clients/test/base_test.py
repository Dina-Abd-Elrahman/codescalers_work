import uuid
import unittest
import subprocess
from Jumpscale import j
from loguru import logger


class BaseTest(unittest.TestCase):
    LOGGER = logger

    @staticmethod
    def info(message):
        BaseTest.LOGGER.info(message)

    @staticmethod
    def os_command(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, error = process.communicate()
        return output, error

    @staticmethod
    def rand_num(start=100, stop=1000):
        return j.data.idgenerator.generateRandomInt(start, stop)

    @staticmethod
    def rand_string(size=10):
        return str(uuid.uuid4()).replace("-", "")[1:10]
    
