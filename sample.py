"""
Sample Usage
Uses the Azure provider
"""
from async_translate import AsyncTranslate
from async_translate.providers import Azure
import asyncio
import os

os.environ['MS_TRANSLATE_KEY'] = "YOUR_AZURE_TRANSLATE_KEY"


async def main():
    engine = AsyncTranslate()
    await engine.add_provider(Azure())

    languages = engine.languages
    print("Supported Languages", languages)

    detected_language = await engine.detect("bonjour")
    # detect returns the language and provider used
    print("Detected 'bonjour' as ", detected_language)

    to_english = await engine.translate("guten morgen", to="en")
    print("Translated 'guten morgen' to english as ", to_english)

# Run it!
asyncio.run(main())
