from urllib.parse import urljoin
from tests.frontend.pages.base import Base
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Packages(Base):
    def __init__(self, driver, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.driver = driver
        self.endpoint = "/admin/#/packages"

    def load(self):
        url = urljoin(self.base_url, self.endpoint)
        self.driver.get(url)

    # def packages_category(self):
    #     packages_category = self.driver.find_elements_by_class_name("subtitle-1")
    #     categories = []
    #     for i in range(3):
    #         categories.append(packages_category[i].text)
    #     return categories

    def system_packages(self):
        packages = self.driver.find_elements_by_class_name("v-card__title")
        system_packages = []
        for i in range(6):
            system_packages.append(packages[i])
        return system_packages

    def add_package(self, git_url):
        buttons = self.driver.find_elements_by_class_name("v-btn")
        add_button = [button for button in buttons if button.text == "ADD"][0]
        add_button.click()
        add_new_package_box = self.driver.find_elements_by_class_name("v-text-field__slot")
        git_url_input = add_new_package_box[1].find_element_by_tag_name("input")
        git_url_input.send_keys(git_url)
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "v-dialog")))

    def check_package_card(self, packages_type):
        packages = {}
        packages_class = self.driver.find_elements_by_class_name("row")
        if packages_type is "installed":
            i = 1
        else:
            i = 2
        packages_cards = packages_class[i].find_elements_by_class_name("v-card")
        for package_card in packages_cards:
            package_card_name = package_card.find_element_by_class_name
            packages_name = package_card_name.text
            packages[packages_name] = package_card
        return packages

    def delete_package(self, package_name):
        packages = self.check_package_card("installed")
        for package in packages.keys():
            if package == package_name:
                package_card = packages[package_name]
                delete_icon = package_card.find_elements_by_class_name("v-btn")
                delete_icon[0].click()
                break
            else:
                return
        buttons = self.driver.find_elements_by_class_name("v-btn")
        submit_button = [button for button in buttons if button.text == "SUBMIT"][0]
        submit_button.click()
