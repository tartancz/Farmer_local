from datetime import datetime

import pytest

from src.watcher.youtube_api import DetailedVideoFromApi
from src.redeemer.redeemer import CodeState


@pytest.mark.parametrize("video, expected_value", [
    (
            DetailedVideoFromApi(
                url='https://www.youtube.com/watch?v=999999',
                video_id='999999',
                publish_time=datetime.max,
                description='Some video description 5555,2589645656,123456789',
                video_lenght=24.6,
                title="Some video title",
            ),
            ["5555", "123456789"]
    ),
    (
            DetailedVideoFromApi(
                url='https://www.youtube.com/watch?v=999999',
                video_id='999999',
                publish_time=datetime.max,
                description='123456789Some video description 5555,2589645656,',
                video_lenght=24.6,
                title="Some video title",
            ),
            ["123456789", "5555"],
    )
])
def test_finds_code_in_description(farmer, video, expected_value):
    codes = farmer._finds_code_in_description(video)
    assert len(codes) == len(expected_value)
    assert codes[0] == expected_value[0]
    assert codes[1] == expected_value[1]


@pytest.mark.parametrize("codes, video, expected_value",
                         [
                             (
                                     [
                                         "123456789",
                                         "456789",
                                         "5555",
                                         "123456789"
                                     ],
                                     DetailedVideoFromApi(
                                         url='https://www.youtube.com/watch?v=999999',
                                         video_id='999999',
                                         publish_time=datetime.max,
                                         description='123456789Some video description 5555,2589645656,',
                                         video_lenght=24.6,
                                         title="Some video title"),
                                     [
                                         CodeState.SUCCESSFULLY_REDEEM,
                                         CodeState.BAD_CODE,
                                         CodeState.SUCCESSFULLY_REDEEM,
                                         CodeState.ALREADY_TAKEN
                                     ]
                             )

                         ])
def test_redeem_codes_from_description(farmer, codes, video, expected_value):
    with farmer:
        farmer._redeem_codes_from_description(codes, video)
    assert farmer.db.code.get_count_of_rows() == 4

    for i, code in enumerate(farmer.db.code.get_codes_by_video_id(video.video_id)):
        assert code.code_state == expected_value[i]
        assert code.code == codes[i]
        assert code.video_id == video.video_id
        assert code.id == i + 1
