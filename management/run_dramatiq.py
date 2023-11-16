import os
import subprocess
import sys


def run_dramatiq():
    executable_name = 'dramatiq'

    tasks_modules = ['bots.admin_bot.tasks']

    process_args = [
        executable_name,
        '--processes', '3',
        '--threads', '1',
        *tasks_modules,
    ]

    sys.stdout.write(' * Running dramatiq: "%s"\n\n' % " ".join(process_args))

    if sys.platform == 'win32':
        command = [executable_name] + process_args[1:]
        sys.exit(subprocess.run(command))

    os.execvp(executable_name, process_args)


if __name__ == '__main__':
    run_dramatiq()
