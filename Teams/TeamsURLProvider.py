#!/usr/local/autopkg/python
#
#
# Licensed under the Educational Community License, Version 2.0 (ECL-2.0);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/ECL-2.0
#
#
import re

from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter

__all__ = ["TeamsURLProvider"]

# Leverages repo: https://github.com/ItzLevvie/MicrosoftTeams-msinternal
# Which seems to be frequently updated.
GITHUB_MSINTERNAL_URL = "https://raw.githubusercontent.com/ItzLevvie/MicrosoftTeams-msinternal/master/defconfig"
OS_STR = "(osx-x64 + osx-arm64)"
RE_OS_STR = OS_STR.replace("(", "\(").replace(")", "\)")
RE_EXTRACT_PROD_STRS = "(?<=URLs for the latest production build of Microsoft Teams:)(?:\n.*){9}" # Needs some tweaking, this assumes always 9 lines.
RE_EXTRACT_PROD_LINE = "(.*)%s(.*)" % OS_STR
RE_EXTRACT_URL = r"((?<=:\ ).+)"

class TeamsURLProvider(URLGetter):
    description= __doc__

    input_variables = {}
    output_variables = {
        "download_url": {
            "description": "URL for downloading the latest version of Microsoft Teams"
        },
        "download_version": {
            "description": "Version of Microsoft Teams to from the download_url"
        },
        "ms_version": {
            "description": "Microsoft Teams presents it's version differently from what it actually is. This converts 1.5.00.$BUILDNO to 1.00.5$BUILDNO"
        }
    }

    """ Pull information file, and extract relevant data """
    def getDownloadURL(self):
        self.output("Retrieve 'defconfig' from GITHUB")
        headers = {

        }
        defconfig = self.download(GITHUB_MSINTERNAL_URL, headers, text=True)

        # Pull block of "production" strings
        prodBlock = re.findall(
            re.compile(RE_EXTRACT_PROD_STRS),
            defconfig
        )[0].splitlines()
        if prodBlock is None:
            return ProcessorError("Unable to parse production block.")
        self.output("Found production block.")

        prodIndex = self._indexSubstring(prodBlock)
        if prodIndex is None:
            return ProcessorError("Unable to parse production index.")

        prodLine = prodBlock[prodIndex]
        self.output("Parsing production line @%s from block." % prodIndex)

        prodURL = re.search(
            RE_EXTRACT_URL,
            prodLine
        )[0]
        if prodURL is None:
            return ProcessorError("Unable to parse production url.")
        else:
            self.env["download_url"] = prodURL
            self.output("Found production download url for Mac.")

        prodVersion = prodLine.split(" ")[0]
        if prodVersion is None:
            self.output("Unable to extract version. Submitting -1")
            self.env["download_version"] = -1
        else: 
            self.env["download_version"] = prodVersion
            self.output("Found production version.")
            raw_version = prodVersion
            ms_version_split = prodVersion.split(".")

        self.output("Determined version of %s @ %s" % (prodVersion, prodURL))
        print("Determined version of %s @ %s" % (prodVersion, prodURL))


    """ Scrape through production block to locate OS_STR in entry"""
    def _indexSubstring(self, thelist):
        self.output("Determining the correct production line.")
        for i, s in enumerate(thelist):
            macEntry = OS_STR in s
            if macEntry:
                return i
        return -1

    
    def main(self):
        try:
            self.output("Starting...")
            self.getDownloadURL()
        except Exception as err:
            raise ProcessorError(err)
        self.output("Complete. Bye!")


if __name__ == "__main__":
    PROCESSOR = TeamsURLProvider()
    PROCESSOR.execute_shell()
    