#!/usr/bin/env python3
import urllib
from bs4 import BeautifulSoup
import os
import argparse
import json

from datetime import datetime

from urllib.request import urlopen

from urllib.parse import urlsplit

parser = argparse.ArgumentParser(
    description='AWS Documentation Downloader')
parser.add_argument('-d', '--documentation',
                    help='Download the Documentation', action='store_true', required=False)
parser.add_argument('-w', '--whitepapers', help='Download White Papers',
                    action='store_true', required=False)
parser.add_argument('-b', '--builderlibrary', help='Download Documents in Builder Library',
                    action='store_true', required=False)
parser.add_argument('-s', '--solutions', help='Download Documents in Solutions Library',
                    action='store_true', required=False)
parser.add_argument('-e', '--events', help='Download Documents in Events Library',
                    action='store_true', required=False)
parser.add_argument('-q', '--quick-starts', help='Download Documents in QuickStarts Library',
                    action='store_true', required=False)
parser.add_argument('-c', '--compliance', help='Download Compliance resources',
                    action='store_true', required=False)
parser.add_argument('-a', '--all', help='Activates all file type switches',
                    action='store_true', required=False)
parser.add_argument('-f', '--force', help='Overwrite old files',
                    action='store_true', required=False)
parser.add_argument('-o', '--base-output-dir',
                    help="Base for output directory. Each document type is saved into it's own subdirectory(whitepaper for whitepaper, etc). Defaults to current directory",
                    required=False, default="output")
parser.add_argument('-p', '--page-size', help="pagination size for files", required=False,
                    default=15)
parser.add_argument('-t', '--test-mode', help="when set, limits the documents to 5 for testing",
                    required=False, default=False, action='store_true')
args = parser.parse_args()

force = args.force
base_output_dir = args.base_output_dir
page_size = args.page_size
test_mode = args.test_mode

def dateconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


def pretty_info(data, message_prefix=''):
    debug_str = json.dumps(data, indent=4, default=dateconverter)
    print(f'{message_prefix} {debug_str}')


def list_pdfs(source_url, download_url_key):
    responseAsJson = json.loads(urlopen(source_url).read().decode('UTF-8'))
    maxNumberofDocuments = responseAsJson['metadata']['totalHits']
    print("Number of pdfs to be retrieved: " + str(maxNumberofDocuments))
    maxPage = maxNumberofDocuments // page_size + 1
    print("Number of iterations :" + str(maxPage))
    pdfs = set()
    currentPage = 0
    print("Generating PDF list (this may take some time)")
    while currentPage < maxPage:
        responseAsJson = json.loads(
            urlopen(f"{source_url}&page={currentPage}").read().decode('UTF-8'))
        for item in responseAsJson['items']:
            # pretty_info(item['item'])
            item_additional_fields = item['item']['additionalFields']
            if download_url_key in item_additional_fields:
                print("URL to be added to pdf list: " + item_additional_fields[download_url_key])
                pdfs.add(item_additional_fields[download_url_key])
                if test_mode and len(pdfs) >= 5:
                    print('test_mode is on, stopping here...')
                    return pdfs
            else:
                print(f'{source_url} does not contain field {download_url_key}')
        currentPage += 1
    return pdfs


def list_builderlibrary_pdfs():
    builder_library_url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=amazon-redwood&sort_by=item.additionalFields.customSort&sort_order=asc&size={page_size}&item.locale=en_US"
    return list_pdfs(builder_library_url, 'downloadUrl')

def list_solutions_pdfs():
    solutions_url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=solutions-master&sort_by=item.additionalFields.sortDate&sort_order=asc&size={page_size}&item.locale=en_US"
    return list_pdfs(solutions_url, 'downloadUrl')

def list_compliance_pdfs():
    compliance_resources = f"https://aws.amazon.com/compliance/resources/"
    return find_pdfs_in_html(compliance_resources)

def list_whitepaper_pdfs():
    whitepaper_url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=whitepapers&sort_by=item.additionalFields.sortDate&sort_order=desc&size={page_size}&item.locale=en_US"

    return list_pdfs(whitepaper_url, 'primaryURL')

def list_events_pdfs():
    events_url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=event-content&sort_by=item.dateCreated&sort_order=desc&size={page_size}&item.locale=en_US"

    return list_pdfs(events_url, 'headlineUrl')


def list_quickstart_pdfs():
    quickstart_url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=quickstart-content&sort_by=item.additionalFields.updateDate&sort_order=desc&size={page_size}&item.locale=en_US"

    return list_pdfs(quickstart_url, 'guideUrl')


def find_pdfs_in_html(url):
    html_page_doc = urlopen(url)
    soup_doc = BeautifulSoup(html_page_doc, 'html.parser')
    # Get the A tag from the parsed page
    pdfs = set()
    for link in soup_doc.findAll('a'):
        try:
            sub_url = link.get('href')
            if sub_url.endswith("pdf"):
                pdfs.add(sub_url)
        except:
            continue
    return pdfs


def list_docs_pdfs(start_page):
    locale_path = "en_us/"
    base_url = "http://docs.aws.amazon.com"

    page = urlopen(start_page)
    soup = BeautifulSoup(page, "xml")
    pdfs = set()
    print("Generating PDF list (this may take some time)")

    for link in soup.findAll('service'):
        try:
            uri = link.get('href')
            print('URI: ', uri)
            # if service uri is .html then parse as HTML
            if '.html' in uri:
                url = base_url + uri
                pdfs = pdfs.union(find_pdfs_in_html(url))
                continue

            # if service uri ends with "/" find and parse xml landing page
            if not uri.startswith('http'):
                url = base_url + \
                      uri.split("?")[0] + locale_path + "landing-page.xml"

            # Fetch the XML sub page (this is where the links to the pdf's live)
            sub_page_doc = urlopen(url)
            soup_doc = BeautifulSoup(sub_page_doc, 'xml')

            # Get the "tile" tag from the parsed page
            for sublink in soup_doc.findAll('tile'):
                try:
                    sub_url = sublink.get('href')
                    directory = base_url + \
                                "/".join(urlsplit(sub_url).path.split('/')[:-1])

                    guide_info_url = directory + "/meta-inf/guide-info.json"
                    print("Guide info url:", guide_info_url)
                    guide_info_doc = urlopen(guide_info_url).read()
                    guide_info = json.loads(guide_info_doc)

                    if "pdf" in guide_info:
                        pdf_url = directory + "/" + guide_info["pdf"]
                        pdfs.add(pdf_url)
                        if test_mode and len(pdfs) >= 5:
                            print('test_mode is on, stopping here...')
                            return pdfs
                except:
                    continue
        except:
            continue
    return pdfs


def save_pdf(full_dir, filename, pdf_url, force):
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
    # Open the URL and retrieve data
    file_loc = full_dir + filename
    if not os.path.exists(file_loc) or force == True:
        if pdf_url.startswith("//"):
            pdf_url = "http:" + pdf_url
        print("Downloading : " + pdf_url)
        web = urlopen(pdf_url)
        print("Saving to : " + file_loc)
        # Save Data to disk
        output = open(file_loc, 'wb')
        output.write(web.read())
        output.close()
    else:
        print(
            "Skipping " + pdf_url + " - file exists or is a dated API document, use './getAWSdocs.py --force' to force override")


def get_pdfs(pdf_list, force, output_dir):
    for pdf_url in pdf_list:
        if not "pdf" in pdf_url:
            try:
                pdf_url = urlopen(pdf_url).geturl()
            except:
                print(f"Error trying to get url for {pdf_url}, will continue")
                continue
            if not "pdf" in pdf_url:
                print(f"Skipping {pdf_url} - doesn't seem to be a pdf url")
                continue
        filename = urlsplit(pdf_url).path.split('/')[-1]
        full_dir = f'{output_dir}/'
        directory = urlsplit(pdf_url).path.split('/')[:-1]
        for path in directory:
            if path != "":
                full_dir = full_dir + path + "/"
        try:
            save_pdf(f'{base_output_dir}/{full_dir}', filename, pdf_url, force)
        except:
            continue

def main1():
    pdf_list = []
    if args.documentation or args.all:
        print("Downloading Docs")
        pdf_list = list_docs_pdfs(
            "https://docs.aws.amazon.com/en_us/main-landing-page.xml")
        get_pdfs(pdf_list, force, "documentation")
    if args.whitepapers or args.all:
        print("Downloading Whitepapers")
        pdf_list = list_whitepaper_pdfs()
        get_pdfs(pdf_list, force, "whitepapers")
    if args.builderlibrary or args.all:
        print("Downloading Builder Lib documents")
        pdf_list = list_builderlibrary_pdfs()
        get_pdfs(pdf_list, force, "builderslibrary")
    if args.solutions or args.all:
        print("Downloading solutions")
        pdf_list = list_solutions_pdfs()
        get_pdfs(pdf_list, force, "solutions")
    if args.events or args.all:
        print("Downloading events")
        pdf_list = list_events_pdfs()
        get_pdfs(pdf_list, force, "events")
    if args.quick_starts or args.all:
        print("Downloading Quick Starts")
        pdf_list = list_quickstart_pdfs()
        get_pdfs(pdf_list, force, "quickstarts")
    if args.compliance or args.all:
        print("Downloading Compliance Resources")
        pdf_list = list_compliance_pdfs()
        get_pdfs(pdf_list, force, "compliance")
    for p in pdf_list:
        print(p)


if __name__ == '__main__':
    main1()
