"""The Google Generative AI Conversation integration."""
from __future__ import annotations

import logging
import json
from typing import Literal

from google.api_core.exceptions import ClientError
import vertexai
from google.oauth2 import service_account
from vertexai.preview.generative_models import (
    GenerativeModel,
    GenerationConfig,
    Content,
    Part,
)
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid

from .const import (
    CONF_CHAT_MODEL,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_K,
    CONF_TOP_P,
    CONF_SERVICE_ACCOUNT,
    CONF_LOCATION,
    DEFAULT_CHAT_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    DEFAULT_LOCATION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigEntry):
    """Set up gemini component."""
    _LOGGER.info("loading %s completed.", DOMAIN)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Google Generative AI Conversation from a config entry."""
    _LOGGER.info("loading gemini entry")
    service_account_json = json.loads(entry.data[CONF_SERVICE_ACCOUNT])
    project = service_account_json.get("project_id")
    location = entry.data.get(CONF_LOCATION, DEFAULT_LOCATION)
    creds = service_account.Credentials.from_service_account_info(service_account_json)
    _LOGGER.info(
        "configuring vertex ai for GCP project %s and location %s", project, location
    )
    vertexai.init(project=project, location=location, credentials=creds)
    model = GenerativeModel(entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL))
    chat = model.start_chat()

    try:
        await chat.send_message_async("hi")
    except ClientError as err:
        if err.reason == "API_KEY_INVALID":
            _LOGGER.error("Invalid API key: %s", err)
            return False
        _LOGGER.error("Error getting model: %s", err)
        raise ConfigEntryNotReady(err) from err

    conversation.async_set_agent(hass, entry, GoogleGenerativeAIAgent(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload GoogleGenerativeAI."""
    # palm.configure(api_key=None)
    conversation.async_unset_agent(hass, entry)
    return True


class GoogleGenerativeAIAgent(conversation.AbstractConversationAgent):
    """Google Generative AI conversation agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[dict]] = {}
        # self.model = GenerativeModel(
        #     entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        # )
        # self.chat = self.model.start_chat()

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        raw_prompt = self.entry.options.get(CONF_PROMPT, DEFAULT_PROMPT)
        model = self.entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        temperature = self.entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        top_p = self.entry.options.get(CONF_TOP_P, DEFAULT_TOP_P)
        top_k = self.entry.options.get(CONF_TOP_K, DEFAULT_TOP_K)
        model = GenerativeModel(
            self.entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        )
        messages: list[Content] = [{}, {}]

        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid_now()

        try:
            prompt = self._async_generate_prompt(raw_prompt)
        except TemplateError as err:
            _LOGGER.error("Error rendering prompt: %s", err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Sorry, I had a problem with my template: {err}",
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )

        # always tell the model the current values
        messages[0] = Content(role="user", parts=[Part.from_text(text=prompt)])
        messages[1] = Content(role="model", parts=[Part.from_text(text="OK")])

        chat = model.start_chat(history=messages)

        _LOGGER.debug("Prompt for %s: %s", model, user_input.text)

        try:
            chat_response = await chat.send_message_async(
                user_input.text,
                generation_config=GenerationConfig(
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    # max_output_tokens=2048,
                ),
            )
        except ClientError as err:
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Sorry, I had a problem talking to Google Generative AI: {err}",
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )

        _LOGGER.debug("Response %s", chat_response)
        # For some queries the response is empty. In that case don't update history to avoid
        # "google.generativeai.types.discuss_types.AuthorError: Authors are not strictly alternating"
        if chat_response.text:
            self.history[conversation_id] = list(chat.history)

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(chat_response.text)
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    def _async_generate_prompt(self, raw_prompt: str) -> str:
        """Generate a prompt for the user."""
        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
            },
            parse_result=False,
        )
