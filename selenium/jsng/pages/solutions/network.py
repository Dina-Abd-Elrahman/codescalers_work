from urllib.parse import urljoin
from tests.frontend.pages.base import Base


class Network(Base):
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

    def view_my_workload_button(self):
        self.load()
        network_card = self.driver.find_elements_by_class_name("ma-2")[0]
        my_workloads_button = network_card.find_elements_by_class_name("v-btn")[1]
        my_workloads_button.click()

    def deploy_network_solution(self, network_solution_name):
        network_card = self.driver.find_elements_by_class_name("ma-2")[0]
        new_button = network_card.find_elements_by_class_name("v-btn")[0]
        new_button.click()

        # Switch iframe
        self.switch_driver_to_iframe()

        # Choose create network and click next
        self.click_button(self.driver, "NEXT")

        name_box = self.driver.find_element_by_tag_name("input")
        name_box.send_keys(network_solution_name)

        self.click_button(self.driver, "NEXT")
        self.wait(self.driver, "progressbar")

        # Choose ip range for me
        self.click_button(self.driver, "NEXT")

        # Choose ipv4
        self.click_button(self.driver, "NEXT")

        # Select node access automatically
        self.click_button(self.driver, "NEXT")

        self.wait(self.driver, "v-progress-linear__buffer")
        # Click finish button
        self.click_button(self.driver, "FINISH")

    def view_my_workloads(self):

        self.view_my_workload_button()

        # Add some wait
        self.wait(self.driver, "progressbar")

        # List network instances
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")

        my_network_instances = []
        for row in rows:
            my_network_instances.append(row.text)

        return my_network_instances

    def delete_network_workload(self, network_solution_name):

        self.view_my_workload_button()

        # Add some wait
        self.wait(self.driver, "progressbar")

        # List network instances
        table_box = self.driver.find_element_by_class_name("v-data-table")
        table = table_box.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")

        for row in rows:
            if row.text == network_solution_name:
                row.find_element_by_class_name("v-btn__content").click()
                break
        else:
            return

        self.click_button(self.driver, "DELETE RESERVATION")

        self.click_button(self.driver, "CONFIRM")
