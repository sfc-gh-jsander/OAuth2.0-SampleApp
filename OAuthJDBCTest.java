/*
###################################################################
###################################################################
##        The MIT License - SPDX short identifier: MIT           ##
###################################################################
###################################################################
#
#Copyright 2019 @sanderiam & https://github.com/snowflakedb
#
#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the "Software"),
#to deal in the Software without restriction, including without
#limitation the rights to use, copy, modify, merge, publish, distribute,
#sublicense, and/or sell copies of the Software, and to permit persons
#to whom the Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# Please consider this script an example.
# Do not use this in any production scenario

*/

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

public class OAuthJDBCTest {
  public static void main(String[] args) throws Exception
  {
    if (args.length != 3)
    {
      System.out.println("Please run with an OAuth Access Token and account name!");
      return;
    }


    // get connection
    Connection connection = getConnection(args[0], args[1]);
    if (connection == null)
    {
      return;
    }

    // use connection to run the statement
    Statement statement = connection.createStatement();
    ResultSet resultSet = statement.executeQuery("SELECT NAME, TEAM FROM SCIFI_FANTASY.PUBLIC.MARVEL_CHARACTERS");

    int rowIdx = 0;
    while (resultSet.next()) {
    	System.out.println(resultSet.getString(1) + ", " + resultSet.getString(2));
    }

    resultSet.close();
    statement.close();

    // System.out.println("Done creating JDBC connection\n");
    connection.close();
  }

  /**
   * Gets a connection via the OAuth Authenticator
   */
  private static Connection getConnection(String oAuthAccessToken, String accountName)
      throws SQLException
  {
    try
    {
      Class.forName("net.snowflake.client.jdbc.SnowflakeDriver");
    }
    catch (ClassNotFoundException ex)
    {
      System.err.println("Driver not found");
      return null;
    }

    String connectStr = "jdbc:snowflake://";
    connectStr += accountName;
    connectStr += ".us-east-1.snowflakecomputing.com";

    // build connection properties. Note that username is optional
    // and role can be omitted
    Properties properties = new Properties();
    properties.put("account", accountName);
    properties.put("authenticator", "OAUTH");
    properties.put("token", oAuthAccessToken);
    return DriverManager.getConnection(connectStr, properties);
  }
}
