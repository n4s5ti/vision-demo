#!/usr/bin/env python3
"""Strip BroadcastExtension from the Xcode scheme at CI time."""

import xml.etree.ElementTree as ET

NS = "http://schemas.apple.com/xcscheme/3.0"
ET.register_namespace("", NS)

tree = ET.parse("swift-frontend/VisionDemo.xcodeproj/xcshareddata/xcschemes/VisionDemo.xcscheme")
root = tree.getroot()
ba = root.find(f"{{{NS}}}BuildAction")

for entry in list(ba.findall(f"{{{NS}}}BuildActionEntry")):
    ref = entry.find(f"{{{NS}}}BuildableReference")
    if ref is not None and ref.get("BlueprintName") == "BroadcastExtension":
        ba.remove(entry)
        print("Removed BroadcastExtension from scheme")

tree.write(
    "swift-frontend/VisionDemo.xcodeproj/xcshareddata/xcschemes/VisionDemo.xcscheme",
    xml_declaration=True,
    encoding="UTF-8",
)
print("Scheme patched successfully")
