from __future__ import annotations

import sys
import zipfile
from pathlib import Path

package=Path(sys.argv[1]); temporary=package.with_suffix(".tampered.zip")
with zipfile.ZipFile(package) as source, zipfile.ZipFile(temporary,"w",zipfile.ZIP_DEFLATED) as target:
    for name in source.namelist():
        value=source.read(name)
        target.writestr(name,value+b"tampered-after-signing" if name=="model.onnx" else value)
temporary.replace(package)
print(f"tampered signed package: {package}")
