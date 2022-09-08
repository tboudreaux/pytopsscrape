def test_format_TOPS_string():
    testInput = [
            ('H', 0.5, 0.8, 0.0, 0.0, 0.0, 0.0),
            ('He', 0.5, 0.2, 0.0, 0.0, 0.0, 0.0)
            ]
    targetOutput = "0.5000000000 H 0.5000000000 He"

    from pyTOPSScrape.api.utils import format_TOPS_string

    testResults = format_TOPS_string(testInput)

    assert testResults == targetOutput


