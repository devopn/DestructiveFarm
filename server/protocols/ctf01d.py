import requests

from server import app
from server.models import FlagStatus, SubmitResult

RESPONSES = {
    FlagStatus.ACCEPTED: ["accepted", "flag already stoled by your"],
    FlagStatus.REJECTED: [
        "flag has wrong format",
        "flag is too old or flag never existed or flag alredy stole",
        "flag is too old",
        "this is your flag",
        "game already ended",
    ],
    FlagStatus.QUEUED: [
        "game not started yet",
        "game on coffeebreak now",
        "not found get-parameter 'teamid' or parameter is empty",
        "not found get-parameter 'flag' or parameter is empty",
        "this is team not found",
        "your same service is dead. try later",
    ],
}

TIMEOUT = 5


def submit_flags(flags, config):
    unknown_responses = set()

    for item in flags:
        url = f"http://{config['SYSTEM_HOST']}:{config['PORT']}/flag?teamid={config['SYSTEM_TOKEN']}&flag={item.flag}"

        try:
            response = requests.get(url, timeout=TIMEOUT).text.strip()
            response_lower = response.lower()

            for status, substrings in RESPONSES.items():
                if any(sub in response_lower for sub in substrings):
                    found_status = status
                    break
            else:
                found_status = FlagStatus.QUEUED
                if response not in unknown_responses:
                    unknown_responses.add(response)
                    app.logger.warning(
                        "Unknown response (flag will be resent): %s", response
                    )

            yield SubmitResult(item.flag, found_status, response)

        except requests.RequestException as e:
            app.logger.error("Request failed: %s", str(e))
            yield SubmitResult(item.flag, FlagStatus.QUEUED, "Request failed")
