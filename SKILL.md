---
name: vision-demo
description: |
  LiveKit Vision Demo — iOS app with realtime audio/video AI assistant.
  Agent: Python + LiveKit Agents + Gemini Live API.
  Frontend: Swift iOS app with camera, screen share, background support.
  Multica integration: autopilots for iOS IPA builds, tailnet delivery,
  Apple Reminders/iMessage/Find My actions.
version: 1.0.0
author: da3mon
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [livekit, vision, ios, gemini, webrtc, swift]
    related_skills: [apple-integration, ios-ipa-build-without-eas, serve-file-over-tailnet, multica]
---

# Vision Demo — LiveKit AI Assistant

Voice AI assistant with realtime audio and video input, built on LiveKit's Swift SDK (iOS) and Python Agents framework with Gemini Live API.

## Architecture

```
iPhone (Swift) ──WebRTC──▶ LiveKit Cloud ◀── Agent (Python) ──▶ Gemini Live
                                │
                          Multica Actions
                     (builds, serve, reminders)
```

## Components

### 1. iOS Frontend (`swift-frontend/`)
- SwiftUI app with camera, microphone, screen sharing
- Background audio support for multitasking
- LiveKit Swift SDK integration
- Token service for sandbox auth

### 2. Python Agent (`agent/`)
- LiveKit Agents framework with Gemini Live multimodal model
- Video frame processing at 0.3-1 fps
- Multica action integration (webhook triggers)

### 3. Multica Actions
- **ios-ipa-build-without-eas**: GitHub Actions CI for unsigned IPA builds
- **serve-file-over-tailnet**: Deliver IPA/artifacts to iPhone over Tailscale
- **apple-integration**: Reminders, iMessage, Find My from CLI (macOS)

## Running the Agent

```bash
cd agent
cp .env.example .env  # fill in LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, GOOGLE_API_KEY
source .venv/bin/activate
python main.py dev
```

## Building iOS App

Requires Xcode 16+ on macOS. Open `swift-frontend/VisionDemo/VisionDemo.xcodeproj`.

## Multica Integration

Set these env vars in `agent/.env`:
```
MULTICA_TOKEN=mul_...
MULTICA_WORKSPACE_ID=a891648f-b3d2-4144-a13c-c58b720e3ca0
```

When configured, the agent can:
- Trigger iOS IPA builds via autopilot webhook
- Serve built artifacts to iPhone over tailnet
- Create Multica issues for tracking
