"""
Adversys Target Management Tool
Tool for managing targets in Adversys Core
"""
import json
from typing import Optional
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.tools.adversys_api_tool import AdversysAPI


class AdversysTargets(AdversysAPI):
    """Tool for managing Adversys targets"""
    
    async def execute(self, **kwargs) -> Response:
        """Execute target management operation"""
        operation = self.args.get("operation", "").lower()
        
        if operation == "create":
            return await self._create_target()
        elif operation == "list":
            return await self._list_targets()
        elif operation == "search":
            return await self._search_targets()
        elif operation == "get":
            return await self._get_target()
        elif operation == "update":
            return await self._update_target()
        elif operation == "delete":
            return await self._delete_target()
        else:
            return Response(
                message=f"Unknown operation: {operation}. Valid operations: create, list, search, get, update, delete",
                break_loop=False
            )
    
    async def _create_target(self) -> Response:
        """Create a new target"""
        name = self.args.get("name", "")
        target_type = self.args.get("type", "")
        value = self.args.get("value", "")
        description = self.args.get("description", "")
        
        if not name or not target_type or not value:
            return Response(
                message="Missing required parameters: name, type, and value are required",
                break_loop=False
            )
        
        # Support both single value and multiple values format
        values = self.args.get("values", "")
        if values:
            try:
                values_list = json.loads(values) if isinstance(values, str) else values
                target_data = {
                    "name": name,
                    "values": values_list,
                    "description": description
                }
            except:
                return Response(
                    message="Invalid 'values' parameter. Expected JSON array of {type, value} objects",
                    break_loop=False
                )
        else:
            target_data = {
                "name": name,
                "type": target_type,
                "value": value,
                "description": description
            }
        
        resp = self.api_client.post("/api/v1/targets/", json_data=target_data)
        return self._handle_api_response(resp, f"Target '{name}' created successfully")
    
    async def _list_targets(self) -> Response:
        """List all targets"""
        resp = self.api_client.get("/api/v1/targets/")

        try:
            resp.raise_for_status()
            targets = resp.json()

            if not targets:
                return Response(message="No targets found", break_loop=False)

            # Format targets list
            message = f"Found {len(targets)} target(s):\n\n"
            for target in targets:
                message += f"- {target.get('name', 'Unknown')} (ID: {target.get('id', 'N/A')})\n"
                message += f"  Type: {target.get('type', 'N/A')}, Value: {target.get('value', 'N/A')}\n"
                if target.get('description'):
                    message += f"  Description: {target.get('description')}\n"
                message += "\n"

            return Response(message=message.strip(), break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to list targets")

    async def _search_targets(self) -> Response:
        """Search for targets by value, name, or type"""
        query = self.args.get("query", "")
        search_type = self.args.get("type", "")
        search_name = self.args.get("name", "")

        if not query and not search_type and not search_name:
            return Response(
                message="Missing search parameters. Provide 'query' (value), 'type', or 'name' to search",
                break_loop=False
            )

        # Get all targets and filter client-side since API may not support search
        resp = self.api_client.get("/api/v1/targets/")

        try:
            resp.raise_for_status()
            all_targets = resp.json()

            # Filter targets based on search criteria
            matching_targets = []
            for target in all_targets:
                matches = True

                if query and query.lower() not in target.get('value', '').lower():
                    matches = False

                if search_type and search_type.lower() != target.get('type', '').lower():
                    matches = False

                if search_name and search_name.lower() not in target.get('name', '').lower():
                    matches = False

                if matches:
                    matching_targets.append(target)

            if not matching_targets:
                return Response(message=f"No targets found matching the search criteria", break_loop=False)

            # Format matching targets
            message = f"Found {len(matching_targets)} matching target(s):\n\n"
            for target in matching_targets:
                message += f"- {target.get('name', 'Unknown')} (ID: {target.get('id', 'N/A')})\n"
                message += f"  Type: {target.get('type', 'N/A')}, Value: {target.get('value', 'N/A')}\n"
                if target.get('description'):
                    message += f"  Description: {target.get('description')}\n"
                message += "\n"

            return Response(message=message.strip(), break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to search targets")
    
    async def _get_target(self) -> Response:
        """Get target details"""
        target_id = self.args.get("target_id", "")
        
        if not target_id:
            return Response(
                message="Missing required parameter: target_id",
                break_loop=False
            )
        
        resp = self.api_client.get(f"/api/v1/targets/{target_id}")
        return self._handle_api_response(resp, f"Target details retrieved")
    
    async def _update_target(self) -> Response:
        """Update a target"""
        target_id = self.args.get("target_id", "")
        
        if not target_id:
            return Response(
                message="Missing required parameter: target_id",
                break_loop=False
            )
        
        # Build update data from provided args
        update_data = {}
        if "name" in self.args:
            update_data["name"] = self.args["name"]
        if "description" in self.args:
            update_data["description"] = self.args["description"]
        if "type" in self.args and "value" in self.args:
            update_data["type"] = self.args["type"]
            update_data["value"] = self.args["value"]
        if "values" in self.args:
            try:
                values = self.args["values"]
                update_data["values"] = json.loads(values) if isinstance(values, str) else values
            except:
                return Response(
                    message="Invalid 'values' parameter. Expected JSON array",
                    break_loop=False
                )
        
        if not update_data:
            return Response(
                message="No update parameters provided",
                break_loop=False
            )
        
        resp = self.api_client.put(f"/api/v1/targets/{target_id}", json_data=update_data)
        return self._handle_api_response(resp, f"Target updated successfully")
    
    async def _delete_target(self) -> Response:
        """Delete a target"""
        target_id = self.args.get("target_id", "")
        
        if not target_id:
            return Response(
                message="Missing required parameter: target_id",
                break_loop=False
            )
        
        resp = self.api_client.delete(f"/api/v1/targets/{target_id}")
        
        try:
            resp.raise_for_status()
            return Response(message=f"Target {target_id} deleted successfully", break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to delete target")
