from .handle import NotificationHandle
from CEACStatusBot.request import query_status
from CEACStatusBot.captcha import CaptchaHandle,OnnxCaptchaHandle

class NotificationManager():
    def __init__(self,location:str,number:str,passport_number:str,surname:str,captchaHandle:CaptchaHandle=OnnxCaptchaHandle("captcha.onnx")) -> None:
        self.__handleList = []
        self.__location = location
        self.__number = number
        self.__captchaHandle = captchaHandle
        self.__passport_number = passport_number
        self.__surname = surname

    def addHandle(self, notificationHandle:NotificationHandle) -> None:
        self.__handleList.append(notificationHandle)

    def send(self,) -> str:
        import os
        import re
        last_state = os.getenv("LAST_STATE", "")

        res = query_status(self.__location, self.__number, self.__passport_number, self.__surname, self.__captchaHandle)

        current_state = re.sub(r'[^a-zA-Z0-9]', '_', f"{res['status']}:{res['case_last_updated']}:{res['description']}")

        if current_state == last_state:
            print("State has not changed. Skipping notification.")
            return last_state

        if res['status'] == "Refused":
            import pytz, datetime
            try:
                TIMEZONE = os.environ["TIMEZONE"]
                localTimeZone = pytz.timezone(TIMEZONE)
                localTime = datetime.datetime.now(localTimeZone)
            except pytz.exceptions.UnknownTimeZoneError:
                print("UNKNOWN TIMEZONE Error, use default")
                localTime = datetime.datetime.now()
            except KeyError:
                print("TIMEZONE Error")
                localTime = datetime.datetime.now()

            if localTime.hour < 8 or localTime.hour > 22:
                print("In Manager, no disturbing time")
                return current_state
            if localTime.minute > 30:
                print("In Manager, no disturbing time")
                return current_state

        for notificationHandle in self.__handleList:
            notificationHandle.send(res)

        return current_state
