====
json
====

Parse JSON into variables and store them in the variable store. Input can be either a
JSON file (via ``local_path``) or a variable containing a valid JSON string (via ``cmd``).
If ``local_path`` is set, ``cmd`` is ignored.

Keys are flattened recursively into variable names by joining each level with an underscore
(``_``). Lists of primitives (strings, integers, etc.) are preserved as-is without further
flattening. List elements that are objects are indexed numerically (e.g. ``friends_0_name``).

Example
-------

Given the following JSON input:

.. code-block:: json

   {
     "first_list": [1, 2, 3],
     "user": {
       "name": "John Doe",
       "age": 30,
       "address": {
         "street": "123 Main St",
         "city": "New York",
         "postal_codes": [10001, 10002]
       },
       "friends": [
         {
           "name": "Jane Smith",
           "age": 28,
           "address": {
             "street": "456 Oak Rd",
             "city": "Los Angeles",
             "postal_codes": [90001, 90002]
           }
         },
         {
           "name": "Emily Davis",
           "age": 35,
           "address": {
             "street": "789 Pine Ln",
             "city": "Chicago",
             "postal_codes": [60007, 60008]
           }
         }
       ]
     }
   }

The variables will be saved in the variable store:

.. code-block:: yaml

   first_list: [1, 2, 3]
   user_name: "John Doe"
   user_age: 30
   user_address_street: "123 Main St"
   user_address_city: "New York"
   user_address_postal_codes: [10001, 10002]
   user_friends_0_name: "Jane Smith"
   user_friends_0_age: 28
   user_friends_0_address_street: "456 Oak Rd"
   user_friends_0_address_city: "Los Angeles"
   user_friends_0_address_postal_codes: [90001, 90002]
   user_friends_1_name: "Emily Davis"
   user_friends_1_age: 35
   user_friends_1_address_street: "789 Pine Ln"
   user_friends_1_address_city: "Chicago"
   user_friends_1_address_postal_codes: [60007, 60008]

Configuration
-------------

.. note::

   Either ``local_path`` or ``cmd`` must be provided.

.. confval:: local_path

   Path to a JSON file to parse. Takes precedence over ``cmd`` if both are set.

   :type: str
   :required: Either ``local_path`` or ``cmd`` must be provided.

.. confval:: cmd

   Name of a variable in the variable store (without the leading ``$``) whose value
   is a valid JSON string.

   :type: str
   :required: Either ``local_path`` or ``cmd`` must be provided.

.. confval:: varstore

   Log the variable store before and after the command executes, useful for debugging.

   :type: bool
   :default: ``False``
   :required: False

Examples
--------

Parse a JSON file directly:

.. code-block:: yaml

   commands:
     - type: json
       local_path: "/path/to/samplefile.json"
       varstore: True

Parse JSON from a shell command's output:

.. code-block:: yaml

   commands:
     - type: shell
       cmd: |
         cat <<EOF
         {
           "name": "Whiskers",
           "favorite_toys": ["ball", "feather", "laser pointer"]
         }
         EOF

     - type: json
       cmd: RESULT_STDOUT
