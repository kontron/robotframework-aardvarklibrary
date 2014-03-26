#!/usr/bin/env python

from setuptools import setup, Command
import sys
sys.path.insert(0, 'src')

class run_build_libdoc(Command):
    description = "Build Robot Framework library documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import robot.libdoc
        except ImportError:
            print "build_libdoc requires the Robot Framework package."
            sys.exit(-1)
        robot.libdoc.libdoc('AardvarkLibrary', 'docs/AardvarkLibrary.html')

def main():
    setup(name = 'robotframework-aardvarklibrary',
            version = '0.1',
            description = 'Aardvark Library for Robot Framework',
            author_email = 'michael.walle@kontron.com',
            package_dir = { '' : 'src' },
            license = 'Apache License 2.0',
            classifiers = [
                'Development Status :: 4 - Beta',
                'License :: OSI Approved :: Apache Software License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Testing',
            ],
            packages = [ 'AardvarkLibrary' ],
            install_requires = [
                'robotframework',
                'pyaardvark >= 0.2',
            ],
            cmdclass = {
                'build_libdoc': run_build_libdoc,
            },
    )

if __name__ == '__main__':
    main()
