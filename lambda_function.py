import json
import os
import requests
import smtplib
from dotenv import load_dotenv
from datetime import datetime, timedelta

from requests.auth import HTTPBasicAuth

load_dotenv()

# Sheety configurations
SHEETY_BA_UNAME = os.environ.get("SHEETY_BA_UNAME")
SHEETY_BA_PASS = os.environ.get("SHEETY_BA_PASS")
SHEETY_AUTH = HTTPBasicAuth(SHEETY_BA_UNAME, SHEETY_BA_PASS)
SHEETY_SCHEDULE_ENDPOINT = "https://api.sheety.co/a3d35913087e197134de6e63c1bdf81d/roboticsMentorSchedule20242025/schedule"

# Google email configurations
GOOGLE_APP_PASSWORD = os.environ.get("GOOGLE_APP_PASSWORD")
MY_EMAIL = "paul.d.johansen@gmail.com"
TO_EMAIL = "paul.d.johansen@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SUBJECT = "Upcoming Robotics Mentoring Session"

# App Configurations
DAYS_TO_LOOK_AHEAD = 7

# Mentor Information
mentors = {
    "leAnneJohansen": {"FirstName": "LeAnne", "LastName": "Johansen", "Email": "leannejohansen@hotmail.com"},
}


def send_notification(people_to_notify, day, date, meeting_time):
    for person in people_to_notify:
        mentor = mentors[person]
        message_content = (
            f"{mentor["FirstName"]},\n\nYou are scheduled to be a mentor on {day} {date} from {meeting_time}. "
            f"Please let LeAnne Johansen (leannejohansen@hotmail.com or 507-327-9096) know if you have any conflicts.")
        with smtplib.SMTP(SMTP_HOST, port=SMTP_PORT) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=GOOGLE_APP_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=mentor["Email"],
                msg=f"Subject:{SUBJECT}\n\n{message_content}")


def get_schedule_data():
    current_date = datetime.today().date()
    notification_date = current_date + timedelta(days=DAYS_TO_LOOK_AHEAD)
    url = f"{SHEETY_SCHEDULE_ENDPOINT}?filter[date]={notification_date.strftime("%m-%d-%y")}"
    response = requests.get(url, auth=SHEETY_AUTH)
    data = response.json()
    schedule = data.get('schedule', [])
    for event in schedule:
        people_to_notify = []
        for key, value in event.items():
            if value == "Yes":
                people_to_notify.append(key)

        if len(people_to_notify) > 0:
            send_notification(people_to_notify, event["day"], event["date"], event["meetingTimeToCover"])


def lambda_handler(event, context):
    get_schedule_data()
