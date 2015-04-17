[![Build Status](https://travis-ci.org/Haravan/haravan_python_api.svg?branch=master)](https://travis-ci.org/Haravan/haravan_python_api)
[![Package Version](https://pypip.in/version/HaravanAPI/badge.svg)](https://pypi.python.org/pypi/HaravanAPI)

# Haravan API

The HaravanAPI library allows Python developers to programmatically
access the admin section of stores.

The API is accessed using pyactiveresource in order to provide an
interface similar to the
[ruby Haravan API](https://github.com/haravan/haravan_api) gem.
The data itself is sent as XML over HTTP to communicate with Haravan,
which provides a web service that follows the REST principles as
much as possible.

## Usage

### Requirements

All API usage happens through Haravan applications, created by
either shop owners for their own shops, or by Haravan Partners for
use by other shop owners:

* Shop owners can create applications for themselves through their
own admin: <http://docs.haravan.com/api/tutorials/creating-a-private-app>
* Haravan Partners create applications through their admin:
  <http://app.haravan.com/services/partners>

For more information and detailed documentation about the API visit
<http://api.haravan.com>

### Installation

To easily install or upgrade to the latest release, use
[pip](http://www.pip-installer.org/)

```shell
pip install --upgrade HaravanAPI
```

or [easy_install](http://packages.python.org/distribute/easy_install.html)

```shell
easy_install -U HaravanAPI
```

### Getting Started

HaravanAPI uses pyactiveresource to communicate with the REST web
service. pyactiveresource has to be configured with a fully authorized
URL of a particular store first. To obtain that URL you can follow
these steps:

1.  First create a new application in either the partners admin or
    your store admin. For a private App you'll need the API_KEY and
    the PASSWORD otherwise you'll need the API_KEY and SHARED_SECRET.

2.  For a private App you just need to set the base site url as
    follows:

     ```python
     shop_url = "https://%s:%s@SHOP_NAME.myharavan.com/admin" % (API_KEY, PASSWORD)
     haravan.HaravanResource.set_site(shop_url)
     ```

     That's it you're done, skip to step 6 and start using the API!
     For a partner App you will need to supply two parameters to the
     Session class before you instantiate it:

     ```python
     haravan.Session.setup(api_key=API_KEY, secret=SHARED_SECRET)
     ```

3.  In order to access a shop's data, apps need an access token from that
    specific shop. This is a two-stage process. Before interacting with
    a shop for the first time an app should redirect the user to the
    following URL:

    `GET https://SHOP_NAME.myharavan.com/admin/oauth/authorize`

    with the following parameters:

    ```
    * client_id – Required – The API key for your app
    * scope – Required – The list of required scopes (explained here: http://docs.haravan.com/api/tutorials/oauth)
    * redirect_uri – Optional – The URL that the merchant will be sent to once authentication is complete. Defaults to the URL specified in the application settings and must be the same host as that URL.
    ```

    We've added the create_permision_url method to make this easier, first
    instantiate your session object:

    ```python
    session = haravan.Session("SHOP_NAME.myharavan.com")
    ```

    Then call:

    ```python
    scope=["write_products"]
    permission_url = session.create_permission_url(scope)
    ```

    or if you want a custom redirect_uri:

    ```python
    permission_url = session.create_permission_url(scope, "https://my_redirect_uri.com")
    ```

4.  Once authorized, the shop redirects the owner to the return URL of your
    application with a parameter named 'code'. This is a temporary token
    that the app can exchange for a permanent access token. Make the following call:

    `POST https://SHOP_NAME.myharavan.com/admin/oauth/access_token`

    with the following parameters:

    ```
    * client_id – Required – The API key for your app
    * client_secret – Required – The shared secret for your app
    * code – Required – The code you received in step 3
    ```

    and you'll get your permanent access token back in the response.

    There is a method to make the request and get the token for you. Pass
    all the params received from the previous call (shop, code, timestamp,
    signature) as a dictionary and the method will verify
    the params, extract the temp code and then request your token:

    ```python
    token = session.request_token(params)
    ```

    This method will save the token to the session object
    and return it. For future sessions simply pass the token when
    creating the session object.

    ```python
    session = haravan.Session("SHOP_NAME.myharavan.com", token)
    ```

5.  The session must be activated before use:

    ```python
    haravan.HaravanResource.activate_session(session)
    ```

6.  Now you're ready to make authorized API requests to your shop!
    Data is returned as ActiveResource instances:

    ```python
    shop = haravan.Shop.current()

    # Get a specific product
    product = haravan.Product.find(179761209)

    # Create a new product
    new_product = haravan.Product()
    new_product.title = "Burton Custom Freestyle 151"
    new_product.product_type = "Snowboard"
    new_product.vendor = "Burton"
    success = new_product.save() #returns false if the record is invalid
    # or
    if new_product.errors:
        #something went wrong, see new_product.errors.full_messages() for example

    # Update a product
    product.handle = "burton-snowboard"
    product.save()
    ```

    Alternatively, you can use temp to initialize a Session and execute a command which also handles temporarily setting ActiveResource::Base.site:

     ```python
     with haravan.Session.temp("SHOP_NAME.myharavan.com", token):
        product = haravan.Product.find()
     ```

7.  If you want to work with another shop, you'll first need to clear the session::

     ```python
     haravan.HaravanResource.clear_session()
     ```

### Console

This package also includes the `haravan_api.py` script to make it easy to
open up an interactive console to use the API with a shop.

1.  Obtain a private API key and password to use with your shop
    (step 2 in "Getting Started")

2.  Use the `haravan_api.py` script to save the credentials for the
    shop to quickly log in. The script uses [PyYAML](http://pyyaml.org/) to save
    and load connection configurations in the same format as the ruby
    haravan\_api.

    ```shell
    haravan_api.py add yourshopname
    ```

    Follow the prompts for the shop domain, API key and password.

3.  Start the console for the connection.

    ```shell
    haravan_api.py console
    ```

4.  To see the full list of commands, type:

    ```shell
    haravan_api.py help
    ```

## Using Development Version

The development version can be built using

```shell
python setup.py sdist
```

then the package can be installed using pip

```shell
pip install --upgrade dist/HaravanAPI-*.tar.gz
```

or easy_install

```shell
easy_install -U dist/HaravanAPI-*.tar.gz
```

Note Use the `bin/haravan_api.py` script when running from the source tree.
It will add the lib directory to start of sys.path, so the installed
version won't be used.

To run tests, simply open up the project directory in a terminal and run:

```shell
python setup.py test
```

## Limitations

Currently there is no support for:

* asynchronous requests
* persistent connections

## Additional Resources

* [Haravan API](http://api.haravan.com) <= Read the tech docs!
* [Ask questions on the Haravan forums](http://ecommerce.haravan.com/c/haravan-apis-and-technology) <= Ask questions on the forums!

## Copyright

Copyright (c) 2012 "Haravan inc.". See LICENSE for details.
