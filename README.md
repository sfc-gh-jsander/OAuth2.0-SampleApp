# OAuth2.0-SampleApp
Sample app to exercize the OAuth2.0 features of the Snowflake platform

# Before Using
You should read and follow all the steps here: https://docs.snowflake.net/manuals/user-guide/oauth-custom.html

If you do not have either Snowflake or OAuth set up, then the rest of this will not help you. This was built and tested on ubuntu using Python 3.6.7 and openjdk 10.0.2. Support for lower version of either is not assured, and there are absolutely modules and other Python 3 dependancies. Review the Python code carefully to ensure compatability with your testbed.

# Steps to Use

1. Download all the files and put them in a directory of your choice. 
2. Touch a file named '__init__.py' in order to allow for a dynamic module to be picked up. 
3. javac the OAuthJDBCTest.java code to create a OAuthJDBCTest.class file. 
4. Edit the OAuth2_0-SampleApp.ini for your Snowflake registered client following the instructions in the file's comments. 
5. Launch the OAuth2_0-SampleApp.py file using 'python3 ./OAuth2_0-SampleApp.py' or equivalent. 
6. Navigate to the application's URL with a browser and follow on screen instructions. 

Message me with issues. 
