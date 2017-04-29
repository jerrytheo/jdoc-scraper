# jDoc Scraper

Set of scripts that crawl the online [Java documentation](http://docs.oracle.com/javase/7/docs/api/overview-summary.html) to scrape information about the methods and constructors of each class, organised by package names. The result of the scrape is stored as XML files, with each file corresponding to one Java package.

## XML Structure
The structure of the xml file for one package is as follows (the bracketed terms indicate attributes),
```
package
    ├── name
    ├── description
    ├── class (id)
    │     ├── name
    │     └── description
    └── method (id)
          ├── name
          ├── description
          ├── parameter
          │     ├── name
          │     └── type
          ├── return
          └── class
```

## Modules
There are three modules and one script present in this package,

1. `class_scraper.py` --- Contains `scrape_class(soup, cls_name)` that takes a `BeautifulSoup` object and the class name, and scrapes the class' web page to retrieve the class description, and the name, description, parameters and return type of each method belonging to the class.

2. `package_scraper.py` --- Contains `scrape_package(package_name, package_url)` that takes the name and url of the package to be scraped, generates the list of classes in the package, retrieves the web page of each class and generates the `BeautifulSoup` object for the web page, calls `scrape_class` for each class, and then calls `write_xml` on the data returned from `scrape_class`.

3. `doc_scrape.py` --- Executable script that reads the package list from `pkg_list.json` and calls `scrape_package` on each package. Also responsible for printing the results of the operation.

4. `misc.py` --- Contains two functions,
    1. `get_absolute_url(current_url, relative_url)` --- Generates an absolute url from the current url and a url specified relative to the current url.
    2. `write_xml(package_info)` --- Generates the XML tree from the package info and writes it to a file at `docs/<package name>.xml`.

The function `scrape_package` executes `scrape_class` for each class on a separate thread, up to a maximum of 32 threads using `concurrent.futures.ThreadPoolExecutor`. Further, the `doc_scrape.py` script executes `scrape_package` for each package on a separate process, with a maximum of 8 concurrent processes.

## Dependencies

The scripts have been written for Python 3.6.0 and require the following external packages, installable via `pip`,
- `requests 2.13.0`
- `lxml 3.7.3`
- `beautifulsoup4 4.5.3`

Further, execution of the script has not been verified on any operating system other than Arch Linux.

## Usage

The file `pkg_list.json` contains all packages and their associated urls in the JSON format. This file can be backed up and edited to reduce the number of packages to scrape. Running the script `doc_scrape.py` starts the scraper.
```
$ ./doc_scrape.py
```
The output of `./doc_scrape.py` is as follows,
- There are 5 columns --- status, package, done, total, errors.
- Each row corresponds to the result of the scrape for one package, indicated by the package column.
- The first column, status, indicates the overall result.
    - `SUCCESS`: All classes successfully parsed.
    - `PARTIAL`: A few classes could not be parsed.
    - `FAILURE`: No classes could be parsed.
- The third and fourth columns indicate the number of classes successfully parsed and the total number of classes in the package respectively. These values are identical on the status `SUCCESS`, differ on `PARTIAL`, and are marked with `-` on `FAILURE`.
- The last column prints the error during a `FAILURE`.
- Finally, after the scraping is complete, there are 4 values presented,
    - Total packages: Total packages scraped.
    - Complete: Number of packages with `SUCCESS` status.
    - Incomplete: Number of packages with `PARTIAL` status.
    - Failed: Number of packages with `FAILURE` status.
    - Empties: Number of packages with no classes. These packages do not show up on the output table.

Apart from the standard output, log files in the `logs` folder indicate the errors associated with parsing a class when the package has reported a `PARTIAL` status. These files are named `<package name>.log`.

`doc_scape.py` may also be called as,
```
$ ./doc_scrape.py --retry
```

The retry flag reads a file `pkg_retry`, if it exists, and only parses those packages specified there. Every time `doc_scrape.py` is executed, all those packages that fail, or are partially scraped are written to `pkg_retry`. This allows the scraping to resume from only those packages that have failed the previous time.

> **WARNING** Currently, the `logs`, `docs` and `pkg_retry` files are overwritten on each execution of `doc_scrape.py`.

Finally, there is one convenience script included, `clean.py`, that removes `docs`, `logs`, `__pycache__`, and `pkg_retry` after a prompt for each. Calling `clean.py` with the option `--force` skips the prompt.
```
$ ./clean.py
```
or,
```
$ ./clean.py --force
```

## License

This software is licensed under the MIT License.  
For further information, view LICENSE.  
Copyright (C) 2017 Abhijit J. Theophilus, abhitheo96@gmail.com
