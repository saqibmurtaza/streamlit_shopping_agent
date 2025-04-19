from typing import Literal, Union, Dict, Any
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: Union[str, Dict[str, Any]]
