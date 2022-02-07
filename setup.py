from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='toeplitz',
      version='0.1',
      description='Toeplitz hashing algorithm for post-processing Quantum Random Number Generation',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Topic :: Security :: Cryptography',
      ],
      url='https://github.com/BYUCamachoLab/ottoeplitz',
      author='Sarah Maia, Sarah Gonzalez',
      author_email='sarahcrismaia@gmail.com, sarahg.3545@gmail.com',
      license='MIT',
      packages=['toeplitz'],
      install_requires=[
          'numpy', 'scipy', 'matplotlib'],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)

#TODO: register package to PyPi