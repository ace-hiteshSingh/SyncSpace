from datetime import datetime, timezone

from app.services.chat_service import ChatService


def test_chat_service_formats_time_in_indian_standard_time():
    utc_time = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    formatted_time = ChatService.format_time(utc_time)

    assert formatted_time == "08:34 AM"
