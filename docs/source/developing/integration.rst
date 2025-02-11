.. _integration:

=========================================
Integrating AttackMate in a Python Script
=========================================

It is possible to integrate AttackMate into a Python script for automation and custom attack scenarios.
This feature is under development and may change in the future. Bug reports are welcome.

Installation
============

Before using AttackMate in a script, ensure it is installed.

Example Script
==============

Below is an example of how to integrate AttackMate into a Python script.
Configs and Variable Store can be passed as a dictionary or as a Config object.
Commands can be created with the Command.create() method and passed to the run_command() method.

::

    from attackmate.attackmate import AttackMate
    from attackmate.command import Command
    from attackmate.variablestore import VariableStore
    from attackmate.schemas.config import Config

    def main():
        ### Optional: define config manually
        config = Config(
            sliver_config={"config_file": "path/to/config/file"},
            msf_config={"password": "your_password", "ssl": True, "port": 55553},
            cmd_config={"loop_sleep": 10}
        )

        ### Optional: varstore can be passed as a dictionary
        varstore = {"TEST": "test"}

        attackmate = AttackMate(config=config, varstore=varstore)

        command1 = Command.create(type="sleep", cmd="sleep", seconds="1")
        command2 = Command.create(type="debug", cmd="$TEST", varstore=True)

        result1 = attackmate.run_command(command1)
        result2 = attackmate.run_command(command2)

        print(result1)
        print(result2)

    if __name__ == "__main__":
        main()

Running the Script
==================

To execute the script, save it as `attackmate_script.py` and run:

::

  $ python attackmate_script.py

If AttackMate is configured correctly, it will execute the commands and print the results.

.. note::
   Reguler Commands return a Result object.
   Commands that run in Background Mode do not return a Result object.

Understanding the Result Object
===============================

When executing a command with AttackMate, the result is returned as an instance of the `Result` class. This object contains the standard output (`stdout`) and the return code (`returncode`) of the executed command.
Commands that run in the Background return Result(None,None)

Attributes
----------

- **stdout (str)**: The standard output of the executed command.
- **returncode (int)**: The return code indicating the success or failure of the command.

Example Usage
-------------

The `Result` object can be used to check the output and status of a command execution:

::

    result = attackmate.run_command(command)

    print("Command Output:", result.stdout)
    print("Return Code:", result.returncode)

Handling Results
----------------

The return code can be used to determine if the command was successful:

::

    if result.returncode == 0:
        print("Command executed successfully.")
    else:
        print(f"Command failed with return code {result.returncode}")