Domain Analyzer
===============

An application that retrieves certain information from remote hosts via HTTP using selenium webdrivers.
Launch it simply as follows: `python analyzer.py`

Basic workflow
--------------
1. Get .com domains from [domainpunch](https://domainpunch.com/tlds/daily.php)
2. Check if domain matches given regex
3. If it does, check if exists in the given whitelist
4. If it does not, make a screenshot using a web browser and retrieve meta information from the domain main page

Further improvements
--------------------
This is just a prototype, so here is a list of possible improvements / features / things to do:

* Provide command line argument parsing, so that users could feed in whitelist and regex list for example as a file
* Make default values configurable, parse it with ConfigParser
* Cover the codebase with tests, where it makes sense
* Provide proper packaging with setup.py, requirements.txt
* Make the app asyncronous somehow (domain list retrieving maybe?)
* Store results in some DB instead of file dump
