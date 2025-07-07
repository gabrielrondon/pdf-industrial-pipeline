"""
Script to check if judicial-analysis routes are registered
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute
import json

# Import the app
from main import app

def list_routes(app: FastAPI):
    """List all routes in the FastAPI app"""
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "description": route.description or route.summary or ""
            })
    return routes

# Get all routes
all_routes = list_routes(app)

# Filter judicial routes
judicial_routes = [r for r in all_routes if 'judicial' in r['path']]

print("=== Judicial Analysis Routes ===\n")
if judicial_routes:
    for route in judicial_routes:
        print(f"{', '.join(route['methods'])} {route['path']}")
        print(f"  Name: {route['name']}")
        if route['description']:
            print(f"  Description: {route['description'][:100]}...")
        print()
else:
    print("❌ No judicial analysis routes found!")
    print("\nAll available routes:")
    for route in sorted(all_routes, key=lambda x: x['path']):
        print(f"{', '.join(route['methods'])} {route['path']}")

print(f"\nTotal routes: {len(all_routes)}")
print(f"Judicial routes: {len(judicial_routes)}")