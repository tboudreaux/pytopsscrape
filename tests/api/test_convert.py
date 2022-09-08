def test_comp_list_2_dict():
    from pyTOPSScrape.api.convert import comp_list_2_dict

    testInput = [
            ('H', 0.5, 0.8, 0.0, 0.0, 0.0, 0.0),
            ('He', 0.5, 0.2, 0.0, 0.0, 0.0, 0.0)
            ]
    targetOutput = {
            'H' : (0.5, 0.8, 0.0, 0.0, 0.0, 0.0),
            'He': (0.5, 0.2, 0.0, 0.0, 0.0, 0.0),
            'K' : (0.0,0.0,0.0,0.0,0.0,0.0) # K is always added and set to 0
            }

    testResult = comp_list_2_dict(testInput)
    assert testResult == targetOutput

def test_parse_RMO_TOPS_table_file():
    testFile = "../scripts/rawOutputCacheForNoFetchTest/OP:76_0.7_0.22_0.07982056908314321.dat"

    from pyTOPSScrape.api.convert import parse_RMO_TOPS_table_file
    import pickle
    import numpy as np

    testResult = parse_RMO_TOPS_table_file(testFile)

    with open("./parseRMOTopsTarget.pkl", 'rb') as f:
        target = pickle.load(f)

    similar = True
    similar &= np.all(np.equal(testResult[0], target[0]))
    similar &= np.all(np.equal(testResult[1], target[1]))
    similar &= np.all(np.equal(testResult[2], target[2]))

    print(np.equal(testResult[2], target[2]))


    assert similar

def test_convert_rho_2_LogR():
    testFile = "../scripts/rawOutputCacheForNoFetchTest/OP:76_0.7_0.22_0.07982056908314321.dat"

    from pyTOPSScrape.api.convert import convert_rho_2_LogR
    from pyTOPSScrape.api.convert import parse_RMO_TOPS_table_file
    import pickle
    import numpy as np

    rho, LogT, RMO = parse_RMO_TOPS_table_file(testFile)

    testResult = convert_rho_2_LogR(rho, LogT, RMO)

    with open("./convertRho2LogRTarget.pkl", 'rb') as f:
        target = pickle.load(f)

    similar = True
    similar &= np.all(np.equal(target[0], testResult[0]))
    similar &= np.all(np.equal(target[1], testResult[1]))
    similar &= np.all(np.equal(target[2], testResult[2]))

    assert similar

def test_extract_composition_path():
    testFile = "../scripts/rawOutputCacheForNoFetchTest/OP:76_0.7_0.22_0.07982056908314321.dat"
    targetX = 0.7
    targetY = 0.22
    targetZ = 0.07982056908314321

    from pyTOPSScrape.api.convert import extract_composition_path

    X, Y, Z = extract_composition_path(testFile)

    assert X == targetX and Y == targetY and Z == targetZ


def generate_parse_RMO_TOPS_table_file_target():
    testFile = "../scripts/rawOutputCacheForNoFetchTest/OP:76_0.7_0.22_0.07982056908314321.dat"

    from pyTOPSScrape.api.convert import parse_RMO_TOPS_table_file
    import pickle

    testResult = parse_RMO_TOPS_table_file(testFile)

    with open("./parseRMOTopsTarget.pkl", 'wb') as f:
        pickle.dump(testResult, f)

def generate_convert_rho_2_LogR_target():
    testFile = "../scripts/rawOutputCacheForNoFetchTest/OP:76_0.7_0.22_0.07982056908314321.dat"

    from pyTOPSScrape.api.convert import convert_rho_2_LogR
    from pyTOPSScrape.api.convert import parse_RMO_TOPS_table_file
    import pickle

    rho, LogT, RMO = parse_RMO_TOPS_table_file(testFile)

    testResult = convert_rho_2_LogR(rho, LogT, RMO)

    with open("./convertRho2LogRTarget.pkl", 'wb') as f:
        pickle.dump(testResult, f)


if __name__ == "__main__":
    generate_parse_RMO_TOPS_table_file_target()
    generate_convert_rho_2_LogR_target()
