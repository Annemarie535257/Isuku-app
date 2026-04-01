#!/usr/bin/env python
"""
Script to compile Django translation files (.po to .mo) without requiring gettext tools
"""
import os
import struct
from pathlib import Path

def compile_po_to_mo(po_file_path, mo_file_path):
    """Compile a .po file to .mo file format"""
    translations = {}
    current_msgid = None
    current_msgstr = None
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('msgid '):
                if current_msgid is not None and current_msgstr is not None:
                    translations[current_msgid] = current_msgstr
                current_msgid = line[6:].strip('"')
                current_msgstr = None
            elif line.startswith('msgstr '):
                current_msgstr = line[7:].strip('"')
            elif line.startswith('"') and current_msgid is not None:
                if current_msgstr is None:
                    # Continuation of msgid
                    current_msgid += line.strip('"')
                else:
                    # Continuation of msgstr
                    current_msgstr += line.strip('"')
        
        # Don't forget the last entry
        if current_msgid is not None and current_msgstr is not None:
            translations[current_msgid] = current_msgstr
    
    # Write .mo file (binary format)
    # .mo file format: Magic number, version, number of strings, etc.
    with open(mo_file_path, 'wb') as f:
        # Write magic number (0x950412de for big-endian, 0xde120495 for little-endian)
        f.write(struct.pack('<I', 0x950412de))
        
        # Write version (0)
        f.write(struct.pack('<I', 0))
        
        # Count non-empty translations
        valid_translations = {k: v for k, v in translations.items() if k and v}
        num_strings = len(valid_translations)
        
        # Write number of strings
        f.write(struct.pack('<I', num_strings))
        
        # Write offset of original string table
        f.write(struct.pack('<I', 28))  # Header is 28 bytes
        
        # Write offset of translation string table
        # Calculate size needed for original string table
        orig_table_size = num_strings * 8  # Each entry is 8 bytes (length + offset)
        f.write(struct.pack('<I', 28 + orig_table_size))
        
        # Write size of hash table (0 = no hash table)
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', 0))
        
        # Now write the string tables
        offset = 28 + (orig_table_size * 2)  # Start after both tables
        
        # Build lists of strings
        orig_strings = []
        trans_strings = []
        for msgid, msgstr in valid_translations.items():
            orig_strings.append((msgid, offset))
            offset += len(msgid.encode('utf-8')) + 1  # +1 for null terminator
            trans_strings.append((msgstr, offset))
            offset += len(msgstr.encode('utf-8')) + 1
        
        # Write original string table
        for msgid, msg_offset in orig_strings:
            msg_bytes = msgid.encode('utf-8')
            f.write(struct.pack('<I', len(msg_bytes)))
            f.write(struct.pack('<I', msg_offset))
        
        # Write translation string table
        for msgstr, msg_offset in trans_strings:
            msg_bytes = msgstr.encode('utf-8')
            f.write(struct.pack('<I', len(msg_bytes)))
            f.write(struct.pack('<I', msg_offset))
        
        # Write the actual strings
        for msgid, _ in orig_strings:
            f.write(msgid.encode('utf-8'))
            f.write(b'\x00')
        for msgstr, _ in trans_strings:
            f.write(msgstr.encode('utf-8'))
            f.write(b'\x00')

def main():
    """Compile all .po files in locale directory"""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    if not locale_dir.exists():
        print("Locale directory not found!")
        return
    
    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            lc_messages_dir = lang_dir / 'LC_MESSAGES'
            po_file = lc_messages_dir / 'django.po'
            mo_file = lc_messages_dir / 'django.mo'
            
            if po_file.exists():
                try:
                    compile_po_to_mo(po_file, mo_file)
                    print(f"Compiled {lang_dir.name}/LC_MESSAGES/django.mo")
                except Exception as e:
                    print(f"Error compiling {po_file}: {e}")
            else:
                print(f"No django.po file found in {lc_messages_dir}")

if __name__ == '__main__':
    main()

