from setuptools import setup, find_packages

setup(name='vedavaapi_ashtadhyayi',
      version='0.1',
      description='Ashtadhyaayi Interpreter by Vedavaapi',
      long_description='This is query interface for analysis of Panini Ashtadhyayi grammar engine for Samskrit language.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='panini samskrit ashtadhyayi vedavaapi',
      url='http://github.com/vedavaapi/ashtadhyayi',
      author='Sai Susarla',
      author_email='sai.susarla@gmail.com',
      license='MIT',
      packages=find_packages(),
      scripts=['bin/genjson.pl'],
      entry_points = {
        'console_scripts' :
            ['paribhasha=vedavaapi.ashtadhyayi.cmdline:vedavaapi.paribhasha',
                            'mahavakya=vedavaapi.ashtadhyayi.cmdline:mahavakya']
      },
#      test_suite='nose.collector',
#      tests_require=['nose'],
      install_requires=[
          'indic_transliteration',
      ],
      include_package_data=True,
      zip_safe=False)
