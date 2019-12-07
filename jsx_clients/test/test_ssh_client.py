import unittest
from Jumpscale import j
from random import randint
from testconfig import config
from base_test import BaseTest


class SshClient(BaseTest):
    addr = config["ssh"]["addr"]
    port = config["ssh"]["port"]
    login = config["ssh"]["login"]
    passwd = config["ssh"]["passwd"]

    @classmethod
    def setUpClass(cls):
        cls.info("create ssh client")
        cls.ssh_client = j.clients.ssh.get(
            name="SSH_{}".format(randint(1, 1000)),
            addr=cls.addr,
            port=cls.port,
            login=cls.login,
            passwd=cls.passwd
        )

    @classmethod
    def tearDownClass(cls):
        cls.info("delete ssh client")
        cls.ssh_client.delete()

    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    def install_nginx(self):
        self.info("install nginx on remote machine")
        self.os_command('sshpass -p {} ssh root@{} -p {} "sudo apt install nginx -y "'
                        .format(self.passwd, self.addr, self.port))

    def check_nginx_install(self):
        self.info("check that nginx is installed correctly")
        self.install_nginx()

        output, error = self.os_command('sshpass -p {} ssh root@{} -p {} "curl localhost"'
                                        .format(self.passwd, self.addr, self.port))

        self.info("check that nginx is installed correctly on remote machine")
        if "Welcome to nginx!" in output.decode():
            return True
        else:
            return False

    def test001_addr_variable_properites(self):
        """
        TC 509
        Test addr variable property.

        **Test scenario**
        #. Check the output from addr variable property it should equal to addr of remote ssh machine.
        """

        self.info("Check addr variable property")
        self.assertEqual(self.ssh_client.addr_variable, self.addr)

    def test002_port_variable_property(self):
        """
        TC 510
        Test port variable property.

        **Test scenario**
        #. Check the output from port variable property it should equal to port of remote ssh machine.
        """

        self.info("Check port variable property")
        self.assertEqual(str(self.ssh_client.port_variable), str(self.port))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/206")
    def test003_is_connected_property(self):
        """
        TC 511
        Test is_connected property, which checks if the ssh client has been connected or not.

        **Test scenario**
        #. Check that is_connected property is True.
        """

        self.info("Check that is_connected property is True")
        self.assertTrue(self.ssh_client.isconnected)

    def test004_file_copy(self):
        """
        TC 485
        Test file_copy method,which copies files from local machine to remote one.

        **Test scenario**
        #. Create test file, in local machine.
        #. Copy the file from local to remote machine.
        #. Make sure that the file is copied correctly.
        #. Try to copy non valid local file, to remote file, should fail
        """

        self.info("Create file locally")
        with open('/tmp/ssh_test04.txt', 'w') as f:
            data = 'test ssh client copy_file function\n'
            f.write(data)

        self.info("Copy the file from local to remote machine")
        self.ssh_client.file_copy("/tmp/ssh_test04.txt", "/tmp/ssh_test04.txt")

        self.info("Make sure that the file is copied correctly")
        output, error = self.os_command('sshpass -p {} ssh {}@{} -p {} "cat /tmp/ssh_test04.txt"'
                                        .format(self.passwd, self.login, self.addr, self.port))
        self.assertEqual("test ssh client copy_file function\n", output.decode())

        self.info("Try to copy non valid local file, to remote file, should fail")
        with self.assertRaises(Exception):
            self.ssh_client.copy_file("{}".format(self.rand_string()), "/tmp/ssh")

    def test005_download_with_valid_source_valid_dest_none_ignoredir_none_ignorefiles_recursive_True(self):
        """
        TC 491
        Test download method in ssh client, which copies files from remote machine to local one,
        with none ignorefiles, none ignoredir , and recursive=True.

        ignoredir: list of directory to be ignored.
        ignorefiles: list of files to be ignored.

        **Test scenario**
        #. Create a file in a directory in remote machine, with certain file name.
        #. Use download method to copy this directory in my local machine in /tmp/ssh_test05/.
        #. Check if files is downloaded or not.
        """

        self.info("Create a file in a directory in remote machine, with certain file name")
        self.os_command('sshpass -p {} ssh {}@{} -p {} "mkdir  /tmp/ssh_test05/"'
                        .format(self.passwd, self.login, self.addr, self.port))
        self.os_command('sshpass -p {} ssh {}@{} -p {} "touch /tmp/ssh_test05/test1 /tmp/ssh_test05/test2"'
                        .format(self.passwd, self.login, self.addr, self.port))

        self.info("Use download method to copy this directory in my local machine in /tmp/ssh_test05/")
        self.ssh_client.download(source="/tmp/ssh_test05/", dest="/tmp/ssh_test05/")

        self.info("Check if files is downloaded or not")
        output, error = self.os_command('ls /tmp/ssh_test05/')
        self.assertFalse(error)
        self.assertEqual("test1\ntest2\n", output.decode())

    def test006_download_with_valid_source_valid_dest_none_ignoredir_none_ignorefiles_recursive_False(self):
        """
        TC 502
        Test download method in ssh client, which copies files from remote machine to local one,
        with none ignorefiles, none ignoredir , and recursive=False.

        ignoredir: list of directory to be ignored.
        ignorefiles: list of files to be ignored.

        **Test scenario**
        #. Create a files in a directory in remote machine, with certain file name.
        #. Use download method to copy this directory in my local machine in /tmp/test_ssh06/.
        #. Check if files is downloaded or not.
        """

        self.info("Create a files in a directory in remote machine, with certain file name")
        self.os_command('sshpass -p {} ssh {}@{} -p {} "mkdir  /tmp/ssh_test06/test1/test2 -p"'
                        .format(self.passwd, self.login, self.addr, self.port))
        self.os_command(
            'sshpass -p {} ssh {}@{} -p {} "touch /tmp/ssh_test06/test06_1 /tmp/ssh_test06/test1/test2/test3"'
            .format(self.passwd, self.login, self.addr, self.port))

        self.info("Use download method to copy this directory in my local machine in /tmp/test_ssh06/")
        self.ssh_client.download(source="/tmp/ssh_test06/", dest="/tmp/ssh_test06/", recursive=False)

        self.info("Check if files is downloaded or not")
        output, error = self.os_command('ls /tmp/ssh_test06/')
        self.assertFalse(error)
        self.assertEqual("test06_1\n", output.decode())

    def test007_download_with_valid_source_valid_dest_with_ignoredir_with_ignorefiles_recursive_True(self):
        """
        TC 503
        Test download method in ssh client with ignorefiles, ignoredir , and recursive=True.

        **Test scenario**
        #. Create a files in a directory in remote machine, with certain file name.
        #. Use download method to copy this directory in my local machine in /tmp/ssh_test07/.
        #. Check if files is downloaded or not.
        """

        self.info("Create a files in a directory in remote machine, with certain file name")
        self.os_command('sshpass -p {} ssh {}@{} -p {} "mkdir  /tmp/ssh_test07/test1 /tmp/ssh_test07/test2 -p"'
                        .format(self.passwd, self.login, self.addr, self.port))
        self.os_command(
            'sshpass -p {} ssh {}@{} -p {} "touch /tmp/ssh_test07/test07_1 /tmp/ssh_test07/test7_2"'
            .format(self.passwd, self.login, self.addr, self.port)
        )

        self.info("Use download method to copy this directory in my local machine in /tmp/ssh_test07/")
        self.ssh_client.download(
            source="/tmp/ssh_test07/",
            dest="/tmp/ssh_test07/",
            recursive=True,
            ignoredir=["test2"],
            ignorefiles=["test07_2"]
        )

        self.info("Check if files is downloaded or not")
        output, error = self.os_command('ls /tmp/ssh_test07/')
        self.assertFalse(error)
        self.assertEqual("test1\ntest07_1\n", output.decode())

    def test008_upload_with_valid_source_valid_dest_none_ignoredir_none_ignorefiles_recursive_True(self):
        """
        TC 491
        Test upload method in ssh client with none ignorefiles, none ignoredir, and recursive=True.

        **Test scenario**
        #. Create a file in a directory in a local machine, with certain file name.
        #. Use upload method to copy this directory in my local machine in /tmp/ssh_test08/.
        #. Check if files is uploaded or not.
        """

        self.info("Create a file in a directory in a local machine, with certain file name")
        self.os_command("mkdir  /tmp/ssh_test08/")
        self.os_command("touch /tmp/ssh_test08/test1 /tmp/ssh_test08/test2")

        self.info("Use upload method to copy this directory in my local machine in /tmp/ssh_test08/")
        self.ssh_client.upload(source="/tmp/ssh_test08/", dest="/tmp/ssh_test08/")

        self.info("Check if files is uploaded or not")
        output, error = self.os_command('sshpass -p {} ssh {}@{} -p {} "ls /tmp/ssh_test12/"'
                                        .format(self.passwd, self.login, self.addr, self.port))
        self.assertFalse(error)
        self.assertEqual("test1\ntest2\n", output.decode())

    def test009_upload_with_valid_source_valid_dest_none_ignoredir_none_ignorefiles_recursive_False(self):
        """
        TC 506
        Test upload method in ssh client with none ignorefiles, none ignoredir, and recursive=False.

        **Test scenario**
        #. Create a files in a directory in local machine, with certain file name.
        #. Use upload method to copy this directory in my local machine in /tmp/ssh_test09/.
        #. Check if files is uploaded or not.
        """

        self.info("Create a files in a directory in local machine, with certain file name")
        self.os_command("mkdir  /tmp/ssh_test09/test1/test2 -p")
        self.os_command("touch /tmp/ssh_test09/test09_1 /tmp/ssh_test09/test1/test2/test3")

        self.info("Use upload method to copy this directory in my local machine in /tmp/ssh_test09/")
        self.ssh_client.upload(source="/tmp/ssh_test09/", dest="/tmp/ssh_test09/", recursive=False)

        self.info("Check if files is uploaded or not")
        output, error = self.os_command('sshpass -p {} ssh {}@{} -p {} "ls /tmp/ssh_test09/"'
                                        .format(self.passwd, self.login, self.addr, self.port))
        self.assertFalse(error)
        self.assertEqual("test09_1\n", output.decode())

    def test010_upload_with_valid_source_valid_dest_with_ignoredir_with_ignorefiles_recursive_True(self):
        """
        TC 507
        Test upload method in ssh client with none ignorefiles, none ignoredir, and recursive=True.

        **Test scenario**
        #. Create a files in a directory in local machine, with certain file name.
        #. Use upload method to copy this directory in from my local machine in /tmp/ssh_test10/.
        #. Check if files is uploaded or not.
        """

        self.info("Create a file in a directory in remote machine, with certain file name.")
        self.os_command("mkdir /tmp/ssh_test10/test1/ /tmp/ssh_test10/test2/ -p")

        self.os_command("touch /tmp/ssh_test10/test10_1 /tmp/ssh_test10/test10_2")

        self.info("Use upload method to copy this directory in my local machine in /tmp/ssh_test10/")
        self.ssh_client.upload(
            source="/tmp/ssh_test10/",
            dest="/tmp/ssh_test10/",
            recursive=True,
            ignoredir=["test2"],
            ignorefiles=["test10_2"])

        self.info("Check if files is uploaded or not")
        output, error = self.os_command('sshpass -p {} ssh {}@{} -p {} "ls /tmp/ssh_test10/"'
                                        .format(self.passwd, self.login, self.addr, self.port))
        self.assertFalse(error)
        self.assertIn("test1\ntest10_1", output.decode())

    def test011_execute_for_valid_command_line(self):
        """
        TC 492
        Test execute command in remote machine.

        **Test scenario**
        #. Use execute method to execute (ls /) in remote machine.
        #. Check the output of this command.
        """
        self.assertIn("tmp", self.ssh_client.execute(cmd="ls /", interactive=False)[1])

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/160")
    def test012_execute_for_script(self):
        """
        TC 512
        Test execute method in ssh client method should pass.

        **Test scenario**
        #. Use execute method to execute multi-lines cmd with script option == True.
        #. Check that the output if this command.
        """

        self.info("Use execute method to execute multi-lines cmd with script option == True")
        self.assertEqual("test_execute_script\n",
                         self.ssh_client.execute(script=True, interactive=False, cmd="""
                         touch /tmp/test_execute_script
                         ls /tmp/ | grep test_execute_script
                         """)[1]
                         )

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/160")
    def test013_ssh_authorize_with_pubkeys_option_specified_and_home_dir(self):
        """
        TC 495
        Test ssh_authorize with pubkeys option specified, and home dir, should pass.

        **Test scenario**
        #. Grep pubkey from my system.
        #. Use ssh_authorize to copy local pubkey to remote host.
        #. Check on remote host if it copied already or not.
        #. Use ssh_authorize without pubkeys specified, and homedir option, should fail.
        """
        self.info("Grep pubkey from my system")
        pubkey = open("/{}/.ssh/id_rsa.pub".format(j.core.myenv.config["DIR_HOME"])).read()

        self.info("use ssh_authorize to copy local pubkey to remote host")
        self.ssh_client.ssh_authorize(pubkeys=pubkey, interactive=False)

        self.info("check the existence of the pubkey in the remote ssh directory")
        output, error = self.os_command('sshpass -p {} ssh root@{} -p {} "cat /{}/.ssh/authorized_keys"'
                                        .format(j.core.myenv.config["DIR_HOME"], self.passwd, self.addr, self.port))
        self.assertIn(pubkey, output.decode())

        self.info("use ssh_authorize without pubkeys specified, and homedir option")
        with self.assertRaises(Exception) as error:
            self.ssh_client.ssh_authorize(homedir="/root/.ssh/")
            self.assertTrue("sshkeyname needs to be specified" in error.exception.args[0])

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/204")
    def test014_portforward_to_local(self):
        """
        TC
        Test portforward_to_local method in ssh client

        **Test scenario**
        #. Install nginx in the remote machine.
        #. Make sure that nginx is installed correctly and works on port 80.
        #. Use portforward_to_local method to access it from my local machine to port 1234.
        #. Check that nginx is working on port 1234 from my local machine.
        """
        self.assertTrue(self.check_nginx_install())

        self.info("Create portforwarding_to_local using  portforward_to_local in ssh client")
        self.ssh_client.portforward_to_local(80, 99999)

        self.info("Check that port forwarding is created correctly")
        output, error = self.os_command("curl localhost:99999")
        self.assertFalse(error)
        self.assertIn("Welcome to nginx!", output.decode())

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/204")
    def test015_kill_port_forwarding(self):
        """
        TC
        Test kill_port_forwarding method in ssh client.

        **Test scenario**
        #. Create a port forwarding.
        #. Try to kill this port forwarding.
        """
        self.assertTrue(self.check_nginx_install())

        self.info("Create port forwarding from local to remote, using portforward_to_local in ssh client")
        self.ssh_client.portforward_to_local(80, 123456)

        self.info("Try to create a port forwarding using portforward_kill method")
        self.assertTrue(self.ssh_client.portforward_kill(123456))

    def test016_syncer(self):
        """
        TC
        Test syncer method in ssh client.

        **Test scenario**
        #. Create a instance from syncer method.
        #. Try to list ssh_clients in this method, should return our ssh_client.
        """
        self.info("Create a instance from syncer method")
        syncer = self.ssh_client.syncer

        self.info("Try to list ssh_clients in this method, should return our ssh_client")
        self.assertIn(self.ssh_client.name, str(syncer.sshclient_names))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/160")
    def test017_execute_jumpscale_for_valid_jsx_command(self):
        """
        TC
        Test execute_jumpscale method in ssh client for valid jsx command, should pass.

        **Test scenario**
        #. Use execute_jumpscale command create ssh_test28 file in /tmp directory.
        #. Make sure that this file is created correctly.
        """

        self.info("Use execute_jumpscale command create ssh_test28 file in /tmp directory")
        self.ssh_client.execute_jumpscale("j.sal.fs.touch(\"/tmp/ssh_test28\")")

        self.info("Make sure that this file is created correctly")
        output, error = self.os_command('sshpass -p {} ssh {}@{} -p {} "ls /tmp/"'
                                        .format(self.passwd, self.login, self.addr, self.port))

        self.assertIn("ssh_test17", output.decode())
