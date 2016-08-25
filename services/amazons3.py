"""File service implementation for the Amazon S3 cloud service.

Created: 08/11/2016
Creator: Nathan Palmer
"""

from fileservice import fileServiceInterface
from cazobjects import CazFile
import boto3
import logging
logger = logging.getLogger(__name__)


class amazonS3Handler(fileServiceInterface):
    """Amazon cloud service handler."""

    def __init__(self, config_fields):
        """
        Initialize the Amazon S3 handler using configuration dictionary fields.

        Args:
            config_fields (dict): String dictionary from the configuration segment

        Configuration Fields:
            access_key_id (str): Repository access key id
            secret_key (str): Repository secret key for authentication
        """
        self.client = boto3.client("s3",
                                   region_name=config_fields["region"],
                                   aws_access_key_id=config_fields["access_key_id"],
                                   aws_secret_access_key=config_fields["secret_key"])

        self.buckets = []
        raw_buckets = config_fields["buckets"].split(';')
        for b in raw_buckets:
            if b:
                # Only add buckets that are not null or empty strings
                self.buckets.append(b)

    @staticmethod
    def get_service_type():
        """Return the type of file service (Amazon)."""
        return "AmazonS3"

    def convert_file(self, item):
        """Convert the file details into a CazFile."""
        return CazFile(None,
                       item['Key'],
                       None,
                       md5=item['ETag'],
                       path=item['Key'])

    def _find_object_by_etag(self, bucket, tag=None, alt_tag=None, find_one=False):
        """Crawl the contents of a bucket to find the object with a specific tag."""
        if not tag and not alt_tag:
            raise ValueError("No valid search tag specified.")

        marker = None
        matches = []
        while True:
            if marker:
                results = self.client.list_objects(Bucket=bucket, Marker=marker)
            else:
                results = self.client.list_objects(Bucket=bucket)

            # Walk the contents to find the tag(s)
            for content in results['Contents']:
                etag = content['ETag'].lower().replace('"', '')
                if tag and etag == tag.lower():
                    matches.append(self.convert_file(content))
                elif alt_tag and etag == alt_tag.lower():
                    matches.append(self.convert_file(content))

            if len(matches) > 0 and find_one:
                # If there was a request to stop on the first discovery break out
                break

            if results['IsTruncated']:
                marker = results['NextMarker']
            else:
                break

        return matches

    def find_file(self, name=None, md5=None, sha1=None):
        """Find one or more files using the name and/or hash in the Amazon cloud service."""
        matches = []
        for b in self.buckets:
            res = None
            if name:
                res = self.client.get_object(Bucket=b, Key=name)
                matches.append(self.convert_file(res))

            if not res and (md5 or sha1):
                print("Checking for hash {} and {}".format(md5, sha1))
                matches.extend(self._find_object_by_etag(b, tag=md5, alt_tag=sha1))

        return matches

    def get_file(self, name=None, md5=None, sha1=None):
        """Get a file from Amazon using the name or hashes."""
        raise NotImplementedError


# Register our handler
fileServiceInterface.register(amazonS3Handler)