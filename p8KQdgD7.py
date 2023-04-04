import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import telegram

#constants
game_names = []
counter = 0
email = "maurerdavid44@gmail.com"
password = "tO0DPQn#Y$sm8P4Z4cz7xqQQgOH4XE"
error_counter = 0
telegram_bot_token = "5921114141:AAHIMf7SaY6wrosrRb3RnmuIeV5uoy0guzs"
telegram_chat_id = "872788302"

#functions to use later
def get_xpath(elm):
    e = elm
    xpath = elm.tag_name
    while e.tag_name != "html":
        e = e.find_element(By.XPATH, "..")
        neighbours = e.find_elements(By.XPATH, "../" + e.tag_name)
        level = e.tag_name
        if len(neighbours) > 1:
            level += "[" + str(neighbours.index(e) + 1) + "]"
        xpath = level + "/" + xpath
    return "/" + xpath

def get_price_options(input_price):
    if input_price == 80:
        return ["80,00 €", "60,00 €", "50,00 €", "40,00 €", "15,00 €"]
    if input_price == 60:
        return ["60,00 €", "50,00 €", "40,00 €", "15,00 €"]
    if input_price == 50:
        return ["50,00 €", "40,00 €", "15,00 €"]
    if input_price == 40:
        return ["40,00 €", "15,00 €"]
    if input_price == 15:
        return ["15,00 €"]
    
def send_message(text):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_chat_id}&text={text}"
    requests.get(url)


def main():
    #starting on login page
    driver = uc.Chrome()
    driver.get("https://id.fcbayern.com/auth/realms/fcbayern/protocol/openid-connect/auth?client_id=fussball&response_type=code&scope=bpid&redirect_uri=https://tickets.fcbayern.com/internetverkaufzweitmarkt/login.aspx")

    #user log in and go to zweitmarkt page
    input("Please accept the cookies, then press enter...")
    driver.find_element(by=By.ID, value="username-container").send_keys(email)
    time.sleep(0.1)
    driver.find_element(by=By.ID, value="password-container").send_keys(password)
    time.sleep(0.1)
    driver.find_element(by=By.ID, value="rememberMe").click()
    time.sleep(0.1)
    driver.find_element(by=By.NAME, value="login").click()
    time.sleep(3)
    driver.find_element(by=By.ID, value="ctl00_ContentMiddle_SessionTimeoutInfo1_ToEventList").click()
    time.sleep(4)


    #getting game names
    def number_of_games_on_page():
        return driver.page_source.count("_EventImage")
    while True:
        if "Auswahl der Veranstaltung" in driver.page_source:
            print("Getting all available games...")
            #getting number of pages
            pages = driver.find_element(by=By.ID, value="ctl00_ContentMiddle_EventListImages1_GridView1_ctl08_lblPageInfo").text
            number_of_pages = int(pages[12:])
            for i in range(number_of_games_on_page()):
                game_names.append(driver.find_element(by=By.XPATH, value=f"/html/body/form/div[3]/div/div[2]/div/div/div/div[1]/div/table/tbody/tr[{i+3}]/td/div/div/div[2]/div[1]/strong/span").text)
            for i in range(number_of_pages-1):
                next_page = driver.find_element(by=By.ID, value="ctl00_ContentMiddle_EventListImages1_GridView1_ctl08_btnNextPage")
                next_page.click()
                time.sleep(3)
                for i in range(number_of_games_on_page()):
                    game_names.append(driver.find_element(by=By.XPATH, value=f"/html/body/form/div[3]/div/div[2]/div/div/div/div[1]/div/table/tbody/tr[{i+3}]/td/div/div/div[2]/div[1]/strong/span").text)
                back_to_page_1 = driver.find_element(by=By.ID, value=f"ctl00_ContentMiddle_EventListImages1_GridView1_ctl0{number_of_games_on_page()+4}_btnFirstPage")
                back_to_page_1.click()
                time.sleep(3)
            break
        else:
            input("Please first go on the Zweitmarkt page, then press enter...")

    #choosing a game
    print("Please choose a game by typing in its number:")

    for game in game_names:
        print(game + " -- " + str(game_names.index(game)+1))

    chosen_game_number = input("Game: ")

    while True:
        if True != chosen_game_number.isnumeric():
            chosen_game_number = input("Please type in a valid number: ")
        if int(chosen_game_number) < 0 or int(chosen_game_number) > len(game_names):
            chosen_game_number = input("Please type in a number that is connected to a game: ")
        if chosen_game_number.isnumeric():
            break
        
    chosen_game = str(game_names[int(chosen_game_number)-1])

    #checking if chosen game is on first page and clicking the game
    while True:
        if chosen_game[21:] in driver.page_source:
            chosen_game_name_element = driver.find_element(by=By.XPATH, value=f"//*[contains(text(), '{chosen_game[21:]}')]")
            chosen_game_name_element_xpath =  get_xpath(chosen_game_name_element)
            game_zweitmarkt_button_xpath = chosen_game_name_element_xpath[:-18] + "div[7]/div/a"
            try:    
                game_zweitmarkt_button = driver.find_element(by=By.XPATH, value=game_zweitmarkt_button_xpath)
                game_zweitmarkt_button.click()
            except:
                time.sleep(5)
                game_zweitmarkt_button = driver.find_element(by=By.XPATH, value=game_zweitmarkt_button_xpath)
                game_zweitmarkt_button.click()
            break
        else:
            driver.find_element(by=By.ID, value="ctl00_ContentMiddle_EventListImages1_GridView1_ctl08_btnNextPage").click()
            time.sleep(2)
            driver.refresh()
            time.sleep(2)
    time.sleep(7)
    #now on game page, asking for ticket price
    wanted_ticket_price = input("Enter the ticket price that you want to search for in €: ")
    while True:
        if True != wanted_ticket_price.isnumeric():
            wanted_ticket_price = input("Please enter a valid number: ")
        if int(wanted_ticket_price) != 60 or int(wanted_ticket_price) != 50 or int(wanted_ticket_price) != 80 or int(wanted_ticket_price) != 50 or int(wanted_ticket_price) != 40 or int(wanted_ticket_price) != 15:
            wanted_ticket_price = input("That is not a valid option (15, 40, 50, 60, 80): ")
        if wanted_ticket_price.isnumeric():
            break
    wanted_ticket_price = int(wanted_ticket_price)

    #purchase loop including page check
    print("Searching for tickets...")
    while True:
        driver.refresh()
        time.sleep(random.randint(10,15))
        if "Verfügbare Karten zur ausgewählten Veranstaltung" not in driver.page_source:
            counter += 1
            if counter > 3:
                error_counter += 1
                if error_counter >= 3:
                    send_message("An error has occured and the bot is paused. Please check on the bot and go on the desired ticket page to continue.")
                    input("An error occured, please make sure that the browser is on the desired ticket page, press enter to continue...")
                    error_counter = 0
                    counter = 0
            time.sleep(15)
        counter = 0
        for price in reversed(get_price_options(wanted_ticket_price)):
            wanted_price_with_euro = str(price)
            if wanted_price_with_euro in driver.page_source:
                price_elements_with_wanted_price = driver.find_element(by=By.XPATH, value=f"//*[contains(text(), '{wanted_price_with_euro}')]")
                if type(price_elements_with_wanted_price) == list:
                    for element in price_elements_with_wanted_price:
                        wanted_xpath_purchase = str(get_xpath(element))[:-15] + "2]/span/a"
                        kaufen_button = driver.find_element(by=By.XPATH, value=wanted_xpath_purchase)
                        kaufen_button.click()
                        time.sleep(0.15)
                else:
                    wanted_xpath_purchase = str(get_xpath(price_elements_with_wanted_price))[:-15] + "2]/span/a"
                    kaufen_button = driver.find_element(by=By.XPATH, value=wanted_xpath_purchase)
                    kaufen_button.click()
                    time.sleep(0.1)
                    kaufen_button.click()
                    time.sleep(0.1)
                    kaufen_button.click()
                send_message("There is/are ticket/-s available. Check now!")
                if "Kein Warenkorb vorhanden" not in driver.page_source or "Position(en)" in driver.page_source:
                    for i in range(5):
                        send_message("TICKET IM WARENKORB!!!!!!")
                if price == "80,00 €":
                    input("Press enter to continue...")
if __name__ == '__main__':
   try:
       main()
   except:
       send_message("THE SCRIPT CRASHED! CHECK NOW!")