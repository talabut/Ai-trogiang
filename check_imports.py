import pkgutil
import importlib
import traceback

BASE_PACKAGE = "backend"

errors = []

for module in pkgutil.walk_packages([BASE_PACKAGE], BASE_PACKAGE + "."):
    name = module.name
    try:
        importlib.import_module(name)
    except Exception as e:
        errors.append((name, e))

print("\n====== IMPORT ERRORS ======")
for name, err in errors:
    print(f"\n❌ {name}")
    traceback.print_exception(type(err), err, err.__traceback__)

print(f"\nTotal errors: {len(errors)}")
