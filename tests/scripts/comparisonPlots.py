import matplotlib.pyplot as plt
from pyTOPSScrape.parse import load_opal

import os
import datetime

def make_comparision_plot():
    TargetPath = "./GS98Target.opac"
    TestPath = "./GS98TestResult.opac"
    OPALPath = "./GS98OPAL.opac"

    targetTime = datetime.datetime.fromtimestamp(os.path.getmtime(TargetPath))
    testTime = datetime.datetime.fromtimestamp(os.path.getmtime(TestPath))
    OPALTime = datetime.datetime.fromtimestamp(os.path.getmtime(OPALPath))

    print(f"Target File Last Modified at: {targetTime}")
    print(f"Test File Last Modified at: {testTime}")
    print(f"OPAL Comp File Last Modified at: {OPALTime}")

    Target = load_opal(TargetPath)
    Test = load_opal(TestPath)
    OPAL = load_opal(OPALPath)

    fig, ax = plt.subplots(1,1,figsize=(10,7))
    ax.plot(Target[0], Target[2][75, :, 13], label="Current Test Target")
    ax.plot(Test[0], Test[2][75, :, 13], label="Test Result")
    ax.plot(OPAL[0], OPAL[2][75, :, 13], label="OPAL")
    ax.legend()
    ax.set_xlabel("Log T")
    ax.set_ylabel("Opacity")
    ax.set_title("Comparision made at log(R)=-1.5")
    plt.savefig("comparison.pdf", bbox_inches='tight')

    fig, ax = plt.subplots(1,1,figsize=(10,7))
    ax.plot(Target[0], Target[2][75, :, 13] - Test[2][75, :, 13])
    ax.set_xlabel("Log T")
    ax.set_ylabel("Opacity")
    ax.set_title("Target - Result Residuals made at log(R)=-1.5")
    plt.savefig("TRResid.pdf", bbox_inches='tight')


if __name__ == "__main__":
    make_comparision_plot()
