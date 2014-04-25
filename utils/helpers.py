
import os
import os.path
import zipfile

import sublime


def find_all_packages(
    package_names=None,
    package_paths=None,
    include_folders=True,
    include_packages=True,
    contents=False,
    extensions=None
):

    if extensions is not None and not isinstance(extensions, list):
        extensions = [extensions]
    if package_names is not None and not isinstance(package_names, list):
        package_names = [package_names]
    if package_paths is not None and not isinstance(package_paths, list):
        package_paths = [package_paths]

    packages = {}
    for packages_path in [sublime.installed_packages_path(), sublime.packages_path()]:
        for package_name in os.listdir(packages_path):
            if package_names is not None and not package_name in package_names:
                continue
            package_path = os.path.join(packages_path, package_name)
            if package_paths is not None and not package_path in package_paths:
                continue
            if os.path.isdir(package_path) and include_folders:
                packages[package_name] = {
                    'type': 'folder',
                    'path': package_path,
                    'name': package_name,
                    'files': [],
                    'contents': {}
                }
                for item in os.listdir(package_path):
                    item_path = os.path.join(package_path, item)
                    if os.path.isfile(item_path):
                        packages[package_name]['files'].append(item)
                        if (
                            contents and
                            (
                                extensions is None or
                                os.path.splitext(item_path)[1] in extensions
                            )
                        ):
                            with open(item_path, 'r', encoding='utf8') as open_file:
                                packages[package_name]['contents'][item] = open_file.read()
            elif (
                zipfile.is_zipfile(package_path) and
                package_path.endswith('.sublime-package') and
                include_packages
            ):
                package_name = package_name[:-16]
                packages[package_name] = {
                    'type': 'folder',
                    'path': package_path,
                    'name': package_name,
                    'files': [],
                    'contents': {}
                }
                with zipfile.ZipFile(package_path) as package_file:
                    for item in package_file.namelist():
                        if item.replace('\\', '/').find('/') == -1:
                            packages[package_name]['files'].append(item)
                            if (
                                contents and
                                (
                                    extensions is None or
                                    os.path.splitext(item)[1] in extensions
                                )
                            ):
                                content = package_file.read(item).decode('utf8')
                                packages[package_name]['contents'][item] = content
    return packages
