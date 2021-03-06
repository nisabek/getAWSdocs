# Fork of Fork of https://github.com/richarvey/getAWSdocs :)

This is a fork of https://github.com/emschmitt/getAWSdocs with some code reorganization, extra parameters and more sources such as "solutions", "reInvent slides"(searchable PDFs), quick starts etc.

While waiting for https://github.com/richarvey/getAWSdocs/pull/11 PR to be merged, I wanted to use the library and went through the code and made it a little bit understandable for myself. Some additional parameters added. 

Original README

## About

One thing that strikes me as odd with Amazon and the documentation on AWS is that there is no download all button, to make it easy to get all the documentation in one go. After creating a simple bash script that kept breaking and needed updating, I decided to rewrite in python to make it a little easier to maintain. You can download Documentation and/or WhitePapers. The script is now pported to Python3 (finally)!

I hope some of you find this useful.

## Requirements

Make sure all these python modules are installed as well as Python3:

 - argparse
 - beautifulsoup4
 - urllib3+
 - urlparse3
 - lxml

example:

```bash
sudo pip install -r requirements.txt
```

## Usage

To get all documents:

```
./getAWSdocs.py -d
```

Downloading all the docs (290 at the time of writing) can take a long time ~20mins.

To get all whitepapers:

```
./getAWSdocs.py -w
```

To get all the [builder libraries](https://aws.amazon.com/builders-library/)

```
./getAWSdocs.py -b
``` 

To get all the "event" slides (mostly re:Invent content)

```
./getAWSdocs.py -e
``` 

To get all the "quick start" solutions

```
./getAWSdocs.py -q
``` 

To get all aforementioned types

```
./getAWSdocs.py -a
``` 

Files that exist on disk will not be re-downloaded (so by default only new sections/files are downloaded). To override this default and force re-download of files that exist on disk, use

```
./getAWSdocs.py -d -f
```

__Note:__ You can use a combination of -d and -w and -b and -s to download all documents at once.

That's it!

Built by Ric: [@ric__harvey](https://twitter.com/ric__harvey)


## More parameters

### Output directory 

Passing `-o` or `--base-output-dir` will configure the output directory (each "type" of document is stored in it's own subdirectory under this directory)

```
./getAWSdocs.py -d -w -b -s --base-output-dir output
```

will create `output` directory, download documents to `output/documents`, whitepapers to `output/whitepapers`, etc.

### Test mode

Can't really call it "test" but it's better than nothing:

passing `-t` makes it download only 5 pdfs (for any type of document), which helps during development.

## Why Download?

You might ask yourself, why would somebody be interested in downloading these pdfs. Here are some example usages:

* No internet access (yes, that still happens)
* Sending PDFs to Kindle for nicer read
* Feeding the output to a desktop search tool like [Recoll](https://www.lesbonscomptes.com/recoll/) for faster, more focused searching
* <your-usecase-here>...