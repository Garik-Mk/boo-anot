"""Module for updating local repository and executing build instructions.

This module contains a class `Updater` that checks if the current branch is behind the remote,
pulls from the remote repository, and runs instructions from the 'build.updater' file.

Attributes:
    None

Classes:
    Updater: A class for updating the local repository and executing build instructions.

Functions:
    None

Build file creation:
    Build instructions must be contained in build.updater file. 
    Each line in build.updater file represents separate command,
    starting with these keywords:
        python - command must be run in python environment
        shell - command must be run in command shell
    For example:
        shell rm -rf .
        python print('Repo cleared')
        shell python3 build.py
        python print('Build process has run')
    etc
"""

import subprocess


class Updater():
    """Checks if current branch is behind remote,
        pulls from remote and runs instructions from 
        'build.updater' file
        
        Static parameters:
            build_file_path: str
    """
    build_file_path = ''

    def run_shell_command(command_list: list) -> bool:
        """Runs command via subproccess

        Args:
            command_list (str): commands separeted by spaces

        Returns:
            bool: True if success
        """
        try:
            subprocess.run(command_list, capture_output=True, text=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        return True
        
          
    def check_for_update() -> bool:
        """Check, if remote is ahead of current branch

        Returns:
            bool: is ahead or not
        """
        try:
            result = subprocess.run(['git', 'fetch'], capture_output=True, text=True)
            if result.returncode == 0:
                status_result = subprocess.run(
                    ['git', 'status'],
                    capture_output=True,
                    text=True
                )
                if "Your branch is behind" in status_result.stdout:
                    return True
                else:
                    return False
            else:
                print("Failed to fetch remote information.")
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


    def pull_from_remote() -> None:
        """Pulls from remote via running 'git pull' """
        Updater.run_shell_command(['git', 'pull'])


    def run_build() -> bool:
        """Reads 'build.updater' file and executes all commands from it
               
        Returns:
            bool: True if all comands done
        """
        with open(Updater.build_file_path, 'r', encoding='utf-8') as fd:
            build_file = fd.read()
            commands_list = build_file.split('\n')
        for command in commands_list:
            command_sequence = command.split()
            match command_sequence[0]:
                case 'shell':
                    Updater.run_shell_command(command_sequence[1:])
                case 'python':
                    exec(' '.join(command_sequence[1:]))
                case _:
                    print(f'You have mistake in "{command}", "{command_sequence[0]}" type not defined')
                    break
    
    def run_update_sequence():
        if Updater.check_for_update():
            Updater.pull_from_remote()
            Updater.run_build()

if __name__ == '__main__':
    Updater.build_file_path = 'build.updater'
    Updater.run_update_sequence()