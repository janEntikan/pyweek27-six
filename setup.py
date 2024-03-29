from setuptools import setup

import pman.build_apps

CONFIG = pman.get_config()

APP_NAME = CONFIG['general']['name']

setup(
    name=APP_NAME,
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pylint',
        'pytest-pylint',
    ],
    cmdclass={
        'build_apps': pman.build_apps.BuildApps,
    },
    options={
        'build_apps': {
            'include_patterns': {
                'game/**',
                '.pman',
            },
            'rename_paths': {
                'game/': './',
            },
            'include_modules': {
                '*': [
                    'pkg_resources._vendor.packaging',
                    'pkg_resources._vendor.packaging.version',
                    'pkg_resources._vendor.packaging.specifiers',
                    'pkg_resources._vendor.packaging.utils',
                    'pkg_resources._vendor.packaging.requirements',
                ],
            },
            'gui_apps': {
                APP_NAME: CONFIG['run']['main_file'],
            },
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
        },
    }
)
