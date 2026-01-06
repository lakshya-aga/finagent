
from functions.install_packages import install_packages


print(install_packages(['some_invalid_package']))
print(install_packages(['pandas', 'numpy']))
