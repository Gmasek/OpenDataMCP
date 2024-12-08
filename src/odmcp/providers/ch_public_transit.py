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
BASE_URL = "http://transport.opendata.ch/v1/connections?"

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
class Public_TransitParams(BaseModel):
    """Input parameters for the endpoint."""

    origin: str = Field(..., description="city to go from")
    to: str = Field(None, description="destination")


# class Coordinates(BaseModel):
#    type: str = Field(..., description="coordinate type")
#    x: float = Field(..., description="x coordinate")
#    y: float = Field(..., description="y coordinate")


class Location(BaseModel):
    id: str = Field(..., description="location id")
    name: str = Field(..., description="location name")
    # coordinates: Optional[Coordinates] = Field(..., description="location coordinates")


class Stop(BaseModel):
    station: Location = Field(..., description="station info of stop")
    arrival: Optional[str] = Field(None, description="arrival time")
    departure: Optional[str] = Field(None, description="departure time")
    delay: Optional[int] = Field(None, description="delay")


class Departure(BaseModel):
    station: Location = Field(..., description="station info")
    departure: str = Field(..., description="time of departure")
    platform: str = Field(..., description="platform")


class Arrival(BaseModel):
    station: Location = Field(..., description="station info")
    arrival: str = Field(..., description="time of arrival")
    platform: str = Field(..., description="platform")


class Route(BaseModel):
    name: str = Field(..., description="route name")
    category: str = Field(..., description="route category")
    number: str = Field(..., description="route number")
    operator: str = Field(..., description="route operator")
    to: str = Field(..., description="route destination")
    passList: List[Stop] = Field(..., description="list of stops")


class TransitOption(BaseModel):
    journey: Route = Field(..., description="route info")


class PublicTransitResult(BaseModel):
    """Single result item from the endpoint."""

    start: Departure = Field(alias="from", description="Starting station")
    to: Arrival = Field(alias="to", description="Destination station")
    duration: str = Field(..., description="Duration of the trip")
    transfers: int = Field(..., description="Number of transfers")
    sections: List[TransitOption] = Field(..., description="Tranit options")


class Public_TransitResponse(BaseModel):
    """Complete response from the endpoint."""

    connections: List[PublicTransitResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_transit_data(params: Public_TransitParams) -> Public_TransitResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: Public_TransitParams object containing all query parameters

    Returns:
        Public_TransitResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = f"{BASE_URL}from={params.origin}&to={params.to}"
    response = httpx.get(endpoint)
    response.raise_for_status()
    return Public_TransitResponse(**response.json())


# 3. Handler Function
async def handle_transitdata(
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
        response = fetch_transit_data(Public_TransitParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="transit_information",
        description="Description of what this endpoint does",
        inputSchema=Public_TransitParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["transit_information"] = handle_transitdata


###################
# [Another Endpoint Name]
###################
...

# Server initialization (if module is run directly)
if __name__ == "__main__":
    # import anyio     #
    # from odmcp.utils import run_server   #
    # anyio.run(
    #    run_server, "service.name", RESOURCES, RESOURCES_HANDLERS, TOOLS, TOOLS_HANDLERS
    # )
    print(fetch_transit_data(Public_TransitParams(origin="Zürich", to="Basel")))
