import datetime
from getpass import getpass
import os
import sys
import time

from progress.bar import Bar
import schedule
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import format_date
import sms

def main():

    global username
    global password
    global phone_number
    global reservations

    os.system("clear")
    username = input("Enter your HawkID: ")
    password = getpass("Enter your HawkID Password: ")
    validate_login()
    os.system("clear")
    print("Success!")
    
    phone_number = input("Enter your phone number: ")
    reservations = read_reservations()
    reserve_slot()
    
    '''schedule.every().day.at("00:05").do(reserve_slot)
    while True:
        schedule.run_pending()
        print("Sleeping...")
        time.sleep(45)
        os.system("clear")'''

def create_driver():

    cwd = os.path.abspath(os.getcwd())
    options = ChromeOptions()
    options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            executable_path=cwd + '/chromedriver', options=options)
    except Exception as error:
        print(error)

    return driver

def log_in(bar):
    
    driver = create_driver()
    driver.set_page_load_timeout(10)

    try: # Connect to website
        driver.get('https://connect.recserv.uiowa.edu/booking')
        bar.next()
    except Exception as error:
        raise_error(driver, bar, error)
    
    try: # Find main login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "loginLink")))
        login_button.click()
        bar.next()
    except Exception as error:
        raise_error(driver, bar, error)
    
    try: # Select "U Iowa" login option
        myui_login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@title='U Iowa Login']")))
        myui_login_button.click()
        bar.next()
    except Exception as error:
        raise_error(driver, bar, error)

    try: # Populate username and password fields
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "j_username")))
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "j_password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        bar.next()
    except Exception as error:
        raise_error(driver, bar, error)
    
    try: # Press the login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login")))
        login_button.click()
        bar.next()
    except Exception as error:
        raise_error(driver, bar, error)

    return driver

def raise_error(driver, bar, error):
    bar.finish()
    driver.quit()
    sys.exit(error)

def read_reservations():
    with open("reservations.txt") as file:
        lines = (line.rstrip() for line in file)
        lines = (line for line in lines if line)
        lines = (line for line in lines if not line.startswith("//"))
        lines = (line.split() for line in lines)
        lines = list(lines)

    reservations = {}

    for line in lines:
        data = {}
        data["time"] = f"{line[1]} - {line[2]} {line[3]}"
        data["location"] = line[4]

        reservations[line[0]] = data

    return reservations

def reserve_slot():

    print("Reserving slot...")
    bar = Bar("Progress:", max=13, fill="■", suffix="%(percent)d%%")

    driver = log_in(bar)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_data = reservations.get(tomorrow.strftime("%A"))

    try: # Find location option that matches desired location
        location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), '"
                + tomorrow_data.get("location") + "')]")))
        bar.next()
    except Exception as error:
        print("Exited find location")
        raise_error(driver, bar, error)

    try: # Click location option
        location_link = WebDriverWait(location, 10).until(
            EC.presence_of_element_located((By.XPATH, "./../../a")))
        driver.get(location_link.get_attribute("href"))
        bar.next()
    except Exception as error:
        print("Exited location option")
        raise_error(driver, bar, error)

    try: # Open data selection menu
        date_selection_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "spanSelectedDate")))
        date_selection_button.click()
        bar.next()
    except Exception as error:
        print("Exited selection menu")
        raise_error(driver, bar, error)

    try: # Select tomorrow's date
        selected_date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-date-text='"
                + format_date.for_fusion(tomorrow) + "']")))
        selected_date_button.click()
        bar.next()
    except Exception as error:
        print("Exited tomorrow")
        raise_error(driver, bar, error)

    try: # Confirm selection of date
        apply_selection_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@onClick='ApplySelectedDate()']")))
        apply_selection_button.click()
        bar.next()
    except Exception as error:
        print("Exited date")
        raise_error(driver, bar, error)

    try: # Locate desired time slot button
        slot = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//strong[contains(text(), '"
                + tomorrow_data.get("time") + "')]")))
        bar.next()
    except Exception as error:
        print("Exited desired")
        raise_error(driver, bar, error)

    try: # Click time slot button
        slot_button = WebDriverWait(slot, 10).until(
            EC.element_to_be_clickable((By.XPATH, "./../../div/button")))
        # slot_button.click()
        bar.next()
    except Exception as error:
        raise_error(driver, bar, error)

    # Send a confirmation text message to the user
    message_subject = "Reservation Confirmation"
    message_body = "Successfully booked slot from {} on {} at the {}!".format(
        tomorrow_data.get("time"), 
        format_date.for_sms(tomorrow),
        tomorrow_data.get("location"))
    if not sms.send_message(phone_number, message_subject, message_body):
        raise_error(driver, bar, error)

    bar.next()
    bar.finish()

    driver.quit()

def validate_login():
    print("Validating login data...")
    bar = Bar("Progress:", max=6, fill="■", suffix="%(percent)d%%")
    driver = log_in(bar)
    try: # Check if we landed on failed login page
        invalid_login = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[contains(text(), 'Invalid login')]")))
        raise_error(driver, bar, "Invalid login credentials")
    except TimeoutException:
        bar.next()
        bar.finish()
        driver.quit()
    except Exception as error:
        driver.quit()

if __name__ == "__main__":
    main()