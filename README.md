# Lab File Checker

Lab file checker is a set of simple rules in order to guarantee the that the excel file doesn't contain any corrupt or incorrect data.

## Installation

To install the tool, clone the github repository locally and install it using pip.

Requirements:

- python >=3.7
- pip

### Downloading the tool from the repository

```
pip install https://github.com/Joon-Klaps/LabFileChecker/archive/refs/heads/master.zip
```

You're all setup!

> It's possible that the required packages versions are clashing with those locally installed, if this is the case try creating a local environemnt using `conda create labfilechecker-env python=3.9.16` and try building again with `pip install`
>
> > if this also fails try `pip --upgrade --force-reinstall https://github.com/Joon-Klaps/LabFileChecker/archive/refs/heads/master.zip` to really force the installation

### Updating the installation

Updating is done again with pip:

```
pip install --upgrade https://github.com/Joon-Klaps/LabFileChecker/archive/refs/heads/master.zip
```

## Usage

```bash
$ labfilechecker --help
 Usage: labfilechecker [OPTIONS] FILE

 Arguments:
*    file      TEXT  [default: None] [required]

Options:
--config                TEXT        configuration file used to check the excel file. [default: config sheet in [file]]
--export-config  --no-export-config save the configuration .yml file. [default: no-export-config]
--skiprows              INTEGER     Number of rows to skip at the beginning of the excel file. [default: 1]
--help                              Show this message and exit.
```

It requires two files:

- an excel file containing the necessary data to check
- a config file. If none is it will assume that in the given excel a sheet named 'config' is availble which contains information on which columns to check. A yml file can also be given.

### The config file

The config file contains the necessary information to determine the type of tests executed on certain columns.
Currently the following columns/keys are supported:

- Column_name
  - value: `name_of_column`
- Column_type
  - value: `unique-id|numeric|date|text`
- Allowed_values
  - value: `allowed,value,in,columns`, a series of values seperated by a single `,` the string will be split up based on `,`so spaces are not removed
- Is_referring_to:
  - value: `column_my_value_is_based_on` is used in test to check if the value exists in the column it's referring to.
- Separation_character
  - value: `_|+|;|...` a character seperation if the given values are a constructed of multiple values from another column. Values will be split up based on the given character
- Unique_with
  - value: `with_this_column_the_following_values_are_unique`, the combination of the two columns make the coming values unique and are uniquely associated to the row (if the row is not a continuation of another row).

### Terminal output

The terminal will display the results and show how many tests have `failed`, `warned` or `passed`.

- `failed` tests show critical errors, that will make data integration extremely more challenging and labour intensive
- `warned` tests show warnings, which mostly correspond to data loss when being intergrated in a database
- `passed` tests show tests that completed without any issues.

All results are displayed in a table format that contain the identified row, the column, the type of test and a message that will help to solve the issue.

A snapshot of the result is shown:
!(assets/images/snapshot_failed_tests.png)
