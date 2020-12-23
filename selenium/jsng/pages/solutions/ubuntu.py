import os
from gevent import sleep
from urllib.parse import urljoin
from tests.frontend.pages.base import Base
from selenium.webdriver.common.keys import Keys


class Ubuntu(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/solutions"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    def switch_driver_to_iframe(self):
        # switch driver to iframe
        self.wait(self.driver, "v-progress-linear__buffer")
        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to_frame(iframe)

    def find(name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def view_my_workload_button(self):
        self.load()
        network_card = self.driver.find_elements_by_class_name("ma-2")[1]
        my_workloads_button = network_card.find_elements_by_class_name("v-btn")[1]
        my_workloads_button.click()

    def deploy_ubuntu_solution(self, ubuntu_instance_name, solution_name):
        ubuntu_card = self.driver.find_elements_by_class_name("ma-2")[1]
        new_button = ubuntu_card.find_elements_by_class_name("v-btn")[0]
        new_button.click()

        # Switch iframe
        self.switch_driver_to_iframe()

        # Input ubuntu_solution name
        name_box = self.driver.find_element_by_tag_name("input")
        name_box.send_keys(ubuntu_instance_name)

        # Click Next
        self.click_button(self.driver, "NEXT")

        # Choose ubuntu version (Ubuntu 18.04)
        self.driver.find_elements_by_class_name("v-radio")[0].click()

        # Click Next
        self.click_button(self.driver, "NEXT")
        self.click_button(self.driver, "NEXT")

        # Choose a pool

        # open the pools list
        chat_box = self.driver.find_element_by_class_name("chat")
        form = chat_box.find_element_by_class_name("v-form")
        open_list = form.find_element_by_tag_name("i")
        open_list.click()
        pools_menu = self.driver.find_element_by_class_name("v-menu__content")
        pools_list = pools_menu.find_element_by_class_name("v-list")
        # Load all pools and select the pool
        for _ in range(30):
            pools_list.send_keys(Keys.END)
            sleep(0.5)
        pools = pools_list.find_elements_by_class_name("v-list-item__content")
        for pool in pools:
            if name in pool.text:
                pool.click()
                break

        # Click Next
        self.click_button(self.driver, "NEXT")

        # Select a network
        networks = self.driver.find_elements_by_class_name("v-radio")
        for network in networks:
            if network.text == solution_name:
                network.click()
                break

        # Click Next
        self.click_button(self.driver, "NEXT")
        self.click_button(self.driver, "NEXT")

        # Access key
        # Find sshkey file path
        sshkey_path = find("id_rsa.pub", "/")
        file_input = self.driver.find_element_by_tag_name("input")
        file_input.send_keys(sshkey_path)

        self.click_button(self.driver, "NEXT")
        self.click_button(self.driver, "NEXT")
        self.click_button(self.driver, "NEXT")

        # Wait for 2 mins
        self.wait(self.driver, "v-progress-circular")

        self.click_button(self.driver, "NEXT")

        # Wait for 2 mins
        self.wait(self.driver, "v-progress-circular")

        # Find ubuntu machine IP
        text = self.driver.find_element_by_class_name("chat").text
        ip = text.splitlines()[3].split()[-1]

        self.click_button(self.driver, "FINISH")

        return ip

    def view_my_ubuntu_workloads(self):
        self.view_my_workload_button()

        # Add some wait
        self.wait(self.driver, "progressbar")

        # List network instances
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")

        my_ubuntu_instances = []
        for row in rows:
            my_ubuntu_instances.append(row.text)

        return my_ubuntu_instances

    def delete_my_ubuntu_workload(self, ubuntu_solution_name):
        self.view_my_workload_button()

        # Add some wait
        self.wait(self.driver, "progressbar")

        # List network instances
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")

        for row in rows:
            if row.text == ubuntu_solution_name:
                row.find_element_by_class_name("v-btn__content").click()
                break
        else:
            return

        self.click_button(self.driver, "DELETE RESERVATION")

        self.click_button(self.driver, "CONFIRM")
