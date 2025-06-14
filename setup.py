"""Setup script for adk-samples."""

from setuptools import setup, find_packages

setup(
    name="adk-samples",
    version="0.1.0",
    description="Hands on Agent Development Kit(ADK)",
    packages=["agents", "common"],  # Explicitly list the top-level packages
    # Alternatively:
    # packages=find_packages(include=["agents*", "common*"], exclude=["tests*"]),
    python_requires=">=3.11",
)
