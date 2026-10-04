import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from maubot import Plugin, MessageEvent
from maubot.handlers import event
from mautrix.types import EventType

URL_RE = re.compile(
    r"https?://[^\s]+"
)

FILTER_FROM_ALL = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content"
}

DOMAIN_FILTERS = {
    "youtube.com": {"si", "feature"},
    "www.youtube.com": {"si", "feature"},
    "youtu.be": {"si", "feature"}
}

def clean_url(url: str) -> str:
    parts = urlsplit(url)
    hostname = (parts.hostname or "").lower()
    to_remove = FILTER_FROM_ALL | DOMAIN_FILTERS.get(hostname, set())

    query = [(k, v) for k, v in parse_qsl(parts.query) if k not in to_remove]

    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

def clean_message(message: str) -> str:
    return URL_RE.sub(
        lambda match: clean_url(match.group(0)),
        message,
    )

class UtmDisruptorBot(Plugin):
    @event.on(EventType.ROOM_MESSAGE)
    async def on_message(self, evt: MessageEvent) -> None:
        body = evt.content.body
        cleaned = clean_message(body)

        if cleaned != body:
            await evt.reply(
                f"In the future, please remove that tracking junk from links you send.\n"+
                f"That often is stuff after the `?`, like `si=` or `utm_source=`.\n"
                f"Here, I fixed it for you:\n\n{cleaned}"
            )
