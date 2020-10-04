# OAuth2.0-SampleApp
Sample app to exercize the OAuth2.0 features of the Snowflake platform

# Before Using
You should read and follow all the steps here: https://docs.snowflake.net/manuals/user-guide/oauth-custom.html

If you do not have either Snowflake or OAuth set up, then this app will not help you. 

This was built and tested on ubuntu using Python 3.8.2 and AdoptOpenJDK build 11.0.8+10. Support for lower version of either is not assured, and there are modules and other Python 3 dependancies. Review the Python code carefully to ensure compatability with your testbed.

# Steps to Use

1. Download all the files and put them in a directory of your choice. 
2. Compile the OAuthJDBCTest.java code to create a OAuthJDBCTest.class file using a command similar to `javac -cp /path/to/the/OAuth2.0-SampleApp:/path/to/the/snowflake-jdbc-3.12.9.jar OAuthJDBCTest.java`. Note that the Snowflake JDBC jar can be located anywhere so long as you use a full path and name in the classpath.
3. Edit the OAuth2_0-SampleApp.ini for your Snowflake registered client following the instructions in the file's comments. 
4. Launch the OAuth2_0-SampleApp.py file using `python3 ./OAuth2_0-SampleApp.py` or equivalent. If all is well, you will see `Bottle v0.12.18 server starting up (using WSGIRefServer())...
Listening on http://0.0.0.0:8088/
Hit Ctrl-C to quit.` Note that if you're running the app in a container you will need to expose the port for the app to the host machine to use your regular browser.
5. Navigate to the app's URL with a browser and follow on screen instructions. 

# Expected Issues
1. When running your query using Python expect a warning similar to `/usr/lib/python3/dist-packages/urllib3/connectionpool.py:999: InsecureRequestWarning: Unverified HTTPS request is being made to host 'login.microsoftonline.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings` Since we won't have a proper certificate handling these requests in many cases while using this app, it's expected. Of course, if you're planning to use this as a model for anything more serious than testing OAuth features, then you should address this and put proper certs in place. 

Message me with issues. 
