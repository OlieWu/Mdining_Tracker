import requests
import smtplib
import os
from bs4 import BeautifulSoup
from email.message import EmailMessage
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

sender_email = os.getenv('ADMIN_EMAIL')
sender_password = os.getenv('ADMIN_PASSWORD')
receive_email =  os.getenv('RECEIVE_PASSWORD')

# URL of the webpage you want to scrape
url = 'https://dining.umich.edu/menus-locations/dining-halls/'
urls = ['https://dining.umich.edu/menus-locations/dining-halls/' + s for s in ["Bursley", "East Quad", "Markley", "Mosher-Jordan", "North Quad", "South Quad", "Twigs at Oxford"]]

# add more emails and it will send seperate messages to all emails
emails = [receive_email]

def send_email(msg):
# Function to send emails
    for email in emails:    
        message = EmailMessage()
        message['Subject'] = "Chocolate Chunk Cookies Found!"
        message['From'] = sender_email
        message['To'] = email
        message.set_content(msg)
        server = None
        # Connect to the SMTP server and send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()

found = False
msg = ""

# this web scraper is unique to UofM's dining website
# change where you look for content in regards to what site you are looking on

for url in urls:
    try:
        print("Start")
        # Send a GET request to the URL
        response = requests.get(url, verify=False)
        print("Good response")
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the HTML content
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find all divs with class="courses"
            courses_divs = soup.find_all('div', class_='courses')
            # Iterate through each courses div
            for courses_div in courses_divs:
                # Find the preceding h3 tag
                preceding_h3 = courses_div.find_previous_sibling('h3')
                # Check if the preceding_h3 contains "Breakfast"
                if preceding_h3 and 'Dinner' in preceding_h3.get_text():
                    # Find all ul tags with class="courses_wrapper" within courses_div
                    courses_wrapper_uls = courses_div.find_all('ul', class_='courses_wrapper')
                    # Get the last courses_wrapper_ul (Mbakery should be the last item)
                    last_courses_wrapper_ul = courses_wrapper_uls[-1] if courses_wrapper_uls else None
                    if last_courses_wrapper_ul:
                        # Find all li items within the last courses_wrapper_ul
                        li_items = last_courses_wrapper_ul.find_all('li')
                        if li_items:
                            for li_item in li_items:
                                if ('Chocolate Chunk Cookies' in li_item.get_text()):
                                    print("Chocolate Chunk Cookies found!")
                                    msg += f"Chocolate Chunk Cookies have been found at {url.split('/')[-1]}!\n"
                                    found = True
                                    break
                        else: 
                            print("no li_items")
        else:
            print(f"Failed to fetch the webpage. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
# If no cookies were found in all dining halls
if not found:
    send_email("No dining halls with cookies :(")
else:
    send_email(msg)
