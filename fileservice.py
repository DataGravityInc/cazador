"""
Core module for External File Service Interface.

This module defines the base External File Service Interface used by data/file
providers such as Amazon S3, Microsoft Azure, Google Drive, etc. access modules.
"""

import os
import sys
import logging
from abc import ABCMeta, abstractmethod


class fileServiceInterface(metaclass=ABCMeta):
    """External File Service Interface."""

    @staticmethod
    @abstractmethod
    def get_service_type():
        """Return a string id for the file service type handled."""
        raise NotImplementedError

    @abstractmethod
    def find_file(self, name=None, md5=None, sha1=None):
        """
        Search for a file by name or hash.

        If a mixture of input parameters are included then the search
        will walk through in the following manner:
            1. If name is defined then look by name
            2. If not found and md5 is defined then look by md5
            3. If not found and sha1 is defined then look by sha1
            4. If not found raise.

        Args:
            name (string): Filename to find.
            md5 (string): MD5 hash of the file to find.
            sha1 (string): SHA1 hash of the file to find.

        Returns:
            List of file identifiers matching the request parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def get_file(self, name=None, md5=None, sha1=None):
        """
        Search for a file by name or hash and download a copy.

        If a mixture of input parameters are included then the search
        will walk through in the following manner:
            1. If name is defined then look by name
            2. If not found and md5 is defined then look by md5
            3. If not found and sha1 is defined then look by sha1
            4. If not found raise.

        Args:
            name (string): Filename to find.
            md5 (string): MD5 hash of the file to find.
            sha1 (string): SHA1 hash of the file to find.

        Returns:
            List of files matching the request parameters.
        """
        raise NotImplementedError