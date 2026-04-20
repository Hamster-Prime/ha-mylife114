"""Constants for the Mylife114 integration."""

DOMAIN = "mylife114"

CONF_UID = "uid"
CONF_USER_AGENT = "user_agent"

BASE_URL = "https://guard.mylife114.com"
API_COMMUNITIES = "/api/v1/get_communitys"
API_COMMUNITY_DOORS = "/api/v1/community_doors"
API_OPEN_DOOR = "/api/v1/open_door"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 16; Pixel 7 Pro) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/116.0.0.0 Mobile Safari/537.36 "
    "MicroMessenger/8.0.68.3003"
)

DEFAULT_DIRECTION = 1
UPDATE_INTERVAL_HOURS = 12

SERVICE_OPEN_DOOR = "open_door"
