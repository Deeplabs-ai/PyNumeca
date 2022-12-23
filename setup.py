from distutils.core import setup
__version__ = 'v0.0.15'

setup(
    name='PyNumeca',  # How you named your package folder (MyLib)
    packages=['PyNumeca',
              'PyNumeca.fine',
              'PyNumeca.preprocessing',
              'PyNumeca.postprocessing',
              'PyNumeca.igg',
              'PyNumeca.reader',
               ],  # Chose the same as "name"
    version=__version__,  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='PyNumeca',  # Give a short description about
    # your library
    author='Marco Sanguineti',  # Type in your name
    author_email='marco.sanguineti.info@gmail.com',  # Type in your E-Mail
    url='https://github.com/GitMarco27/PyNumeca.git',  # Provide either the link to your github or to your website
    download_url='https://github.com/GitMarco27/PyNumeca/archive/refs/tags/v0.0.15.zip',  # I explain this later on
    keywords=['PyNumeca', 'Numeca', 'Python'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'numpy',
        'pandas',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.8'
    ],
)
