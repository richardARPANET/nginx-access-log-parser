NGINX access log parser
================================

This python script parses an NGINX access log and counts the total occurrences of a chosen item within the logs and outputs a dictionary.

In the example.log it processes the "requested file/page" segment, this can be changed to any other segment of the log.

The output is useful when serving media assets as you can serve assets from source and calculate view counts periodically from the NGINX logs using this parser.

Note: if you log files are not in standard format the find() function will need editing accordingly.
