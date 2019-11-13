import os
import git
import uuid

from Jumpscale import j
from base_test import BaseTest
from parameterized import parameterized


class TestGitClient(BaseTest):
    GIT_REPO = "/tmp/test_tft/code/test/tfttesting/git_client_test"

    @classmethod
    def setUpClass(cls):
        cls.info("create a git repo directory")
        cls.os_command("mkdir -p {}".format(cls.GIT_REPO))

        cls.info("change directory to {}".format(cls.GIT_REPO))
        cls.info("Initialized empty Git repository")

        cls.os_command("cd {} && git init".format(cls.GIT_REPO))

        cls.info("create a git client")
        cls.GIT_CLIENT = j.clients.git.get("{}".format(cls.GIT_REPO))

    def setUp(self):
        print('\t')
        self.info('Test case : {}'.format(self._testMethodName))

    @classmethod
    def tearDownClass(cls):
        cls.info("remove git repo directory")
        cls.os_command("rm -rf /tmp/test_tft/")

        cls.info("remove git client")

    def test001_addfiles__with_exists_file_list(self):
        """
        TC 480
        Test case for addfiles method in git client with exists files, should pass.

        **Test scenario**
        #. create two files in /tmp/test/code/test/tfttesting/git_client_test directory.
        #. use addfiles method to add those two files.
        #. use (git ls-files) to check that files are added correctly.
        """

        self.info("create two files in git repo")
        self.os_command("cd {} && touch test_1 test_2".format(self.GIT_REPO))

        self.info("use addFiles method to add files")
        self.GIT_CLIENT.addFiles(files=["test_1", "test_2"])

        self.info("check the files is added or not using (git ls-files) command")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("test_1\ntest_2", output.decode())

    def test002_addfiles_with_non_exists_file_list(self):
        """
        TC 481
        Test case for addfiles method in git client with non exists file list, should fail.

        **Test scenario**
        #. use addfiles method to add those two non exists files, should raise exception error.
        """

        self.info("use addFiles method to add files non exists files, should raise an error")
        with self.assertRaises(Exception):
            self.GIT_CLIENT.addFiles(files=["test_3", "test_4"])

    def test003_addFiles_add_some_files(self):
        """
        TC 483
        Test Case for addfiles method in git client to add some files.

        **Test scenario**
        #. create 4 files in /tmp/test/code/test/tfttesting/git_client_test directory.
        #. use addfiles method to add two files.
        #. use (git ls-files) to check that files are added correctly.
        """
        self.info("create two files in git repo")
        self.os_command("cd {} && touch test_1 test_2 test_3 test_4".format(self.GIT_REPO))

        self.info("use addFiles method to add files")
        self.GIT_CLIENT.addFiles(files=["test_2", "test_4"])

        self.info("check the files is added or not using (git ls-files) command")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("test_2\ntest_4", output.decode())

    def test004_addRemoveFiles(self):
        """
        TC 484
        Test Case for addfiles method in git client to add some files.

        **Test scenario**
        #. create 4 files in /tmp/test/code/test/tfttesting/git_client_test directory.
        #. use addRemoveFiles method to add all files.
        #. use (git ls-files) to check that files are added correctly.
        """
        self.info("create two files in git repo")
        self.os_command("cd {} && touch test_1 test_2 test_3 test_4".format(self.GIT_REPO))

        self.info("use addFiles method to add files")
        self.GIT_CLIENT.addRemoveFiles()

        self.info("check the files is added or not using (git ls-files) command")
        output, error = self.os_command("cd {} && git ls-files".format(self.GIT_REPO))
        self.assertIn("test_1\ntest_2\ntest_3\ntest_4", output.decode())


    # def test002_find(self):
    #     """
    #     TC386
    #     Test case for find method in git client
    #     find the list of repos locations in you system
    #     the output will be like this:
    #     ['github', organization, repo_name, repo_path]
    #     TODO: will make parametrized with the organization name, try to find better way to check the output
    #     **Test scenario**
    #     #. check the output of find method in git client
    #     """
    #     self.info(
    #         "find the list of repos locations in you system the output will be like this: ['github', organization, repo_name, repo_path]"
    #     )
    #     result_gitclient = j.clients.git.find()
    #     self.assertIn("jumpscaleX_core", result_gitclient)
    #
    # def test001_currentdir_gitrepo(self):
    #     """TC383
    #     Test case for currentDirGitRepo method in git client
    #     **Test scenario**
    #     #. cd to /sandbox/code/github/threefoldtech/jumpscaleX_core/
    #     #. create git client and save it.
    #     #. check that gitclient BASEDIR is /sandbox/code/github/threefoldtech/jumpscaleX_core/
    #     #. check that gitclient account is threefoldtech
    #     #. check that gitclient branchName is the same as the current branch
    #     #. check that gitclient name is jumpscaleX_core
    #     """
    #     currentDirectory = os.getcwd()
    #     self.info("cd to /sandbox/code/github/threefoldtech/jumpscaleX_core/")
    #     os.chdir('/sandbox/code/github/threefoldtech/jumpscaleX_core/')
    #     self.info("create git client and save it")
    #     gitclient = j.clients.git.currentDirGitRepo()
    #     gitclient.save()
    #     self.info("check gitclient BASEDIR")
    #     self.assertEqual('/sandbox/code/github/threefoldtech/jumpscaleX_core', gitclient.BASEDIR)
    #     self.info("check gitclient account")
    #     self.assertEqual('threefoldtech', gitclient.account)
    #     self.info("check gitclient branch")
    #     branch_name = self.check_branch()
    #     self.assertEqual(branch_name, gitclient.branchName)
    #     self.info("check gitclient name")
    #     self.assertEqual('jumpscaleX_core', gitclient.name)
    #     os.chdir(currentDirectory)
    #
    # @parameterized.expand(
    #     [
    #         ("/test_gitclient/",),
    #         ("/sandbox/code/github/threefoldtech/jumpscaleX_core/JumpscaleCore/clients/git/",)
    #     ]
    # )
    # def test003_find_gitpath(self, path):
    #     """
    #     TC384
    #     Test case for findGitPath method in git client
    #     findGitPath check if this path or any of its parents is a git repo,
    #                 return the first git repo
    #     TODO: will be paramterized with True and False.
    #     **Test scenario**
    #     #. check the findGitPath method with two input for path option
    #     #. print an error with /test_gitclient/
    #     #. print ( /sandbox/code/github/threefoldtech/jumpscaleX_core/ ) for another input
    #     """
    #     self.info("check the findGitPath method with two input for path option")
    #     self.info("print an error with /test_gitclient/ input")
    #     if path == "/test_gitclient/":
    #         try:
    #             j.clients.git.findGitPath(path)
    #         except EXCEPTION as err:
    #             self.fail(err)
    #     else:
    #         self.info(
    #             "print /sandbox/code/github/threefoldtech/jumpscaleX_core/ for the other input"
    #         )
    #         result = j.clients.git.findGitPath(path)
    #         self.assertEqual(result, "/sandbox/code/github/threefoldtech/jumpscaleX_core/")
    #
    # def test004_get_currentbranch(self):
    #     """
    #     TC385
    #     Test case for getCurrentBranch method in git client
    #     **Test scenario**
    #     #. check the branch name in /sandbox/code/github/threefoldtech/jumpscaleX_core/ repo
    #     """
    #     self.info("check the branch name in /sandbox/code/github/threefoldtech/jumpscaleX_core/ repo")
    #     gitclient_currentbranch = j.clients.git.getCurrentBranch("/sandbox/code/github/threefoldtech/jumpscaleX_core/")
    #     branch_name = self.check_branch()
    #     self.assertEqual(gitclient_currentbranch, branch_name)
    #
    # def test005_getgit_reposlist_local(self):
    #     """
    #     TC387
    #     Test case for getGitReposListLocal method in git client
    #     find the list of repos locations in you system
    #     the output will be like this:
    #     [repo_name, repo_path]
    #     TODO: add parametrized for provider, account, name, and errorIfNone
    #     **Test scenario**
    #     #. check the output of getGitReposListLocal method in git client
    #     """
    #     self.info("find the list of repos locations in you system the output will be like this: [repo_name, repo_path]")
    #     getreposlist = j.clients.git.getGitReposListLocal()
    #     self.assertIn("/sandbox/code/github/threefoldtech/jumpscaleX_core", getreposlist)
    #
    # def test006_pull_git_repo(self):
    #     """
    #     TC393
    #     Test case for pullGitRepo method in git client
    #     TODO: will add the depth option but trying to find good way to code it
    #     **Test scenario**
    #     #. try pullGitRepo with dest option /tmp/test_gitclient/
    #         && and with url option (https://github.com/threefoldtech/jumpscaleX_threebot.git)
    #     #. check that the repo in /tmp/test_gitclient/ directory.
    #     """
    #     self.info("try pullGitRepo with dest option /tmp/test_gitclient/ and threebot repo as a url")
    #     j.clients.git.pullGitRepo(
    #         dest="/tmp/test_gitclient/", url="https://github.com/threefoldtech/jumpscaleX_core.git")
    #     self.info("check that the repo in /tmp/test_gitclient/ directory")
    #     output, error = self.os_command("git status")
    #     self.assertFalse(error)
    #     self.assertIn("nothing to commit, working tree clean", output.decode())
    #
    # def test007_update_git_repos(self):
    #     """
    #     TC394
    #     Test case for updateGitRepos method in git client
    #     **Test scenario**
    #     #. clone a repo in /sandbox/code/github/tfttesting/ directory.
    #     #. create a file with a random name in git directory.
    #     #. use updateGitRepos to add and commit this file with certain commit message.
    #     #. check the latest commit on this repo make sure it's the same as the FILE_NAME.
    #     """
    #     self.info("clone a repo in /sandbox/code/github/tfttesting/ directory")
    #     git.Repo.clone_from("https://github.com/tfttesting/updateGitRepos.git", "/sandbox/code/github/tfttesting/")
    #
    #     self.info("create a file with a random name in git directory")
    #     FILE_NAME = str(uuid.uuid4()).replace("-", "")[:10]
    #     with open('/sandbox/code/github/tfttesting/{}.txt'.format(FILE_NAME), 'w') as f:
    #         data = 'this is new file {}'.format(FILE_NAME)
    #         f.write(data)
    #
    #     self.info("use updateGitRepos to add and commit this file with certain commit message")
    #     j.clients.git.updateGitRepos(provider='github', account='tfttesting', name='updateGitRepos',
    #                                  message='adding file {}'.format(FILE_NAME))
    #
    #     self.info("check the latest commit on this repo make sure it's the same as the FILE_NAME")
    #     repo = git.Repo("/sandbox/code/github/tfttesting/")
    #     commits = repo.head.log()
    #     latest_commit = str(commits[-1]).split("commit: ")[-1].replace("\n", "")
    #
    #     self.assertEqual("adding file {}".format(FILE_NAME), latest_commit)
