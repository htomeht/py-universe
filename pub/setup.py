from distutils.core import setup
setup(name="PUB",
      description="Python Universe Builder",
      version="0.9",
      url="http://py-universe.sourceforge.net/",
      packages=["pub","pub.lang","pub.lang.englishLang"],
      package_dir={"pub": ""},
      maintainer="PUB team",
      maintainer_email="py-universe-main@lists.sourceforge.net",
      )
