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
    RANDOM_NAME = j.data.idgenerator.generateXCharID(10)
    REPO_NAME = j.data.idgenerator.generateXCharID(10)
    GIT_REPO = "{}/code/test/tfttesting/{}".format(REPO_DIR, REPO_NAME)

    @classmethod
    def setUpClass(cls):

        cls.info("Create remote repo, in github account")
        cls.github_account = j.clients.github.get(cls.RANDOM_NAME, token=cls.git_token)
        cls.repo = cls.github_account.repo_create(cls.REPO_NAME)

        cls.info("Initialized empty Git repository locally in {}, connect to remote one".format(cls.GIT_REPO))
        j.clients.git.pullGitRepo(dest=cls.GIT_REPO, url=cls.repo.clone_url, ssh=False)

        cls.info("Create a git client")
        cls.GIT_CLIENT = j.clients.git.get(cls.GIT_REPO)

    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    @classmethod
    def tearDownClass(cls):
        cls.info("Remove remote repo")
        repo_to_be_deleted = cls.github_account.repo_get(cls.REPO_NAME)
        cls.github_account.repo_delete(repo_to_be_deleted)

        cls.info("Remove git repo directory")
        cls.os_command("rm -rf {}".format(cls.REPO_DIR))

    def create_two_files(self):
        """
        Method to create 2 files in git repo.

        :return: Name of the files.
        """
        RAND_FILE_1 = self.rand_string()
        RAND_FILE_2 = self.rand_string()

        self.info("Create two files in a git repo directory")
        j.sal.fs.createEmptyFile("{}/{}".format(self.GIT_REPO, RAND_FILE_1))
        j.sal.fs.createEmptyFile("{}/{}".format(self.GIT_REPO, RAND_FILE_2))

        return RAND_FILE_1, RAND_FILE_2

    def get_current_branch_name(self):
        """
        Method to get current branch name.

        :return: Branch_name
        """
        output, error = self.os_command("cd {} && git branch | grep \\* | cut -d ' ' -f2".format(self.GIT_REPO))
        return output.decode().rstrip()

    def get_current_commit_id(self):
        """
        Method to get current Commit_ID

        :return: Commit_ID
        """
        output, error = self.os_command("git rev-parse HEAD")
        return output.decode().rstrip()

    def test001_add_files(self):
        """
        TC 480
        Test add new files in git repo.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Add one of those two file, using addfiles method.
        #. Make sure that this file is added correctly.
        #. Try to add non existing file, should return an error.
        """
        FILE_1, FILE_2 = self.create_two_files()

        self.info("Add one of those two file, using addfiles method")
        self.GIT_CLIENT.addFiles(files=[FILE_1])

        self.info("Make sure that this file is added correctly")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("{}".format(FILE_1), output.decode())

        self.info("Try to add non existing file, should return an error")
        with self.assertRaises(Exception) as error:
            self.GIT_CLIENT.addFiles(files=[self.RANDOM_NAME])
            self.assertTrue("No such file or directory" in error.exception.args[0])

    def test002_add_remove_files(self):
        """
        TC 484
        Test add new files and remove deleted ones.

        **Test scenario**
        #. Create two files in a git repo directory FILE_1, FILE_2.
        #. Create another two files FILE_3, FILE_4, add those two files, then remove them.
        #. Use addRemoveFiles method, to add FILE_1, FILE_2 and remove FILE_3, FILE_4.
        #. Make sure that FILE_1, FILE_2 are added, and FILE_3, FILE_4 are removed.
        """
        self.info("Create two files in a git repo directory FILE_1, FILE_2")
        FILE_1, FILE_2 = self.create_two_files()

        self.info("Create another two files FILE_3, FILE_4, add those two files, then remove them")
        FILE_3, FILE_4 = self.rand_string(), self.rand_string()
        self.GIT_CLIENT.addFiles(files=[FILE_3, FILE_4])
        self.os_command("cd {} && rm {} {}".format(self.GIT_REPO, FILE_3, FILE_4))

        self.info("Use addRemoveFiles method, to add FILE_1, FILE_2 and remove FILE_3, FILE_4")
        self.GIT_CLIENT.addRemoveFiles()

        self.info("Make sure that FILE_1, FILE_2 are added, and FILE_3, FILE_4 are removed")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("{}\n{}".format(FILE_1, FILE_2), output.decode())
        self.assertNotIn(FILE_3 and FILE_4, output.decode())

    def test003_check_files_waiting_for_commit(self):
        """
        TC 540
        Test to check if there are files waiting for Commit.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Check that there is files waiting for commit.
        #. Add those files to git repo.
        #. Recheck if there are files waiting for commit or not.
        """
        FILE_1, FILE_2 = self.create_two_files()

        self.info("Check that there is files waiting for commit")
        self.assertTrue(self.GIT_CLIENT.checkFilesWaitingForCommit())

        self.info("Add those files to git repo")
        self.GIT_CLIENT.addFiles(files=[FILE_1, FILE_2])

        self.info("Recheck if there are files waiting for commit.")
        self.assertFalse(self.GIT_CLIENT.checkFilesWaitingForCommit())

    def test004_checkout(self):
        """
        TC 541
        test checkout for branch, commit_id, and path.
        For more info, Please visit here https://git-scm.com/docs/git-checkout

        **Test scenario**
        #. Create a new branch and checkout to this branch.
        #. Checkout to master branch.
        #. Check the current Commit_ID.
        #. Create 2 files, add them, then commit.
        #. Use checkout to switch to previous Commit_ID.
        #. Remove one of the two files.
        #. Use checkout to return the removed file back.
        #. Check if FILE_1 is back or not.
        """
        self.info("Create a new branch and checkout to this new created branch")
        BRANCH_NAME = self.rand_string()
        self.os_command("cd {} && git checkout -b {}".format(self.GIT_REPO, BRANCH_NAME))
        self.assertEqual(BRANCH_NAME, self.get_current_branch_name())

        self.info("Checkout to master branch")
        self.GIT_CLIENT.checkout("master")
        self.assertEqual("master", self.get_current_branch_name())

        self.info("Check the current Commit_ID")
        current_commit_id = self.get_current_commit_id()

        self.info("Create 2 files, add them, then commit")
        FILE_1, FILE_2 = self.create_two_files()
        self.GIT_CLIENT.commit("Add two new files")
        new_commit_id = self.get_current_commit_id()

        self.info("Use checkout to switch to previous Commit_ID")
        self.GIT_CLIENT.checkout(current_commit_id)

        self.info("Check that checkout is checkout to the previous Commit_ID")
        self.assertEqual(current_commit_id, self.get_current_commit_id())
        self.assertNotEqual(new_commit_id, self.get_current_commit_id())

        self.info("Remove one of the two files")
        os.remove("{}/{}".format(self.GIT_REPO, FILE_1))

        self.info("Use checkout to return the removed file back")
        self.GIT_CLIENT.checkout("{}/{}".format(self.GIT_REPO, FILE_1))

        self.info("Check if {} is back or not".format(FILE_1))
        self.assertTrue(os.path.isfile("{}/{}".format(self.GIT_REPO, FILE_1)))

    def test005_commit(self):
        """
        TC 542
        Test commit method which record changes to git repo.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Edit one of the files, then add it.
        #. Use commit with addremove=False, check the commit_id, Make sure that only one file is added to git repo.
        #. Repeat step 1 again, with addremove=True, and check the output and make sure that the two files are added.
        """
        FILE_1, FILE_2 = self.create_two_files()

        self.info("Edit one of the files, then add it")
        with open("{}/{}".format(self.GIT_REPO, FILE_1), "a") as out:
            out.write("test" + "\n")
        self.GIT_CLIENT.addFiles([FILE_1])

        self.info("Use commit with addremove=False, check the commit_id, Make sure that only one file is added")
        commit = self.GIT_CLIENT.commit(addremove=False)
        commit_1 = commit.hexsha
        self.assertTrue(commit_1)
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertNotIn(FILE_2, output.decode())

        self.info("Use commit with addremove=True, and check the output and make sure that the two files are added")
        commit = self.GIT_CLIENT.commit(message="test commit", addremove=True)
        commit_2 = commit.hexsha
        self.assertNotEquals(commit_1, commit_2)
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn(FILE_2, output.decode())

    def test006_describe_and_get_branch_or_tag(self):
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

    def test007_get_changed_files(self):
        """
        TC
        Test getChangedFiles which lists all changed files since certain ref (Commit_ID).

        **Test scenario**
        #. Grep the current Commit_ID.
        #. Add 2 files (FILE_1, FILE_2) to git repo Commit.
        #. Grep the new Commit_ID.
        #. Use getChangedFiles method to get those two files from certain (current Commit_ID) to (new Commit_ID).
        """

        self.info("Grep the current Commit_ID")
        output, error = self.os_command("git rev-parse HEAD")
        current_commit_id = output.decode().rstrip()

        self.info("Add 2 files to git repo, Commit")
        FILE_1, FILE_2 = self.create_two_files()
        new_commit = self.GIT_CLIENT.commit("Add 2 files to git repo")

        self.info(
            "Use getChangedFiles method to get those two files from certain (current Commit_ID) to (new Commit_ID)"
        )
        self.assertEqual(
            sorted([FILE_1, FILE_2]),
            sorted(self.GIT_CLIENT.getChangedFiles(fromref=current_commit_id, toref=new_commit.hexsha)),
        )

    def test008_git_config(self):
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
        self.assertFalse(self.GIT_CLIENT.getConfig(self.RANDOM_NAME))

    def test009_get_modified_files(self):
        """
        TC 547
        Test to get the modified files.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use getModifiedFiles to test that those two files are added.
        #. Delete one of those two files, and check if it deleted or not.
        #. Use getModifiedFiles with options (collapse, ignore), and check the output.
        """
        FILE_1, FILE_2 = self.create_two_files()

        self.info("Use getModifiedFiles to test that those two files are added")
        NEW_FILES = [val for key, val in self.GIT_CLIENT.getModifiedFiles().items() if "N" in key]
        self.assertEqual(sorted(NEW_FILES), sorted([FILE_1, FILE_2]))

        self.info("Delete one of those two files, and check if it deleted or not")
        self.GIT_CLIENT.addFiles([FILE_1, FILE_2])
        os.remove("{}/{}".format(self.GIT_REPO, FILE_1))
        DELETED_FILE = [val for key, val in self.GIT_CLIENT.getModifiedFiles().items() if "D" in key]
        self.assertEqual(FILE_1, DELETED_FILE)

        self.info("Use getModifiedFiles with (collapse, ignore) options")
        j.sal.fs.createEmptyFile("{}/test_1".format(self.GIT_REPO))
        j.sal.fs.createEmptyFile("{}/test_2".format(self.GIT_REPO))
        self.assertEqual("test_2", self.GIT_CLIENT.getModifiedFiles(collapse=True, ignore=["test_1"]))

    def test010_has_modified_files(self):
        """
        TC 548
        Test the existing of modified files.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use hasModifiedFiles to check the output, should be True.
        #. Add those files and recheck again, the output should be false.
        """
        FILE_1, FILE_2 = self.create_two_files()

        self.info("Use hasModifiedFiles to check the output")
        self.assertTrue(self.GIT_CLIENT.hasModifiedFiles())

        self.info("Add those files {}, {}".format(FILE_1, FILE_2))
        self.GIT_CLIENT.commit()

        self.info("Check again after we add the files")
        self.assertFalse(self.GIT_CLIENT.hasModifiedFiles())

    def test011_patch_git_ignore(self):
        """
        TC 551
        Test patch gitignore file in git repo.

        **Test scenario**
        #. Make sure that .gitignore file doesn't exist.
        #. Use patchGitignore method and check if .gitignore file is created.
        """
        self.info("Make sure that .gitignore file doesn't exist")
        self.assertFalse(os.path.isfile("{}/.gitignore".format(self.GIT_REPO)))

        self.info("Use patchGitignore and check if .gitignore file is created")
        self.GIT_CLIENT.patchGitignore()
        self.assertTrue(os.path.isfile("{}/.gitignore".format(self.GIT_REPO)))

    # def test012_pull(self):
    #     """
    #     TC 552
    #     Test pull remote repo.
    #
    #     **Test scenario**
    #     #. Create 2 files, push them
    #     """

    # def test013_push(self):
    #     """
    #     TC 554
    #
    #     **Test scenario**
    #     #.
    #     """

    def test014_remove_files(self):
        """
        TC 555
        Test remove files from git repo.

        **Test scenario**
        #. Create two files in a git repo directory.
        #. Use removeFiles, and check if those files are deleted or not.
        #. Try to use removeFiles to check non existing file, should raise an error.
        """
        FILE_1, FILE_2 = self.create_two_files()

        self.GIT_CLIENT.addFiles([FILE_1, FILE_2])

        self.info("Use removeFiles, and check if those files are deleted or not")
        self.GIT_CLIENT.removeFiles([FILE_2])
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertNotIn("{}".format(FILE_1), output.decode())

        self.info("Try to use removeFiles to check non existing file")
        with self.assertRaises(Exception) as error:
            self.GIT_CLIENT.removeFiles(files=[self.RANDOM_NAME])
            self.assertTrue("did not match any files" in error.exception.args[0])

    def test015_setConfig_and_unset_config(self):
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

    def test016_set_remote_uRL(self):
        """
        """

    def test017_switch_branch(self, Branch_Name, Create_status):
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
            self.GIT_CLIENT.switchBranch(self.RANDOM_NAME, create=False)
            self.assertTrue("did not match any file(s) known to git" in error.exception.args[0])
