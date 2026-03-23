import copy
import logging
import os

from . import bulletin
from . import xmlConfig as des
#
# Copyright (C) 2025 Mark Oberfield
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact Info: Mark.Oberfield@gmail.com
#


class Encoder(object):
    def __init__(self):
        """Superclass for invoking MDL decoders and encoders for a code form."""

        self.geoLocationsDB = None
        self._Logger = logging.getLogger(__name__)
        #
        # Always work in GMT
        os.environ['TZ'] = 'GMT0'

    def _each_tac_encode_stage(self, attrs, translatedBulletinID, receiptTime, text):
        """Yield one dict per TAC match: tac, decoded (deep copy before encoder), element or None."""
        for tac in self.re_TAC.findall(text):
            decodedTAC = self.decoder(tac)
            if decodedTAC['bbb'] == '':
                decodedTAC['bbb'] = attrs['bbb']

            if des.TRANSLATOR:
                decodedTAC['translatedBulletinID'] = translatedBulletinID
                if receiptTime is not None:
                    decodedTAC['translatedBulletinReceptionTime'] = receiptTime
                else:
                    decodedTAC['translatedBulletinReceptionTime'] = decodedTAC['translationTime']

            elif 'err_msg' in decodedTAC:
                if self.T1T2 == 'L':
                    try:
                        self._Logger.warning('Will not create IWXXM document for %s' % decodedTAC['ident']['str'])
                    except KeyError:
                        self._Logger.warning('Bad observation or TAF: Could not determine ICAO ID: %s' % tac)
                else:
                    self._Logger.warning('Will not create IWXXM advisory because of a decoding error.')

                continue

            if self.geoLocationsDB is not None:
                try:
                    metaData = self.geoLocationsDB.get(decodedTAC['ident']['str'], '|||0.0 0.0 0')
                except KeyError:
                    self._Logger.warning('Bad observation, could not determine icaoID: %s' % tac)
                    continue

                fullname, iataID, alternateID, position = metaData.split('|')

                if len(fullname) > 0:
                    decodedTAC['ident']['name'] = fullname
                if len(alternateID) > 0:
                    decodedTAC['ident']['alternate'] = alternateID
                if len(iataID) > 0:
                    decodedTAC['ident']['iataID'] = iataID

                decodedTAC['ident']['position'] = position
                if position == '0.0 0.0 0':
                    self._Logger.warning(
                        '"%s" not found in geoLocationsDB. Location missing.' % decodedTAC['ident']['str']
                    )
            decoded_snapshot = copy.deepcopy(decodedTAC)
            element = None
            try:
                element = self.encoder(decodedTAC, tac)
            except SyntaxError as msg:
                self._Logger.warning(msg)
            yield {'tac': tac, 'decoded': decoded_snapshot, 'element': element}

    def iter_encode_stages(self, text, receiptTime=None, **attrs):
        """Walk the same path as encode() per TAC; yields dicts with tac, decoded, element (or None).

        Decoded is a deep copy taken immediately before invoking the IWXXM encoder."""
        try:
            AHL = self.re_AHL.search(text)
            merged = dict(attrs)
            merged.update(AHL.groupdict(''))
            merged['tt'] = self.T1T2
            translatedBulletinID = AHL.group(0).replace(' ', '')
            yield from self._each_tac_encode_stage(merged, translatedBulletinID, receiptTime, text)
        except AttributeError:
            return

    def encode(self, text, receiptTime=None, **attrs):
        """Parses text to extract the WMO AHL line and one or more TAC forms.

        text = character string containing entire TAC message (required)
        receiptTime = date/time stamp the TAC message was received (optional, see xmlConfig.py)

        returns Bulletin object."""
        #
        collection = bulletin.Bulletin()
        #
        # Get the WMO AHL line and the TAC form(s)
        try:
            AHL = self.re_AHL.search(text)
            attrs.update(AHL.groupdict(''))
            attrs['tt'] = self.T1T2
            collection.set_bulletinIdentifier(**attrs)

            translatedBulletinID = AHL.group(0).replace(' ', '')

            for stage in self._each_tac_encode_stage(attrs, translatedBulletinID, receiptTime, text):
                if stage['element'] is not None:
                    collection.append(stage['element'])

        except AttributeError:
            pass

        return collection
