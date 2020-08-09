import os

CI = os.environ.get("CI")
print(CI)
if CI:
    print(CI == "true", CI.strip() == "true")

TRAVIS = os.environ.get("TRAVIS")
print(TRAVIS)
if TRAVIS:
    print(TRAVIS == "true", TRAVIS.strip() == "true")
