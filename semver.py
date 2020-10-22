import re
import string

# This is an implementation of semver, detailed here:
# https://semver.org/
# The Semantic Versioning specification was originally authored by Tom
# Preston-Werner, inventor of Gravatar and cofounder of GitHub.
# Creative Commons ― CC BY 3.0
# https://creativecommons.org/licenses/by/3.0/

valid_semver_regex = (r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-"
                      r"9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*"
                      r"[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0"
                      r"-9a-zA-Z-]+)*))?$")


class Version:
    def __init__(self, version="0.0.0"):
        version = str(version)
        assert re.match(valid_semver_regex, version)
        self.version = str(version)
        self.version_string = str(version)
        self.version_list = version.split(".", 2)

        self.major, self.minor, self.full_patch = self.version_list[:3]
        self.patch = self.full_patch
        self.build = ""
        self.prerelease = ""
        self.prerelease_parts = []
        if '+' in self.patch:
            self.patch, self.build = self.patch.split('+')
        if '-' in self.patch:
            self.prerelease = self.patch[self.patch.find('-')+1:]
            self.patch = self.patch[:self.patch.find('-')]
        if '.' in self.prerelease:
            self.prerelease_parts = self.prerelease.split('.')
        self.version_list = [self.major, self.minor, self.patch,
                             self.prerelease]

    def __str__(self):
        return self.version_string

    @staticmethod
    def valid(v):
        return re.match(valid_semver_regex, str(v))

    @staticmethod
    def is_numeric(s):
        retval = True
        for l in s:
            if l not in string.digits:
                retval = False
        return retval

    def __lt__(self, other):
        if type(other) is str:
            other = Version(other)
        assert self.valid(other)
        retval = False
        retval = int(self.major) < int(other.major)
        if int(self.major) == int(other.major):
            retval = int(self.minor) < int(other.minor)
            if int(self.minor) == int(other.minor):
                retval = int(self.patch) < int(other.patch)
                if int(self.patch) == int(other.patch):
                    final = False
                    # no prerelease fields
                    if (len(self.prerelease_parts) == 0 and
                       len(other.prerelease_parts) == 0):
                        final = True
                    # larger set of prerelease fields takes higher precedence
                    if (len(self.prerelease_parts) < len(other.prerelease_parts)
                            and other.prerelease.find(self.prerelease) == 0):
                        retval = True
                        final = True
                        # unless one has no prerelease fields
                        if len(self.prerelease_parts) == 0:
                            retval = False
                    elif (len(self.prerelease) > len(other.prerelease)
                          and self.prerelease.find(other.prerelease) == 0):
                        retval = False
                        final = True
                        if len(other.prerelease_parts) == 0:
                            retval = True
                    else:
                        # iterate through dotted pr fields
                        for p, q in zip(self.prerelease.split('.'),
                                        other.prerelease.split('.')):
                            # ignore if comparison already resolved
                            if not final:
                                # compare purely numeric fields
                                if self.is_numeric(p) and self.is_numeric(q):
                                    if int(p) < int(q):
                                        retval = True
                                        final = True
                                    elif int(p) > int(q):
                                        retval = False
                                        final = True
                                # compare alphanum fields
                                elif (not self.is_numeric(p)
                                      and not self.is_numeric(q)):
                                    if p < q:
                                        retval = True
                                        final = True
                                    elif p > q:
                                        retval = False
                                        final = True
                                # numeric lower than alphanum
                                else:
                                    if self.is_numeric(p):
                                        retval = True
                                        final = True
                                    else:
                                        retval = False
                                        final = True
        return retval

    def __eq__(self, other):
        return str(self).split('+')[0] == str(other).split('+')[0]

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other


examples = []
examples.append(Version())
examples.append(Version("1.0.0-alpha"))
examples.append(Version("1.0.0-alpha.1"))
examples.append(Version("1.0.0-alpha.beta"))
examples.append(Version("1.0.0-beta"))
examples.append(Version("1.0.0-beta.2"))
examples.append(Version("1.0.0-beta.11"))
examples.append(Version("1.0.0-rc.1"))
examples.append(Version("1.0.0"))
examples.append(Version("2.0.0"))
examples.append(Version("2.1.0"))
examples.append(Version("2.1.1"))
examples.append(Version("2.1.26"))
examples.append(Version("2.1.26"))
# examples.append(Version("4.1"))  # invalid according to semver guidelines


def verbose(a):
    for i in a.__dict__:
        print(i, a.__dict__[i])


def test(a, b):
    if a < b:
        print(f"{a} < {b}")
    if a <= b:
        print(f"{a} <= {b}")
    if a == b:
        print(f"{a} == {b}")
    if a != b:
        print(f"{a} != {b}")
    if a > b:
        print(f"{a} > {b}")
    if a >= b:
        print(f"{a} >= {b}")
    print()


if __name__ == "__main__":
    for pair in zip(examples[:-1], examples[1:]):
        test(*pair)
