import os
import polib

# Compile Russian translations
ru_po_path = r'c:\Users\Farkhad\Desktop\deli-bike-admin-main\locale\ru\LC_MESSAGES\django.po'
ru_mo_path = r'c:\Users\Farkhad\Desktop\deli-bike-admin-main\locale\ru\LC_MESSAGES\django.mo'

try:
    po = polib.pofile(ru_po_path)
    po.save_as_mofile(ru_mo_path)
    print(f"✓ Russian translations compiled: {ru_mo_path}")
except Exception as e:
    print(f"✗ Error compiling Russian: {e}")

# Compile Kazakh translations
kk_po_path = r'c:\Users\Farkhad\Desktop\deli-bike-admin-main\locale\kk\LC_MESSAGES\django.po'
kk_mo_path = r'c:\Users\Farkhad\Desktop\deli-bike-admin-main\locale\kk\LC_MESSAGES\django.mo'

try:
    po = polib.pofile(kk_po_path)
    po.save_as_mofile(kk_mo_path)
    print(f"✓ Kazakh translations compiled: {kk_mo_path}")
except Exception as e:
    print(f"✗ Error compiling Kazakh: {e}")

print("\n✓ All translations compiled successfully!")
