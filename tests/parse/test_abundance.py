def test_mfrac_to_a():
    mfrac = 0.24
    HeMass = 4.003
    X = 0.75
    Y = 0.24
    target = 10.906224920324307

    from pyTOPSScrape.parse.abundance import mfrac_to_a

    assert target == mfrac_to_a(mfrac, HeMass, X, Y)

def test_a_to_mfrac():
    a = 10.906
    HeMass = 4.003
    X = 0.75
    target = 0.2398757366160616

    from pyTOPSScrape.parse.abundance import a_to_mfrac

    assert target == a_to_mfrac(a, HeMass, X)

