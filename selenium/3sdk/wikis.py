import requests
import os
import random
import subprocess
import time

from Jumpscale import j
from selenium import webdriver


wikis_url = "http://172.17.0.2/wiki/"
card = ""


def info(message):
    j.tools.logger._log_info(message)


def find_wiki_example_card():
    global card
    for i in range(len(driver.find_elements_by_class_name("card-title"))):
        if driver.find_elements_by_class_name("card-title")[i].text == 'zerobot.wiki_examples':
            card = driver.find_elements_by_class_name("card-title")[i]
    return card


def os_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, error = process.communicate()
    return output, error


def set_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080'")
    driver = webdriver.Chrome(options=options)
    return driver


def get_page(driver, page_url):
    try:
        driver.get(page_url)
    except Exception as e:
        info(" * %s Exception at get_page(%s) " % (str(e), page_url))
    else:
        maximize_window(driver)


def maximize_window(driver):
    time.sleep(1)
    screen_dimention = driver.get_window_size()
    screen_size = screen_dimention["width"] * screen_dimention["height"]
    if screen_size < 1800 * 1000:
        driver.set_window_size(1800, 1000)


def load_wikis():
    gedis_client = j.clients.gedis.get(
        name="test_wiki", host="127.0.0.1", port=8901, package_name="zerobot.packagemanager"
    )
    gedis_client.actors.package_manager.package_add(
        path=j.core.tools.text_replace(
            "{DIR_BASE}/code/github/threefoldtech/jumpscaleX_threebot/ThreeBotPackages/zerobot/wiki_examples"
        )
    )
    time.sleep(20)


driver = set_browser()


def before_all():
    os_command("eval `ssh-agent -s` && ssh-add /{}/.ssh/id_rsa".format(os.environ['HOME']))
    j.servers.threebot.start(background=True)
    load_wikis()


def before():
    global driver
    driver = set_browser()
    info("Get wikis page")
    get_page(driver, wikis_url)
    assert "Home" in driver.title


def after():
    driver.close()


def after_all():
    j.sal.process.killall("tmux")


def test001_test_view_button():
    """
    Test case for checking view button.

    **Test scenario**
    #. Get wikis page.
    #. Click view button , should be found.
    #. Check that view button works successfully and redirect to right wikis files.
    """
    info("Click view button")
    cards = driver.find_elements_by_class_name("card-title")
    random_card = random.choice(cards)

    card_name = random_card.find_element_by_class_name("card-title").text

    random_card.find_element_by_link_text("View").click()

    info("Check that view button works successfully and redirect to right wikis files")
    assert driver.current_url == "{}/{}#".format(wikis_url, card_name)


def test002_test_reload_button():
    """
    Test case for checking reload button.

    **Test scenario**
    #. Get wikis page.
    #. Create new file in wikis_example directory.
    #. Click reload button in wikis_example wiki, should succeed.
    #. Click view button.
    #. Check that sidebar is changed.
    """

    info("Change in sidebar in wiki_example page")
    with open("/sandbox/var/docsites/zerobot.wiki_examples/test_wiki_reload.md", "a") as test_wiki:
        test_wiki.write("test wiki reload")

    with open("/sandbox/var/docsites/zerobot.wiki_examples/_sidebar.md", "a") as sidebar:
        sidebar.write("* [Test wiki reload](test_wiki_reload.md)")

    info("Click reload button in wikis_example wiki, should succeed")

    wiki_example_card = find_wiki_example_card()
    wiki_example_card.find_element_by_xpath("/html/body/div/div/div/div[2]/div/ul/li[6]/div/div/div/a[2]").click()

    info("Click view button")
    wiki_example_card.find_element_by_link_text("View").click()

    info("Check that sidebar is changed")
    wiki_reload_page = requests.get("http://172.17.0.2/wiki/zerobot.wiki_examples#/test_wiki_reload")
    assert wiki_reload_page.status_code == 200


def test003_test_pull_button():
    """
    Test case for checking pull button.

    **Test scenario**
    #. Get wikis page.
    #. Change the current commit id to an older one.
    #. Click pull button.
    #. Check that the latest changed is pulled.
    
    """
    info("Change the current commit id to an older one")
    GIT_REPO = "/sandbox/code/github/threefoldtech/jumpscaleX_threebot"
    older_commit_id = os_command("cd {} && git log -4 | grep commit | tail -1 | cut -d " " -f 2".format(GIT_REPO))
    os_command("cd {} && git reset --soft {}".format(GIT_REPO, older_commit_id))

    info("Click pull button")
    wiki_example_card = find_wiki_example_card()
    wiki_example_card.find_element_by_xpath("/html/body/div/div/div/div[2]/div/ul/li[6]/div/div/div/a[3]").click()

    info("Check that the latest changed is pulled")
    current_commit_id = os_command("cd {} && git rev-parse HEAD".format(GIT_REPO))
    assert current_commit_id != older_commit_id


def test004_test_wiki_example():
    """
    Test case for github icon in wiki_examples.

    **Test scenario**
    #. Get wiki page.
    #. Click view button on web_examples wiki.
    #. Click github icon in the top right.
    #. Check that github icon forwards to jumpscaleX_threebot repo.
    #. Test wiki_example readme.
    """
    info("Click view button on web_examples wiki")
    wiki_example_card = find_wiki_example_card()
    wiki_example_card.find_element_by_link_text("View").click()

    info("Click github icon in the top right")
    wiki_example_card.find_element_by_class_name("github-corner").click()

    info("Check that github icon forwarded to jumpscaleX_threebot repo")
    assert driver.current_url == "https://github.com/threefoldtech/jumpscaleX_threebot"

    info("Test wiki_example readme")
    url = 'http://172.17.0.2/wiki/zerobot.wiki_examples#/'
    driver.get(url)
    assert driver.find_element_by_class_name("markdown-section").text == "test wikis file"

