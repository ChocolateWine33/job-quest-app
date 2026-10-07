


def get_contents(chat_history: list,  user_message: str, contents: list | None = None) -> list:

    if contents is None:
        contents = []
        
    for chat in chat_history:
        contents.append({"role": chat.role, "parts": [{"text": chat.message_content}]})

    contents.append({"role": "user", "parts": [{"text": user_message}]})

    return contents
