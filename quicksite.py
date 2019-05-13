import json
import os

import botocore
import botocore.loaders
import botocore.regions
import requests

import boto3
import click
import CloudFlare
import magic

s3 = boto3.resource("s3")
cf = CloudFlare.CloudFlare()

AWS_REGION = os.environ.get("AWS_REGION")


# CLOUDFLARE


def get_zone_id(domain):
    zones = cf.zones.get(params={"per_page": 100})
    for zone in zones:
        if domain == zone["name"]:
            return zone["id"]
    return None


def get_dns_records(zone_id):
    return cf.zones.dns_records.get(zone_id)


def get_dns_record(zone_id, dns_name):
    dns_records = get_dns_records(zone_id)
    for dns_record in dns_records:
        if dns_record["name"] == dns_name:
            return dns_record
    return None


def add_dns_record(zone_id, name, content):
    dns_record = dict(name=name, type="CNAME", content=content, proxied=True)
    r = cf.zones.dns_records.post(zone_id, data=dns_record)
    # try:
    #     r = cf.zones.dns_records.post(zone_id, data=dns_record)
    # except CloudFlare.CloudFlareAPIError as e:
    #     exit("/zones.dns_records.post %s - %d %s" % (record["name"], e, e))


def delete_dns_record(zone_id, dns_name):
    dns_record = get_dns_record(zone_id, dns_name)
    if dns_record is None:
        print("Warning: DNS record doesn't exist")
        return
    cf.zones.dns_records.delete(zone_id, dns_record["id"])


# AWS


def get_bucket_name(subdomain, domain):
    return "{}.{}".format(subdomain, domain)


def get_endpoint_for_s3_bucket(bucket_name, region="us-west-2"):
    loader = botocore.loaders.create_loader()
    data = loader.load_data("endpoints")
    resolver = botocore.regions.EndpointResolver(data)
    endpoint_data = resolver.construct_endpoint("s3", region)
    parts = endpoint_data["hostname"].split(".", 1)
    parts.insert(1, "website")
    url = "{}.{}".format(bucket_name, "-".join(parts))
    return url


def get_bucket(bucket_name):
    return s3.Bucket(bucket_name)


def create_bucket_policy(bucket_name):
    bucket_policy = s3.BucketPolicy(bucket_name)
    bucket_policy.put(
        Policy=json.dumps(
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": [
                            "arn:aws:s3:::{}".format(bucket_name),
                            "arn:aws:s3:::{}/*".format(bucket_name),
                        ],
                    }
                ]
            }
        )
    )


def create_bucket_website(
    bucket_name, index_document="index.html", error_document="error.html", **kwargs
):
    bucket = s3.BucketWebsite(bucket_name)
    bucket.put(
        WebsiteConfiguration={
            "ErrorDocument": {"Key": error_document},
            "IndexDocument": {"Suffix": index_document},
        }
    )
    return bucket


def create_bucket(bucket_name, region=None):
    region = region or AWS_REGION
    return s3.create_bucket(
        Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region}
    )


@click.group()
def cli():
    pass


@cli.command()
@click.argument("domain")
@click.argument("subdomain")
def deploy(domain, subdomain):

    # Setup AWS
    bucket_name = get_bucket_name(subdomain, domain)
    bucket = create_bucket(bucket_name)
    create_bucket_website(bucket_name)
    create_bucket_policy(bucket_name)

    # Setup Cloudflare
    url = get_endpoint_for_s3_bucket(bucket_name, AWS_REGION)
    zone_id = get_zone_id(domain)
    add_dns_record(zone_id, subdomain, url)
    print("https://{}".format(bucket_name))


@cli.command()
@click.argument("domain")
@click.argument("subdomain")
def undeploy(domain, subdomain):
    _s3 = boto3.client("s3")
    zone_id = get_zone_id(domain)

    bucket_name = get_bucket_name(subdomain, domain)
    bucket = get_bucket(bucket_name)
    try:
        bucket.objects.all().delete()
        bucket.delete()
    except _s3.exceptions.NoSuchBucket:
        print("Warning: bucket doesn't exist")
    delete_dns_record(zone_id, bucket_name)
