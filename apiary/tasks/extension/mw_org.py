"""Synchronize Rating to Mediawiki.org for extensions."""
# pylint: disable=C0301,R0201,R0904

from apiary.tasks import BaseApiaryTask
import logging
import requests
import ConfigParser
from xml.etree import ElementTree
import os
import mwparserfromhell

LOGGER = logging.getLogger()

class MediawikiTasks(BaseApiaryTask):
    """Update extension data on mediawiki.org"""

    def get_rating(self, extension_name):
        """Retrieve and calculate total rating for an extension"""

        rating_properties = ['Has ease of installation rating', 'Has usability rating', 'Has documentation quality rating']
        total_rating = 0
        for property in rating_properties:
            try:
                wiki_return = self.bumble_bee.call({
                    'action': 'ask',
                    'query': ''.join([
                        "[[Category:Reviews]]",
                        "[[Has item::%s]]" % extension_name,
                        "|?%s|format=average" % property
                        ])
                    })
                rating = ((wiki_return['query']['results']).values()[0])['printouts'][property]
                total_rating = total_rating + rating[0]
            except Exception, e:
                raise Exception("Error while querying for Rating for extension %s (%s)." % (extension_name, e))

        return (total_rating / len(rating_properties) )

    def get_mwpagetitle(self, extension_name):
        """Return the corresponding page for the extension on mw.o"""
        #To be modified to fetch by smw property

        return extension_name

    def parse(self, title, wiki):
        """Function to parse MW page using mwparserfromhell"""

        data = {"action": "query", "prop": "revisions", "rvlimit": 1,
                "rvprop": "content", "format": "json", "titles": title}
        wiki_return = wiki.call(data)
        text = wiki_return["query"]["pages"].values()[0]["revisions"][0]["*"]
        return mwparserfromhell.parse(text)

    def updatemediawiki(self, title, data):
        """Edit a page on mediawiki.org using its title"""

        wiki_return = self.mworg_bee.call({
            'action':'edit',
            'title':title,
            'text':data,
            'token':self.mworg_bee_token,
            'assert':'user'
        })
        LOGGER.debug(wiki_return)
        if 'error' in wiki_return:
            raise Exception(wiki_return)

        return wiki_return

    def run(self, extension_name):
        """Get rating information for an extension and write to mediawiki"""

        rating = self.get_rating(extension_name)
        mwtitle = self.get_mwpagetitle(extension_name)

        data = self.parse(mwtitle, self.mworg_bee)
        for template in data.filter_templates():
            if template.name.matches(" "):
            template.add("rating", rating)

        #Update ratings inside extension template
        wiki_return = self.updatemediawiki(mwtitle, data)

        #Write code to fetch more data to mw.o in subpage

        return wiki_return

    def generate_template(self, apiary_data):
        """Build the block to add additional page to extensions for apiary data"""
        return 0
