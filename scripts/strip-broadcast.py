#!/usr/bin/env python3
"""Strip BroadcastExtension from the Xcode scheme at CI time."""

import xml.etree.ElementTree as ET
import re
import sys

scheme_path = sys.argv[1] if len(sys.argv) > 1 else \
    "swift-frontend/VisionDemo.xcodeproj/xcshareddata/xcschemes/VisionDemo.xcscheme"

with open(scheme_path) as f:
    content = f.read()

# Use regex to remove BuildActionEntry blocks referencing BroadcastExtension
content = re.sub(
    r'<BuildActionEntry[^>]*>.*?BroadcastExtension.*?</BuildActionEntry>',
    '',
    content,
    flags=re.DOTALL,
)

with open(scheme_path, 'w') as f:
    f.write(content)

print("Stripped BroadcastExtension from scheme")
