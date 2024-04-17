from datetime import datetime

import pytest

from src.watcher.youtube_api import DetailedVideoFromApi

@pytest.mark.parametrize("video, expected_value", [
    (DetailedVideoFromApi(
        url='https://www.youtube.com/watch?v=999999',
        video_id='999999',
        publish_time=datetime.max,
        description='Some video description 5555,2589645656,123456789',
        video_lenght=24.6,
        title="Some video title",
    ), ["5555", "123456789"])
])
def test_code_in_description(farmer, video, expected_value):
    codes = farmer._finds_code_in_desription(video)
    assert len(codes) == len(expected_value)
    assert codes[0] == expected_value[0]
    assert codes[1] == expected_value[1]
