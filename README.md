Quicksite
---------

Sets up a website by creating a S3 AWS bucket and add a subdomain record to an existing site in Cloudflare.  


## Installation

git clone https://github.com/gridcell/quicksite.git
python setup.py install


## Environment Variables

```
AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
AWS_REGION=<AWS_REGION>
CF_API_EMAIL=<Cloudflare Email>
CF_API_KEY=<Cloudflare Global API Key>
CF_API_CERTKEY=<Cloudflare Origin CA Key>
```

## Usage

```
# quicksite deploy <DOMAIN> <SUB DOMAIN>
quicksite deploy abc.com mysite
```
Creates S3 bucket named `mysite.abc.com` and adds a DNS record to Cloudflare called `mysite`.


```
# quicksite undeploy <DOMAIN> <SUB DOMAIN>
quicksite undeploy abc.com mysite
```
Deletes S3 bucket named `mysite.abc.com` and removes a DNS record to Cloudflare called `mysite`.