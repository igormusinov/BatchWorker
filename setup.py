import setuptools

setuptools.setup(
    name="BatchWorker",
    version="1.0.0",
    author="Igor Musinov && Dmitry Maevskiy",
    author_email="igor.musinov@phystech.edu",
    description="Small set of scripts for ACI, Kubernetes and Slurm run",
    scripts=['bin/run_job.py'],
    url="https://github.com/igormusinov/BatchWorker",
    package=setuptools.find_packages(),
    python_requires='>=3.0',
)
