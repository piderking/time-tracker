
# --- Define the Custom Update Function ---
def custom_modifier(doc):
    """
    Renames a field and merges a new list of roles into an existing list.
    The function MUST modify the passed 'doc' dictionary directly.
    """
    new_roles = ['admin', 'write']  # Roles to be merged

    # 1. Rename the field
    if 'legacy_id' in doc:
        doc['user_id'] = doc.pop('legacy_id')

    # 2. Merge the lists without duplicates
    if 'permissions' in doc and isinstance(doc['permissions'], list):
        current_permissions = set(doc['permissions'])
        current_permissions.update(new_roles)
        doc['permissions'] = list(current_permissions)

    # 3. Add a timestamp for audit purposes (optional)
    import time
    doc['last_modified'] = int(time.time())
