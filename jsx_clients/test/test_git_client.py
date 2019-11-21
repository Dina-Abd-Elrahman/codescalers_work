import os
from Jumpscale import j
from testconfig import config
from base_test import BaseTest
from parameterized import parameterized


class TestGitClient(BaseTest):

    user_name = config["git"]["name"]
    user_email = config["git"]["email"]
    user_passwd = config["git"]["passwd"]
    REPO_DIR = "/tmp/test_tft"
    REPO_NAME = "test_git_client"
    GIT_REPO = "{}/code/test/tfttesting/test_git_client".format(REPO_DIR)

    @classmethod
    def setUpClass(cls):

        cls.info("Create a git repo directory")
        j.sal.fs.createDir(cls.GIT_REPO)

        cls.info("Change directory to {}, and create an empty Git repository".format(cls.GIT_REPO))
        cls.os_command("cd {} && git init".format(cls.GIT_REPO))

        cls.info("Create a git client")
        cls.GIT_CLIENT = j.clients.git.get(cls.GIT_REPO)

    def setUp(self):

        self.sub_word = "file"
        self.RAND_FILE_1 = self.sub_word + self.rand_string()
        self.RAND_FILE_2 = self.sub_word + self.rand_string()

        self.info("Create two files in a git repo directory")
        j.sal.fs.createEmptyFile("{}/{}".format(self.GIT_REPO, self.RAND_FILE_1))
        j.sal.fs.createEmptyFile("{}/{}".format(self.GIT_REPO, self.RAND_FILE_2))

        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    @classmethod
    def tearDownClass(cls):
        cls.info("Remove remote branch")
        cls.os_command("git push origin --delete {}".format(cls.REPO_NAME))

        cls.info("Remove git repo directory")
        cls.os_command("rm -rf {}".format(cls.REPO_DIR))

    def test001_addfiles(self):
        """
        TC 480
        Test case for addfiles method in git client.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Add one of those two file, using addfiles method.
        #. Make sure that this file is added correctly.
        #. Try to add non existing file, should return an error.
        """
        self.info("Add one of those two file, using addfiles method")
        self.GIT_CLIENT.addFiles(files=[self.RAND_FILE_1])

        self.info("Make sure that this file is added correctly")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("{}".format(self.RAND_FILE_1), output.decode())

        self.info("Try to add non existing file, should return an error")
        with self.assertRaises(Exception) as error:
            self.GIT_CLIENT.addFiles(files=["RANDOM_FILE"])
            self.assertTrue("No such file or directory" in error.exception.args[0])

    def test002_addRemoveFiles(self):
        """
        TC 484
        Test Case for addRemoveFiles method in git client.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Create another two files, commit and remove them again.
        #. Use addRemoveFiles method, check the output.
        #. Make sure that those two files are added correctly.
        """
        self.info("Create two files, commit and remove them again")
        File1 = self.rand_string()
        File2 = self.rand_string()
        self.GIT_CLIENT.addFiles(files=[File1, File2])
        self.os_command("cd {} && rm {} {}".format(self.GIT_REPO, File1, File2))

        self.info("Add those files, using addRemoveFiles method")
        self.GIT_CLIENT.addRemoveFiles()

        self.info("Make sure that those two files are added correctly")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("{}\n{}".format(self.RAND_FILE_1, self.RAND_FILE_2), output.decode())
        self.assertNotIn(File1, File2, output.decode())

    def test003_checkFilesWaitingForCommit(self):
        """
        TC 540
        Test Case for checkFilesWaitingForCommit.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Check that there is files waiting for commit.
        #. Add those files to git repo.
        #. Recheck again if there are files waiting for commit or not.
        """
        self.info("Check that there is files waiting for commit")
        self.assertTrue(self.GIT_CLIENT.checkFilesWaitingForCommit())

        self.info("Add those files to git repo")
        self.GIT_CLIENT.addFiles(files=[self.RAND_FILE_1, self.RAND_FILE_2])

        self.info("Recheck again if there are files waiting for commit or not")
        self.assertFalse(self.GIT_CLIENT.checkFilesWaitingForCommit())

    def test004_checkout(self):
        """
        TC 541
        Test Case for checkout method.

        **Test scenario**
        #. Create a new branch and checkout to this new created branch.
        #. Checkout to master branch.
        """
        self.info("Create a new branch and checkout to this new created branch")
        BRANCH_NAME = self.rand_string()
        self.os_command("cd {} && git checkout -b {}".format(self.GIT_REPO, BRANCH_NAME))
        self.assertEqual(BRANCH_NAME, self.GIT_CLIENT.describe()[1])

        self.info("Checkout to master branch")
        self.GIT_CLIENT.checkout("master")
        self.assertEqual("master", self.GIT_CLIENT.describe()[1])

    def test005_commit(self):
        """
        TC 542
        Test Case for commit method.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use commit with addremove=False, check the commit_id, Make sure the two files aren't added to git repo.
        #. Repeat step 1 again, with addremove=True, and check the output and make sure that the files is added.
        """
        self.info("Use commit with addremove=False, check the commit_id")
        commit = self.GIT_CLIENT.commit(addremove=False)
        commit_1 = commit.hexsha
        self.assertTrue(commit_1)

        self.info("Make sure the two files aren't added to git repo")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertNotIn(self.RAND_FILE_1, self.RAND_FILE_2, output.decode())

        self.info("Use commit with addremove=True, and check the output and make sure that the files is added")
        commit = self.GIT_CLIENT.commit(message="test commit", addremove=True)
        commit_2 = commit.hexsha
        self.assertNotEquals(commit_1, commit_2)

    # def test006_getBranchOrTag(self):
    #     """
    #     TC 544
    #
    #     **Test scenario**
    #     #.
    #     """
    #
    # def test007_describe(self):
    #     """
    #     TC 543
    #
    #     **Test scenario**
    #     #.
    #     """
    #
    # def test008_getChangedFiles(self):
    #     """
    #     TC
    #
    #     **Test scenario**
    #     #.
    #     """

    def test009_gitconfig(self):
        """
        TC 545
        Test getconfig method.

        **Test scenario**
        #. Use getconfig to get the value of certain git config field.
        #. Redo step 1 again, but with non valid value.
        """
        self.info("Use getconfig to get the value of certain git config field")
        self.GIT_CLIENT.setConfig("user.name", self.user_name, local=False)
        self.assertEqual(self.user_name, self.GIT_CLIENT.getConfig("user.name"))

        self.info("Redo step 1 again, but with non valid value")
        self.assertFalse(self.GIT_CLIENT.getConfig("RANDOM"))

    def test010_getModifiedFiles(self):
        """
        TC 547
        Test getModifiedFiles method.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use getModifiedFiles to test that those two files are added.
        #. Delete one of those two files, and check if it deleted or not.
        #. Use getModifiedFiles with options (collapse, ignore), and check the output.
        """
        self.info("Use getModifiedFiles to test that those two files are added")
        NEW_FILES = [val for key, val in self.GIT_CLIENT.getModifiedFiles().items() if "N" in key]
        self.assertEqual(sorted(NEW_FILES), sorted([self.RAND_FILE_1, self.RAND_FILE_2]))

        self.info("Delete one of those two files, and check if it deleted or not")
        self.GIT_CLIENT.addFiles([self.RAND_FILE_1, self.RAND_FILE_2])
        os.remove("{}/{}".format(self.GIT_REPO, self.RAND_FILE_1))
        DELETED_FILE = [val for key, val in self.GIT_CLIENT.getModifiedFiles().items() if "D" in key]
        self.assertEqual(self.RAND_FILE_1, DELETED_FILE)

        self.info("Use getModifiedFiles with (collapse, ignore) options")
        j.sal.fs.createEmptyFile("{}/test_1".format(self.GIT_REPO))
        j.sal.fs.createEmptyFile("{}/test_2".format(self.GIT_REPO))
        self.assertEqual("test_2", self.GIT_CLIENT.getModifiedFiles(collapse=True, ignore=["test_1"]))

    def test011_hasModifiedFiles(self):
        """
        TC 548
        Test hasModifiedFiles method

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use hasModifiedFiles to check the output, should be True.
        #. Add those files and recheck again, the output should be false.
        """
        self.info("Use hasModifiedFiles to check the output")
        self.assertTrue(self.GIT_CLIENT.hasModifiedFiles())

        self.info("Add those files {}, {}".format(self.RAND_FILE_1, self.RAND_FILE_2))
        self.GIT_CLIENT.commit()

        self.info("Check again after we add the files")
        self.assertFalse(self.GIT_CLIENT.hasModifiedFiles())

    def test012_patchGitignore(self):
        """
        TC 551
        Test patchGitignore method

        **Test scenario**
        #. Use patchGitignore and check if .gitignore file is created or not.
        """
        self.info("Use patchGitignore and check if .gitignore file is created or not")
        self.GIT_CLIENT.patchGitignore()
        self.assertTrue(os.path.isfile({} / ".gitignore".format(self.GIT_REPO)))

    # def test013_pull(self):
    #     """
    #     TC 552
    #     Test pull method
    #
    #     **Test scenario**
    #     #.
    #     """
    #
    # def test014_push(self):
    #     """
    #     TC 554
    #
    #     **Test scenario**
    #     #.
    #     """

    def test015_removeFiles(self):
        """
        TC 555
        Test removeFiles method.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use removeFiles, and check if those files are deleted or not.
        #. Try to use removeFiles to check non existing file, should raise an error.
        """
        self.GIT_CLIENT.addFiles([self.RAND_FILE_1, self.RAND_FILE_2])

        self.info("Use removeFiles, and check if those files are deleted or not")
        self.GIT_CLIENT.removeFiles([self.RAND_FILE_2])
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertNotIn("{}".format(self.RAND_FILE_1), output.decode())

        self.info("Try to use removeFiles to check non existing file")
        with self.assertRaises(Exception) as error:
            self.GIT_CLIENT.removeFiles(files=["RANDOM_FILE"])
            self.assertTrue("did not match any files" in error.exception.args[0])

    def test016_setConfig_unsetconfig(self):
        """
        TC 556
        Test setConfig method

        **Test scenario**
        #. Set user mail.
        #. Try to set non valid field.
        #. Unset the email.
        """
        self.info("Set user mail")
        self.GIT_CLIENT.setConfig("user.email", self.user_email, local=False)
        self.assertEqual(self.user_email, self.GIT_CLIENT.getConfig("user.email"))

        self.info("Try to set non valid field")
        with self.assertRaises(Exception) as error:
            self.GIT_CLIENT.setConfig("NON_VALID", "NON_VALID", local=False)
            self.assertTrue("key does not contain a section" in error.exception.args[0])

        self.info("Unset the email")
        self.GIT_CLIENT.unsetConfig("user.email", local=False)

    # def test017_setRemoteURL(self):
    #     """
    #     """

    # @parameterized.expand([
    #     ("test", True),
    #     ("NEW", True),
    #     ("test", False),
    #     ("NEW", False),
    # ])
    # def test018_switchBranch(self):
    #     """
    #     TC 558
    #
    #     **Test scenario**
    #     #. Create new branch.
    #     #. Use switchBranch with (existing branch name, create=True).
    #     #. Use switchBranch with (non existing branch name, create=True).
    #     #. Use switchBranch with (existing branch name, create=False).
    #     #. Use switchBranch with (non existsing branch name, create=False)
    #     """
