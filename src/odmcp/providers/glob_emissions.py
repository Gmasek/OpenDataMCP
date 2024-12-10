"""
Template for MCP server definitions.

This template provides a standardized structure for creating MCP server modules.
Each module should follow this pattern to ensure consistency across the codebase.

Module Structure:
1. Imports and Configuration
2. Global Constants
3. Registration Variables
4. Endpoint Sections (one per endpoint):
   - Pydantic Models (Input/Output)
   - Data Fetching Function
   - Handler Function
   - Tool Registration

Usage:
    Copy this template and replace the placeholders with actual implementation.
"""

# 1. Standard Imports Section
import logging
from typing import Any, List, Optional, Sequence

import httpx
import mcp.types as types
from pydantic import BaseModel, Field

# Initialize logging
log = logging.getLogger(__name__)

# 2. Constants Section
BASE_URL = (
    "https://www.climatewatchdata.org/api/v1/data/historical_emissions?regions=EUU&"
)

# 3. Registration Variables
RESOURCES: List[Any] = []  # resources that will be registered by each endpoints
RESOURCES_HANDLERS: dict[
    str, Any
] = {}  # resources handlers that will be registered by each endpoints
TOOLS: List[types.Tool] = []  # tools that will be registered by each endpoints
TOOLS_HANDLERS: dict[
    str, Any
] = {}  # tools handlers that will be registered by each endpoints

###################
# [Endpoint Name]
###################


# 1. Input/Output Models
class EndpointParams(BaseModel):
    """Input parameters for the endpoint."""

    # regions:Optional[str] = Field(None, description="region ISO code 3 (ISO Codes for World and European Union (27) are WORLD and EUU, respectively)")
    start_year: Optional[str] = Field(None, description="Description of param1")
    end_year: Optional[str] = Field(None, description="Description of param2")


class YearlyEmissions(BaseModel):
    year: int = Field(..., description="year")
    value: float = Field(..., description="emissions")


class EndpointResult(BaseModel):
    """Single result item from the endpoint."""

    id: int = Field(..., description="id of the country displayed")
    iso_code3: str = Field(..., description="iso code of country")
    country: str = Field(..., description="name of the country")
    data_source: str = Field(..., description="data source ")
    sector: str = Field(..., description="Sector of the emission source")
    gas: str = Field(..., description="gas ")
    unit: str = Field(..., description="unit of carbon emissions")
    emissions: List[YearlyEmissions] = Field(..., description="emissions")


class EndpointResponse(BaseModel):
    """Complete response from the endpoint."""

    data: List[EndpointResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_endpoint_data(params: EndpointParams) -> list[EndpointResponse]:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = f"{BASE_URL}"
    if params is not None:
        endpoint = f"{endpoint}&"
        if params.start_year:
            endpoint += f"start_year={params.start_year}&"
        if params.end_year:
            endpoint += f"end_year={params.end_year}&"
        endpoint = endpoint.rstrip("&")
    all_data = []
    while endpoint:
        response = httpx.get(endpoint)
        response.raise_for_status()
        data = response.json()

        # Extend all_data with EndpointResponse objects
        all_data.extend(EndpointResponse(**data))

        # Update the endpoint for the next page
        endpoint = data.get("next")
    print(len(all_data))
    return all_data


# 3. Handler Function
async def handle_endpoint(
    arguments: dict[str, Any] | None = None,
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle the tool execution for this endpoint.

    Args:
        arguments: Dictionary of tool arguments

    Returns:
        Sequence of content objects

    Raises:
        Exception: If the handling fails
    """
    try:
        response = fetch_endpoint_data(EndpointParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="endpoint-name",
        description="Description of what this endpoint does",
        inputSchema=EndpointParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["endpoint-name"] = handle_endpoint


###################
# [Another Endpoint Name]
###################
...

# Server initialization (if module is run directly)
if __name__ == "__main__":
    #   import anyio#
    #   from odmcp.utils import run_server#
    #   anyio.run(
    #       run_server, "service.name", RESOURCES, RESOURCES_HANDLERS, TOOLS, TOOLS_HANDLERS
    #   )
    print(fetch_endpoint_data(EndpointParams(start_year="2009", end_year="2010")))
