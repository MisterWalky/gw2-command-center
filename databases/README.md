# Databases

> Runtime folder – database files are generated automatically and not versioned.

This folder stores local SQLite databases used by the project.

## Purpose

The databases are used to:

- store Guild Wars 2 API data
- keep historical records
- support data analysis and reporting

## Notes

- Database files are **NOT versioned**
- Files are created automatically at runtime if missing
- It is safe to delete them (they will be recreated if needed)

## Typical files

- `GW2_API.db`
- `GW2_TEST.db`
