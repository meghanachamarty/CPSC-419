"""Class to generate a nice-looking table from some data and column headers.

Author: Alan D. Weide
Copyright 2022

The table generated by this program has the following properties:
    * The first line has column headers
    * The second line consists of underlines for those column headers
    * The rest of the lines of the table contain formatted rows of the table
        * Format specifiers are in the FormatSpec class; the format_str argument to Table.__init__ should be a string of those letters (currently 'p', 'w', or 't').

A Table can be displayed either by calling __str__ or by iterating through each row of the table and printing it.
"""

import textwrap
import itertools
from enum import Enum
import shutil


class FormatSpec(Enum):
    """Enum class for format specifiers for the columns in the table.

    Possible values:
        PREFORMATTED columns will not have their widths changed. They will be separated into several lines by splitting at each PREFORMAT_SEPARATOR character occurence.
        WRAPPED columns will be wrapped at word boundaries to the appropriate width.
        TRUNCATED columns will have their values truncated to the appropriate width, with a trailing ellipsis (or rather, the string Table._DOTS).
    """

    PREFORMATTED = 'p'
    WRAPPED = 'w'
    TRUNCATED = 't'


class Table:
    """Class for formatting data in an ASCII table.

    The Table class is:
        * (mostly) immutable. Therefore it is imperative to generate all data before creating a table. The instance variable column_widths can be set explicitly, but it is automatically generated according to each row's format specifier so you should not need to do so.
        * addressable. To print the x-th data row in a table, use:
            print(a_table[x])
        * iterable. To print every data row in a table, use:
            for row in a_table:
                # A row is an iterable of strings, with one element per line
                for line in row:
                    print(line)
        * stringifiable. To get a string containing all rows in the table including headers, use str(a_table).

    The statment a_table.headers() is the same as a_table[-1], and they both return an iterable of strings.
    """

    # Default values for some useful constants; these can be overridden at init-time.
    _HEAD_UNDERLINE = " "
    _COLUMN_SEPARATOR = " "
    _MAX_WIDTH = 100
    _PREFORMAT_SEPARATOR = ", "
    _DOTS = "..."
    _DEFAULT_FORMAT = FormatSpec.WRAPPED

    def __init__(self, column_names: list[str], data: list[list[str]], *,
                 head_underline: str = None,
                 col_sep: str = None,
                 format_str: str = None,
                 max_width: int = None,
                 preformat_sep: str = None,
                 dots: str = None) -> None:
        """Initializer for Table class.

        Required positional parameters:
            column_names:
                A list of strings to use as column headers in the table.
            data:
                A list, each item of which is itself a list of strings with the same length as column_names

        Optional keyword parameters:
            head_underline:
                The character to use as the header underline. Default is _HEAD_UNDERLINE.
            col_sep:
                The string to use as a separator between columns. Default is _COLUMN_SEPARATOR.
            format_str:
                Describes how to format each column of the table. If specified, format_str should have one character per column, with each character one of 'p', 'w', or 't'. Default applies _DEF_FORMAT to every column.
            max_width:
                The maximum width of the entire table. Default is _MAX_WIDTH.
            preformat_sep:
                The string used by preformatted columns to denote a newline. Default is _PREFORMAT_SEPARATOR.
            dots:
                The string used as the ellipsis at the end of a trunctated line. Default is _DOTS.
        """

        # Assert argument invariants
        assert all((len(r) == len(column_names) for r in data)),\
            "Each row in data must have the same length as the number of column headers."
        assert (not format_str) or (len(format_str) == len(column_names)),\
            "format_str must have the same length as column_names."
        assert (not format_str) or\
            all(((chr in {spec.value for spec in FormatSpec}) for chr in format_str)),\
            "Each character in format_str must be a valid FormatSpec."
        assert (not head_underline) or (len(head_underline) == 1),\
            "head_underline must be a single character."
        assert (not max_width) or (max_width > 0),\
            "max_width must be positive."

        self._column_names = column_names
        self._data = data
        self._head_underline = head_underline or Table._HEAD_UNDERLINE
        self._col_sep = col_sep or Table._COLUMN_SEPARATOR
        if format_str:
            self._format_spec = [FormatSpec(fmt) for fmt in format_str]
        else:
            self._format_spec = ([Table._DEFAULT_FORMAT] * len(column_names))

        self._max_width = max_width or min(
            Table._MAX_WIDTH, shutil.get_terminal_size((Table._MAX_WIDTH, 24)).columns)
        self._preformat_sep = preformat_sep or Table._PREFORMAT_SEPARATOR
        self._dots = dots or Table._DOTS
        self._column_widths = []

    @property
    def column_widths(self, *, recompute=False) -> list[int]:
        """Computes and returns appropriate column widths for the column names and data.

        This computation is done via the following algorithm:
            1. Compute the longest value in each column
            2. If the total width > self._max_width, then:
                a. Truncate last column such that total width <= self._max_width
                b. If the last column is too narrow, then REDISTRIBUTE.

        The REDISTRIBUTE algorithm is as follows:
            1. Repeatedly remove characters from the widest column that is wider than its header until enough characters have been redistributed or all columns are the same width as their headers (in which case, we will have a table wider than self._max_width).
        """

        if recompute or not self._column_widths:
            # Preliminary computation of the width of each column as the length of the longer of:
            #   - the longest value in that column
            #   - the length of the column name

            columns = tuple(zip(self._column_names, *self._data))
            for fmt, column in zip(self._format_spec, columns):
                # A PREFORMATTED column needs special treatment. A PREFORMATTED column actually contains several lines before any wrapping functions are applied; we want the longest of those lines.
                if fmt == FormatSpec.PREFORMATTED:
                    col_lines = []
                    for row in column:
                        col_lines += (str(x)
                                      for x in row.split(self._preformat_sep))
                    width = max(len(line) for line in col_lines)
                else:
                    width = max((len(str(line)) for line in column))
                self._column_widths.append(width)

            # Redistribute the columns so they fit in self._max_width
            self._column_widths = self._redistribute_widths()

        return self._column_widths

    @column_widths.setter
    def set_column_widths(self, col_widths: list[int]):
        """Setter for column_widths property, providing the capability to manually set the widths of columns in a Table.
        """

        self._column_widths = col_widths

    def lines_for_row(self, row_idx: int) -> list[str]:
        """Generates the lines of text needed to print row row_idx with appropriate formatting, and returns those lines as a list of strings.

        Parameters:
            row_idx:
                The index of the row in data to format; a negative index indicates the header row, and the returned value includes the underline.
        """

        def is_header(idx):
            return idx < 0

        if is_header(row_idx):
            values = self._column_names
        else:
            values = self._data[row_idx]

        # formatted_columns is a list[list[str]] in which each element is a value that has been formatted according to self._col_format
        formatted_columns = []
        for val, width, fmt in zip(values, self.column_widths, self._format_spec):
            value = [val]
            match fmt:
                case FormatSpec.PREFORMATTED:
                    value = val.split(self._preformat_sep)
                case FormatSpec.WRAPPED:
                    value = textwrap.wrap(str(val), width)
                case FormatSpec.TRUNCATED:
                    if len(val) > width:
                        value = [
                            f"{val[:(width-len(self._dots))]}{self._dots}"]
            formatted_columns.append(value)

        # Square off and transpose formatted_columns so each line has one value from each column
        row = [self._col_sep.join(f"{v:<{w}}"
                                  for (v, w) in zip(line, self.column_widths))
               for line in itertools.zip_longest(*formatted_columns, fillvalue="")]

        if is_header(row_idx):
            underline = self._col_sep.join(
                (self._head_underline*w for w in self.column_widths))
            row.append(underline)

        return row

    def headers(self) -> list[str]:
        """Returns list of two strings containing headers and the underline for this Table."""

        return self.lines_for_row(-1)

    def __getitem__(self, row_idx: int) -> str:
        """Enables the use of accessor syntax ([...]) on a Table."""

        return self.lines_for_row(row_idx)

    def __str__(self) -> str:
        """Returns a string that, when printed, displays a table no wider than max_width with each row containing the values from one element of data. It has the following properties.
            * The first line of the table contains the names of the columns, left-aligned in their respective fields
            * The second line of input is a sequence of blocks of head_underline characters, each as wide as the respective column, and each separated by a col_sep character.
            * The reamaining lines of the table are the rows of data, each value formatted according to the formatspec string (described below). Note that this means some rows of data will span multiple lines in the returned string.
        """

        lines = self.headers()
        for row in self:
            lines.extend(row)

        return "\n".join(lines)

    def __len__(self):
        """Returns the number of data rows in this table."""

        return len(self._data)

    def __iter__(self):
        """Returns an iterator for formatted rows of data in this table (does not include the header row).
        """

        self._iter_cnt = 0
        return self

    def __next__(self):
        """Returns the next row of data in this table as a formatted row."""

        if self._iter_cnt == len(self):
            raise StopIteration
        next_row = self[self._iter_cnt]
        self._iter_cnt += 1
        return next_row

# **************************************
# *           BEGIN PRIVATE            *
# **************************************

    def _total_width(self) -> int:
        """Computes and returns the total width of the table."""

        width = sum(self.column_widths) + \
            (len(self._col_sep) * (len(self.column_widths)-1))
        return width

    def _redistribute_widths(self):
        """Redistributes the column widths according to the algorithm described in column_widths.
        """

        # Truncate the rightmost column naively
        redistributed_widths = list(self._column_widths)
        redistributed_widths[-1] = min(
            redistributed_widths[-1],
            self._max_width
            - (self._total_width() - redistributed_widths[-1])
            - (len(self._col_sep) - 1))

        # Helper function for REDISRIBUTE algorithm
        def column_is_wide_enough(
                width: int, header: str, format_spec: FormatSpec, nominal_width: int) -> bool:
            """Returns true iff this column is "wide enough".

            That is, returns True iff the column is at least as wide as:
                * any line of its contents (aka nominal_width), if it is PREFORMATTED, or
                * its header, if it is WRAPPED, or
                * the wider of its header or len(_dots) + 3 characters, if it is TRUNCATED.
            """

            match format_spec:
                case FormatSpec.WRAPPED:
                    return width >= len(header)
                case FormatSpec.PREFORMATTED:
                    return width >= nominal_width
                case FormatSpec.TRUNCATED:
                    return width >= max(len(header), len(self._dots + 3))

            # This code should never be reached; here only to make pylint happy
            assert False

        # Helper function for REDISRIBUTE algorithm
        def next_reducable_column_idx(widths: list[int]) -> int:
            """Returns the index of the widest column that is wider than its header, or -1 if no such column exists.
            """

            # Sort the widths in decreasing order, keeping track of their original indices
            sorted_idxes_and_widths = sorted(
                enumerate(widths), key=lambda t: t[1], reverse=True)

            idx = -1

            # Sweep the widths from highest to lowest, stopping when there is a column that is wide
            # enough to be reducable.
            for i, width in sorted_idxes_and_widths:
                if column_is_wide_enough(
                        width,
                        self._column_names[i],
                        self._format_spec[i],
                        self._column_widths[i]):
                    idx = i
                    break

            return idx

        # Helper function for REDISTRIBUTE algorithm
        def last(itr) -> int:
            return itr[-1]

        # Loop for REDISTRIBUTE algorithm.
        while (to_reduce := next_reducable_column_idx(redistributed_widths)) >= 0 and\
                not column_is_wide_enough(
                    last(redistributed_widths),
                    last(self._column_names),
                    last(self._format_spec),
                    last(self._column_widths)):
            redistributed_widths[to_reduce] -= 1
            redistributed_widths[-1] += 1

        return redistributed_widths