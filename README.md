# kindle-to-md

A small tool that allows you to download annotations you have made on your Kindle via the Kindle Store and transforms them into markdown notes.


## Example

This is how the output looks:

> [!quote] Position 266:
> Markets, the medium of capitalism, have been replaced by digital trading platforms which look like, but are not, markets, and are better understood as fiefdoms. And profit, the engine of capitalism, has been replaced with its feudal predecessor: rent.

> [!quote] Position 268:
> I call it cloud rent.


## Installation

```bash
git clone https://github.com/anakles/kindle-to-md.git
cd kindle-to-md
pip install -r requirements
```

**Requirements**
The tool requires you to have `fzf` installed on your system.


## Usage

The script, when called, asks you for a cookie.
You can get this cookie by logging into the Kindle Store in any browser. Only the following cookies are required:

- `at-main` is necessary
- `x-main` is necessary
- `ubid-main` is necessary

You can copy the cookie from your browser's developer tools in the "Network" or "Storage" tab.
Paste the cookie value into the prompt and confirm with Enter. The value of the cookie is not reflected.

You can select the book you want to export your annotations for withing `fzf`.


```bash
❯ python kindle-to-md.py -h
usage: kindle-to-md.py [-h] output_path

Fetch data from a predefined URL using a provided cookie.

positional arguments:
  output_path  Path to save the output file

options:
  -h, --help   show this help message and exit
```


**Example Usage:**

```bash
❯ python kindle-to-md.py output/
Enter the cookie: *****
You selected: {'ASIN': 'B0BS37DHM3', 'Title': 'Technofeudalism: What Killed Capitalism', 'Author': 'Yanis Varoufakis', 'Date': 'Friday March 14, 2025'}
Annotations fetched successfully!
Data successfully saved to output/Technofeudalism: What Killed Capitalism
```
