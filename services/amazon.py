"""File service implementation for Amazon cloud services.

Created: 08/11/2016
Creator: Nathan Palmer
"""

from fileservice import fileServiceInterface
import boto3


class amazonHandler(fileServiceInterface):
    """Amazon cloud service handler."""

    def __init__(self, config_fields):
        """
        Initialize the Amazon handler using configuration dictionary fields.

        Args:
            config_fields (dict): String dictionary from the configuration segment

        Configuration Fields:
            resource_type (str): s3, ec2, or glacier
            access_key_id (str): Amazon repository access key id
            secret_key (str): Amazone repository secret key for authentication
        """
        if "resource_type" not in config_fields:
            res_type = "s3"
        else:
            res_type = config_fields["resource_type"]

        self.client = boto3.client(res_type,
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
        return "Amazon"

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
                    matches.append(content)
                elif alt_tag and etag == alt_tag.lower():
                    matches.append(content)

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

            if not res and (md5 or sha1):
                print("Checking for hash {} and {}".format(md5, sha1))
                res = self._find_object_by_etag(b, tag=md5, alt_tag=sha1)

            if res:
                # Add the match to the list of matches
                matches.append(res)

        return matches

    def get_file(self, name=None, md5=None, sha1=None):
        """Get a file from Amazon using the name or hashes."""
        raise NotImplementedError


# Register our handler
fileServiceInterface.register(amazonHandler)