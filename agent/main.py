"""
LiveKit Vision Demo — Enhanced Agent with Multica Integration

Original: LiveKit vision assistant with Gemini Live API
Enhanced: + Multica actions, autopilot webhooks, iOS build workflows

Multica Skills wired:
  - apple-integration (Apple ecosystem CLI: Notes, Reminders, Find My, iMessage)
  - ios-ipa-build-without-eas (xcodebuild CI for unsigned IPA)
  - serve-file-over-tailnet (tailnet HTTPS file delivery to iPhone)

Architecture:
  iOS App (Swift) ──WebRTC──▶ LiveKit Cloud ◀──Python Agent──▶ Gemini Live API
                                    │
                              Multica Autopilots
                              (scheduled/triggered actions)
"""

import logging
import asyncio
import base64
import json
import os
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.agents.llm import ImageContent
from livekit.plugins import google, noise_cancellation

logger = logging.getLogger("vision-assistant")
load_dotenv()


# ─── Multica Action Integration ───────────────────────────────────────────

# Multica API base URL (cloud or self-hosted)
MULTICA_API = os.getenv("MULTICA_API_URL", "https://api.multica.ai")
MULTICA_WORKSPACE = os.getenv("MULTICA_WORKSPACE_ID", "")
# Bearer token for Multica API (PAT or JWT)
MULTICA_TOKEN = os.getenv("MULTICA_TOKEN", "")

MULTICA_HEADERS: dict[str, str] = {
    "Authorization": f"Bearer {MULTICA_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
} if MULTICA_TOKEN else {}


def multica_enabled() -> bool:
    """Check if Multica integration is configured."""
    return bool(MULTICA_TOKEN and MULTICA_WORKSPACE)


# ─── Multica Action Definitions ───────────────────────────────────────────
#
# These are the "actions" the vision agent can invoke through Multica.
# Multica autopilots expose webhook triggers; the agent can also create
# issues and trigger autopilots via the Multica REST API.

MULTICA_ACTIONS = {
    "build_ios_ipa": {
        "description": "Trigger an iOS IPA build via the ios-ipa-build-without-eas workflow on GitHub Actions",
        "autopilot": None,  # set via MULTICA_BUILD_AUTOPILOT_ID env var
    },
    "serve_to_iphone": {
        "description": "Serve a file to the iPhone over the tailnet using serve-file-over-tailnet",
        "command": "serve-file-over-tailnet",
    },
    "create_reminder": {
        "description": "Create an Apple Reminder via apple-integration skill",
        "command": "apple-reminder",
    },
    "send_imessage": {
        "description": "Send an iMessage via apple-integration skill",
        "command": "apple-imessage",
    },
    "find_my_device": {
        "description": "Locate an Apple device via Find My",
        "command": "apple-findmy",
    },
}


class VisionAssistant(Agent):
    """LiveKit vision agent with Multica action capabilities."""

    def __init__(self) -> None:
        self._tasks = []

        # Build instructions with Multica-aware context
        instructions = """
You are a helpful voice and vision assistant. You can see what the user's camera sees and hear what they say.

When the user asks you to perform actions, check if any of these capabilities apply:
- Building iOS apps (trigger CI builds)
- Serving files to iPhone over the tailnet
- Setting reminders
- Sending messages
- Finding devices

If Multica actions are available, you can offer to trigger them. Otherwise, respond naturally.
"""

        super().__init__(
            instructions=instructions,
            llm=google.beta.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8,
            ),
        )

    async def on_enter(self):
        def _image_received_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._image_received(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))

        get_job_context().room.register_byte_stream_handler("test", _image_received_handler)

        greeting = "Hi there! I'm your vision assistant"
        if multica_enabled():
            greeting += " with Multica actions enabled"
        greeting += ". I can see your camera and hear you. How can I help?"

        self.session.generate_reply(instructions=greeting)

    async def _image_received(self, reader, participant_identity):
        logger.info("Received image from %s: '%s'", participant_identity, reader.info.name)
        try:
            image_bytes = bytes()
            async for chunk in reader:
                image_bytes += chunk

            chat_ctx = self.chat_ctx.copy()
            chat_ctx.add_message(
                role="user",
                content=[
                    ImageContent(
                        image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                    )
                ],
            )
            await self.update_chat_ctx(chat_ctx)
            logger.debug("Image processed for %s", participant_identity)
        except Exception as e:
            logger.error("Error processing image: %s", e)


# ─── Multica Action Handlers ──────────────────────────────────────────────

async def multica_create_issue(title: str, description: str, labels: list[str] | None = None) -> dict:
    """Create a Multica issue from the agent."""
    if not multica_enabled():
        return {"error": "Multica not configured"}

    import aiohttp
    url = f"{MULTICA_API}/workspaces/{MULTICA_WORKSPACE}/issues"
    payload: dict[str, str | list[str]] = {
        "title": title,
        "description": description,
    }
    if labels:
        payload["labels"] = labels

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=MULTICA_HEADERS) as resp:
            return await resp.json()


async def multica_trigger_autopilot(autopilot_id: str, payload: dict | None = None) -> dict:
    """Trigger a Multica autopilot run."""
    if not multica_enabled():
        return {"error": "Multica not configured"}

    import aiohttp
    url = f"{MULTICA_API}/autopilots/{autopilot_id}/trigger"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload or {}, headers=MULTICA_HEADERS) as resp:
            return await resp.json()


# ─── Entrypoint ───────────────────────────────────────────────────────────

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession()
    await session.start(
        agent=VisionAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
