"""Setup script for adk-samples."""

from setuptools import setup, find_packages

setup(
    name="adk-samples",
    version="0.1.0",
    description="Hands on Agent Development Kit(ADK)",
    packages=["agents", "common"],  # Explicitly list the top-level packages
    python_requires=">=3.11",
)
