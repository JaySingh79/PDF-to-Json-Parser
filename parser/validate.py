def validate_formation_tops(rows):
    last_md = -1
    for r in rows:
        md = r["MD_ft"]
        tvd = r["TVD_ft"]
        if md <= last_md:
            return False
        if tvd > md:
            return False
        last_md = md
    return True
