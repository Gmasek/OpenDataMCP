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
from typing import Any, List, Sequence

import httpx
import mcp.types as types
from pydantic import BaseModel, Field

# Initialize logging
log = logging.getLogger(__name__)

# 2. Constants Section
BASE_URL = "http://ich-tanke-strom.switzerlandnorth.cloudapp.azure.com:8080/geoserver/ich-tanke-strom/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ich-tanke-strom"

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
class ChargingStationParams(BaseModel):
    limit: int = Field(
        default=3,
    )
    # city: str = Field(default="&cql_filter=Address.City.value%20iis%20%Zurich")
    # test: str = Field(default="&cql_filter=IsOpen24Hours=true")
    test: str = Field(default="&cql_filter=RenewableEnergy=true")


class Geodata(BaseModel):
    type: str = Field(description="Feature type")
    coordinates: List[float] = Field(description="Feature coordinates")


class AdressProperties(BaseModel):
    PostalCode: str = Field(description="Postal Code")
    City: str = Field(description="City")
    Street: str = Field(description="Street")
    Country: str = Field(description="Country")


class CharingFacilites(BaseModel):
    Power: int = Field(description="Power")
    Voltage: int = Field(description="Voltage")
    PowerType: str = Field(description="Power Type")


class StationProperties(BaseModel):
    featureType: str = Field(alias="@featureType", description="Feature type")
    id: str = Field(alias="_id", description="Feature id")
    EvseStatus: str = Field(description="Evse Status")
    Plugs: str = Field(description="Plugs")
    AuthenticationModes: list[str] = Field(description="Authentication Modes")
    AccessibilityLocation: str = Field(description="Accessibility Location")
    Address: AdressProperties = Field(description="Adress")
    PaymentOptions: list[str] = Field(description="Payment Options")
    RenewableEnergy: bool = Field(description="Renewable Energy")
    ChargingFacilities: list[CharingFacilites] = Field(
        description="Charging Facilities"
    )


class CharingStationResult(BaseModel):
    type: str = Field(description="Feature type")
    id: str = Field(description="Feature id")
    geometry: Geodata = Field(description="Feature geometry")
    properties: StationProperties = Field(description="Feature properties")


class CharingStationResponse(BaseModel):
    type: str = Field(description="Feature type")
    features: List[CharingStationResult] = Field(description="List of features")


# 2. Data Fetching Function
def fetch_endpoint_data(params: ChargingStationParams) -> CharingStationResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = (
        f"{BASE_URL}%3Aevse&maxFeatures=10&outputFormat=application%2Fjson{params.test}"
    )
    response = httpx.get(
        endpoint,
    )

    response.raise_for_status()

    return CharingStationResponse(**response.json())


# 3. Handler Function
async def handle_query_charing_station(
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
        response = fetch_endpoint_data(ChargingStationParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="charging-stations",
        description="Description of what this endpoint does",
        inputSchema=ChargingStationParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["charging-stations"] = handle_query_charing_station


###################
# [Another Endpoint Name]
###################
...

# Server initialization (if module is run directly)
if __name__ == "__main__":
    print(fetch_endpoint_data(ChargingStationParams(select="", limit=10)))
