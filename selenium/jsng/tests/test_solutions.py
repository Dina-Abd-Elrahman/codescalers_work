import pytest
import subprocess
from random import randint
from jumpscale.loader import j
from tests.frontend.tests.base_tests import BaseTest
from tests.frontend.pages.solutions.ubuntu import Ubuntu
from tests.frontend.pages.solutions.network import Network
from solutions_automation.dashboard_solutions.pools import PoolAutomated
from solutions_automation.dashboard_solutions.network import NetworkDeployAutomated


@pytest.mark.integration
class SolutionsTests(BaseTest):

    solution_name = "solution{}".format(randint(1, 5000))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        j.clients.stellar.create_testnet_funded_wallet(cls.solution_name)

    def setUp(self):
        super().setUp()
        NetworkDeployAutomated(
            solution_name=self.solution_name,
            type="Create",
            ip_version="IPv4",
            ip_select="Choose ip range for me",
            ip_range="",
            access_node="choose_random",
            pool="choose_random",
            debug=True,
        )

        PoolAutomated(
            type="create",
            solution_name=self.solution_name,
            wallet_name=self.solution_name,
            farm="choose_random",
            cu=1,
            su=1,
            time_unit="Day",
            time_to_live=1,
            debug=True,
        )

    @classmethod
    def tearDownClass(cls):
        j.clients.stellar.delete(cls.solution_name)
        super().tearDownClass()

    @staticmethod
    def os_command(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, error = process.communicate()
        return output, error

    def test01_deploy_and_delete_network_solution(self):
        """
        Test case for deploying network solution.
        **Test Scenario**

        #. Deploy network solution instance.
        #. Check that network workload has been deployed successfully.
        #. Delete the network solution instance.
        #. Check that network workload has been deleted successfully.
        """

        self.network = Network(self.driver)
        self.network.load()

        self.info("Deploy network solution instance")

        network_name = "network{}".format(randint(1, 500))
        self.network.deploy_network_solution(network_name)

        self.info("Check that network workload has been deployed successfully")
        my_network_instances = self.network.view_my_workloads()

        self.assertIn(network_name, my_network_instances)

        self.info("Delete the network solution instance")
        self.network.delete_network_workload(network_name)

        self.info("Check that network workload has been deleted successfully")
        my_network_instances = self.network.view_my_workloads()
        self.assertNotIn(network_name, my_network_instances)

    def test02_deploy_and_delete_ubuntu_solution(self):
        """
        Test case for deploying ubuntu solution.
        **Test Scenario**

        #. Deploy ubuntu solution instance.
        #. Check that ubuntu workload has been deployed successfully.
        #. Delete the ubuntu solution instance.
        #. Check that ubuntu workload has been deleted successfully.
        """

        self.ubuntu = Ubuntu(self.driver)
        self.ubuntu.load()

        self.info("Deploy ubuntu solution instance")
        ubuntu_instance_name = "ubuntu{}".format(randint(1, 500))
        ubuntu_instance_ip = self.ubuntu.deploy_ubuntu_solution(ubuntu_instance_name, self.solution_name)

        self.info("Check that ubuntu workload has been deployed successfully")
        output, error = self.os_command('ssh {} "cat /etc/issue"'.format(ubuntu_instance_ip))
        self.assertIn("Ubuntu 18.04", output.decode())

        my_ubuntu_instances = self.ubuntu.view_my_ubuntu_workloads()
        self.assertIn(ubuntu_instance_name, my_ubuntu_instances)

        self.info("Delete the ubuntu solution instance")
        self.ubuntu.delete_my_ubuntu_workload(my_ubuntu_instances)

        self.info("Check that ubuntu workload has been deleted successfully")
        my_ubuntu_instances = self.ubuntu.view_my_ubuntu_workloads()
        self.assertNotIn(my_ubuntu_instances, my_ubuntu_instances)
