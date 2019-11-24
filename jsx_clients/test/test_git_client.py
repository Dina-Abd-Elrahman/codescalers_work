import os
from Jumpscale import j
from testconfig import config
from base_test import BaseTest


class TestGitClient(BaseTest):

    user_name = config["git"]["name"]
    user_email = config["git"]["email"]
    user_passwd = config["git"]["passwd"]
    git_token = config["git"]["token"]
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
        Test add new files in git repo.

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
        Test add new files and remove deleted ones..

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
        Test to check if there is files waiting for Commit or not.

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
        Test checkout method.

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
        Test commit method.

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

    def test006_describe_getBranchOrTag(self):
        """
        TC 543, 544
        Test get Branch or Tag name, and describe option in a git command.

        **Test scenario**
        #. Use describe to check the branch name.
        #. Create new tag.
        #. Use getBranchOrTag, and describe method to get the tag name.
        #. Add new files and commit.
        #. Use getBranchOrTag method to get the branch name.
        #. Use describe method and check the output.
        """
        self.info("Use describe to check the branch name")
        output, error = self.os_command("git branch | grep \\* | cut -d ' ' -f2")
        self.assertEqual("('branch', {})".format(output.decode().rstrip()), self.GIT_CLIENT.describe())

        self.info("Create new tag")
        self.os_command("cd {} && git tag 1.0".format(self.GIT_REPO))

        self.info("Use getBranchOrTag, and describe method to get the tag name")
        self.assertEqual("('tag', '1.0')", self.GIT_CLIENT.getBranchOrTag())
        self.assertEqual("('tag', '1.0\n')", self.GIT_CLIENT.describe())

        self.info("Add new files and commit")
        commit = self.GIT_CLIENT.commit("Add new files and commit")
        Commit_ID = commit.hexsha

        self.info("Use getBranchOrTag method to get the branch name")
        self.assertEqual("('branch', {})".format(output.decode().rstrip()), self.GIT_CLIENT.getBranchOrTag())

        self.info("Use describe method and check the output")
        self.assertEqual("('tag', '1.0-1-g{}\n')".format(Commit_ID[0:7]), self.GIT_CLIENT.describe())

    def test007_getChangedFiles(self):
        """
        TC
        Test getChangedFiles which lists all changed files since certain ref (Commit_ID).

        **Test scenario**
        #. Add 2 files to git repo, Commit.
        #. Use getChangedFiles method to get those files from certain ref (Commit_ID) to certain ref (Commit_ID).
        """
        self.info("Grep the current Commit_ID")
        output, error = self.os_command("git rev-parse HEAD")
        current_commit_id = output.decode().rstrip()

        self.info("Add 2 files to git repo, Commit")
        new_commit = self.GIT_CLIENT.commit("Add 2 files to git repo")

        self.info("Use getChangedFiles method to get those files from certain Commit_ID to certain ref (Commit_ID)")
        self.assertEqual(
            sorted([self.RAND_FILE_1, self.RAND_FILE_2]),
            sorted(self.GIT_CLIENT.getChangedFiles(fromref=current_commit_id, toref=new_commit.hexsha)),
        )

    def test008_gitconfig(self):
        """
        TC 545
        Test get config value to certain git config field.

        **Test scenario**
        #. Use getconfig to get the value of certain git config field.
        #. Redo step 1 again, but with non valid value.
        """
        self.info("Use getconfig to get the value of certain git config field")
        self.GIT_CLIENT.setConfig("user.name", self.user_name, local=False)
        self.assertEqual(self.user_name, self.GIT_CLIENT.getConfig("user.name"))

        self.info("Redo step 1 again, but with non valid value")
        self.assertFalse(self.GIT_CLIENT.getConfig("RANDOM"))

    def test009_getModifiedFiles(self):
        """
        TC 547
        Test to get the modified files.

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

    def test010_hasModifiedFiles(self):
        """
        TC 548
        Test the existing of modified files.

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

    def test011_patchGitignore(self):
        """
        TC 551
        Test patch gitignore file in git repo.

        **Test scenario**
        #. Use patchGitignore and check if .gitignore file is created or not.
        """
        self.info("Use patchGitignore and check if .gitignore file is created or not")
        self.GIT_CLIENT.patchGitignore()
        self.assertTrue(os.path.isfile("{}/.gitignore".format(self.GIT_REPO)))

    # def test012_pull(self):
    #     """
    #     TC 552
    #     Test pull method
    #
    #     **Test scenario**
    #     #.
    #     """
    #
    # def test013_push(self):
    #     """
    #     TC 554
    #
    #     **Test scenario**
    #     #.
    #     """

    def test014_removeFiles(self):
        """
        TC 555
        Test remove files from git repo.

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

    def test015_setConfig_unsetconfig(self):
        """
        TC 556
        Test set and unset new config values to certain config fields.

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

    def test016_setRemoteURL(self):
        """
        """

    def test017_switchBranch(self, Branch_Name, Create_status):
        """
        TC 558
        Test switch branch in git repo.

        **Test scenario**
        #. Create new branch.
        #. Use switchBranch with (existing branch name, create=True).
        #. Use switchBranch with (non existing branch name, create=True).
        #. Use switchBranch with (existing branch name, create=False).
        #. Use switchBranch with (non existing branch name, create=False).
        """
        self.info("Create new branch")
        new_branch_name = self.rand_string()
        self.os_command("cd {} && git checkout -b {}".format(self.GIT_REPO, new_branch_name))

        self.info("Use switchBranch with (existing branch name, create=True)")
        self.assertEqual(
            "was not able to create branch test_2", self.GIT_CLIENT.switchBranch("NEW_BRANCH", create=True)
        )

        self.info("Use switchBranch with (non existing branch name, create=True)")
        self.GIT_CLIENT.switchBranch("NEW_BRANCH", create=True)
        self.assertEqual("NEW_BRANCH", self.GIT_CLIENT.describe()[1])

        self.info("Use switchBranch with (existing branch name, create=False)")
        self.GIT_CLIENT.switchBranch(new_branch_name, create=False)
        self.assertEqual(new_branch_name, self.GIT_CLIENT.describe()[1])

        self.info("Use switchBranch with (non existing branch name, create=False)")
        with self.assertRaises(Exception) as error:
            self.GIT_CLIENT.switchBranch("BLABLA", create=False)
            self.assertTrue("did not match any file(s) known to git" in error.exception.args[0])
