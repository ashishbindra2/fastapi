from enum import Enum

from pydantic import BaseModel


class SentenceRequest(BaseModel):
    id: int
    sentence: str
    intent: str


class IntentRequest(BaseModel):
    intent: str
    description: str


class MessageRequest(BaseModel):
    message: str


# class ModelChoices(str, Enum):
#     model1 = "Model 1"
#     model2 = "Model 2"
#     model3 = "Model 3"


# class ModelChoices(BaseModel):
#     model_name


