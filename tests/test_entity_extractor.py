import pytest
from ml.inference.entity_extractor import EntityExtractorModel


@pytest.fixture
def extractor():
    return EntityExtractorModel()


@pytest.mark.asyncio
async def test_file_path_extraction(extractor):
    entities = await extractor.extract("open file 'document.txt'")
    assert "file_path" in entities
    assert entities["file_path"] == "document.txt"


@pytest.mark.asyncio
async def test_time_extraction(extractor):
    entities = await extractor.extract("remind me at 3:30 PM")
    assert "time" in entities


@pytest.mark.asyncio
async def test_script_extraction(extractor):
    entities = await extractor.extract("run script.py")
    assert "script_name" in entities
    assert entities["script_name"] == "script.py"


@pytest.mark.asyncio
async def test_operation_extraction(extractor):
    entities = await extractor.extract("delete the old files")
    assert "operation" in entities
    assert entities["operation"] == "delete"

