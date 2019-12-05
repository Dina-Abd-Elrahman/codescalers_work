import uuid
from Jumpscale import j
from base_test import BaseTest


class TestSshAgentClient(BaseTest):
    def setUp(self):
        self.SSHKEYCLIENT_NAME = str(uuid.uuid4()).replace("-", "")[:10]
        self.info("create sshkey client with name {}".format(self.SSHKEYCLIENT_NAME))

        self.PATH = "/tmp/.ssh/test_sshagent_client"
        self.skey = j.clients.sshkey.get(name=self.SSHKEYCLIENT_NAME, path=self.PATH)
        self.skey.save()

        self.info("Set default sshkey agent name")
        j.clients.sshagent.key_default_name = self.SSHKEYCLIENT_NAME

        self.info("Set sshkey agent name")
        j.clients.sshagent.key_names = self.SSHKEYCLIENT_NAME

        self.info("Set sshkey agent path")
        j.clients.sshagent.key_paths = self.PATH

        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    def tearDown(self):
        self.info("Delete sshkey client files from ssh directory {}".format(self.SSHKEYCLIENT_NAME))
        self.skey.delete_from_sshdir()

        self.info("Delete sshkey client")
        self.skey.delete()

    def test001_start_and_kill_sshagent(self):
        """
        TC
        Test start and kill ssh agent.

        **Test scenario**
        #. Start ssh agent client.
        #. Load sshkey in sshagent.
        #. Check that ssh agent is loaded.
        #. Try kill method in ssh agent client.
        #. Check that ssh agent is unloaded.
        """
        self.info("Start ssh agent client")
        j.clients.sshagent.start()

        self.info("Load sshkey in sshagent")
        j.clients.sshagent.key_load()

        self.info("Check that ssh agent is loaded")
        self.assertTrue(self.skey.is_loaded())

        self.info("Try kill method in ssh agent client")
        j.clients.sshagent.kill()

        self.info("Check that ssh agent is unloaded")
        self.assertFalse(self.skey.is_loaded())

    def test002_keys_list_and_keypub_path_get(self):
        """
        TC
        Test list of ssh keys in sshagent, and public key path.

        **Test scenario**
        #. Check the list of the loaded ssh key in ssh agent using keys_list method in sshagent.
        #. Check the public key path of the loaded ssh key in ssh agent using keypub_path_get method in sshagent
        """
        self.info("Check the list of the loaded ssh key in ssh agent using keys_list method in sshagent")
        self.assertIn(self.PATH, j.clients.sshagent.keys_list())

        self.info(
            "Check the public key path of the loaded ssh key in ssh agent using keypub_path_get method in sshagent"
        )
        self.assertIn(self.PATH, j.clients.sshagent.keypub_path_get())
