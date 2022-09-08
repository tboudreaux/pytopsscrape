def test_full_stack():
    from pyTOPSScrape.scripts import full_run

    import re
    import os

    kwargs = {
            "abunTable": "../../examples/exampleDataFiles/GS98.abun",
            "abunMap": "../../examples/exampleDataFiles/exampleAbunMap.dat",
            "force": False,
            "outputDirectory": "./rawOutput",
            "noopal" : False,
            "nofetch" : False,
            "output" : "./GS98TestResult.opac",
            "hardforce" : True,
            "jobs" : 20,
            "rect" : False
            }

    full_run(kwargs)

    if not os.path.exists("./GS98TestResult.opac"):
        raise AssertionError("Output File not saved!")

    with open("./GS98Target.opac", "r") as f:
        target = f.read()

    with open("./GS98TestResult.opac", "r") as f:
        result = f.read()

    targetDateCleaned = re.sub(
            r"\d{4}(?:0|1)[0-9](?:0|1)[0-9]",
            "dddddddd",
            target
            )

    resultDateCleaned = re.sub(
            r"\d{4}(?:0|1)[0-9](?:0|1)[0-9]",
            "dddddddd",
            result
            )

    assert targetDateCleaned == resultDateCleaned

def test_nofetch():
    from pyTOPSScrape.scripts import full_run

    import re
    import os

    kwargs = {
            "abunTable": "../../examples/exampleDataFiles/GS98.abun",
            "abunMap": "../../examples/exampleDataFiles/exampleAbunMap.dat",
            "force": False,
            "outputDirectory": "./rawOutputCacheForNoFetchTest",
            "noopal" : False,
            "nofetch" : True,
            "output" : "./GS98TestResult.opac",
            "hardforce" : False,
            "jobs" : 20,
            "rect" : False
            }

    full_run(kwargs)

    if not os.path.exists("./GS98TestResult.opac"):
        raise AssertionError("Output File not saved!")

    with open("./GS98Target.opac", "r") as f:
        target = f.read()

    with open("./GS98TestResult.opac", "r") as f:
        result = f.read()

    targetDateCleaned = re.sub(
            r"\d{4}(?:0|1)[0-9](?:0|1)[0-9]",
            "dddddddd",
            target
            )

    resultDateCleaned = re.sub(
            r"\d{4}(?:0|1)[0-9](?:0|1)[0-9]",
            "dddddddd",
            result
            )

    assert targetDateCleaned == resultDateCleaned

if __name__ == "__main__":
    test_nofetch()
