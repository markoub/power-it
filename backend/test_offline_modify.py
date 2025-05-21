import os
import asyncio
from tools.modify import modify_single_slide
from tools.slides import OFFLINE_SLIDES_RESPONSE

os.environ["POWERIT_OFFLINE"] = "1"

async def test_offline_modify_single_slide():
    compiled = OFFLINE_SLIDES_RESPONSE
    research = {"content": "dummy"}
    result = await modify_single_slide(compiled, research, "Improve", 0)
    assert result["modified_slide"]["fields"]["title"].startswith("Modified")

if __name__ == "__main__":
    asyncio.run(test_offline_modify_single_slide())
