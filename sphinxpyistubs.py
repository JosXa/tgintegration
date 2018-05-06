# in your extension
import os

from sphinx.ext.autodoc import importer

# keep original import_module()
original_import_module = importer.import_module


def import_module(modname, warningiserror=False):
    module = original_import_module(modname, warningiserror)
    if hasattr(module, '__file__') and os.path.isfile('{}i'.format(module.__file__)):
        # merge external spec into the imported module
        try:
            from importlib._bootstrap import spec_from_loader
            from importlib._bootstrap_external import SourceFileLoader
            from importlib._bootstrap import module_from_spec
            spec = spec_from_loader(modname,
                                    SourceFileLoader(modname, '{}i'.format(module.__file__)))
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
        except BaseException as e:
            raise e


# override import_module() by own
importer.import_module = import_module
