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
# This seems to be frequently updated and well maintained.
GITHUB_MSINTERNAL_URL = "https://raw.githubusercontent.com/ItzLevvie/MicrosoftTeams-msinternal/master/defconfig"
OS_STR = "(osx-x64 + osx-arm64)"
MS_STRING_TARGET = "URLs for the latest production build of Microsoft Teams:"
RE_EXTRACT_URL = r'https?://\S+'

class TeamsURLProvider(URLGetter):
    description= __doc__

    input_variables = {}
    output_variables = {
        "download_url": {
            "description": "URL for downloading the latest version of Microsoft Teams"
        },
        "download_version": {
            "description": "Version of Microsoft Teams to from the download_url"
        }
    }

    """ Pull information file, and extract relevant data """
    def getDownloadInfo(self):
        self.output("Retrieve 'defconfig' from GITHUB")
        headers = {

        }
        defconfig = self.download(GITHUB_MSINTERNAL_URL, headers, text=True)
        # # Pull block of "production" strings
        defconfig_split = str.splitlines(defconfig)
        line_index = -1
        for l in range(len(defconfig_split)):
            if defconfig_split[l] == MS_STRING_TARGET:
                line_index = l
                break
        
        if line_index < 0:
            return ProcessorError("Unable to locate prod block location")
        else:
            prod_block = defconfig_split[line_index+1:]
            self.output("Found production block: %s" % prod_block)

        for item in prod_block:
            if OS_STR in item:
                prod_string = item
                self.output("Found production version for macOS: %s" % prod_string)
                break

        # Get and Set prod_url from prod_string
        prod_url_search = re.compile(RE_EXTRACT_URL).findall(prod_string)
        if prod_url_search:
            prod_url = prod_url_search[0]
            self.env["download_url"] = prod_url
        else:
           return ProcessorError("Unable to extract 'download_url'")
        
        # Get and Set prod_ver from prod_string
        prod_ver = prod_string.split(" ")[0]
        if prod_ver:
            self.env["download_version"] = prod_ver
        else:
            return ProcessorError("Unable to extract 'download_version'")

        # Output details
        self.output("Determined version of %s @ %s" % (prod_ver, prod_url))
    
    def main(self):
        try:
            self.output("Starting...")
            self.getDownloadInfo()
        except Exception as err:
            raise ProcessorError(err)
        self.output("Complete. Bye!")

if __name__ == "__main__":
    PROCESSOR = TeamsURLProvider()
    PROCESSOR.execute_shell()
    